/**
 * UPTIME-EXTERNAL-1 — TrustSquare's outside-the-fence outage watcher.
 * Decided and written 22 Aug 2026 (pre-soft-launch third-party sweep, RUL-037: the
 * technical decision is Claude's against the specs; OPEN_LOOPS L8 had been sitting on
 * "David names a vendor" since 14 Aug).
 *
 * WHY A CLOUDFLARE WORKER AND NOT A MONITORING VENDOR
 *   - No new vendor: Cloudflare already carries DNS, CDN, R2 and the inbound email worker.
 *   - No new money: cron triggers + 100k requests/day are on the free plan. The fixed-cost
 *     pricing rule (1 Aug) bars unbudgetable external costs; this one is zero and capped.
 *   - Right vantage: every other instrument we own runs ON the box it watches or on David's
 *     PC. A dead box or a closed laptop is a blind day BY CONSTRUCTION. This runs on
 *     Cloudflare's edge and owes nothing to either.
 *
 * WHAT IT DOES
 *   every 5 min : GET /health, expect 200 + {"status":"ok"}
 *   2 strikes   : email DOWN (one alert, then at most one repeat every 30 min)
 *   recovery    : email UP once, with the outage duration
 *   daily 06:00 : email HEARTBEAT — because a monitor that has silently died reads exactly
 *                 like a site that is fine. Silence must mean something.
 *
 * STATE lives in Workers KV (binding UPTIME_STATE). If the binding is missing the worker
 * still probes and still alerts; it just cannot suppress repeats. It never fails silently.
 */

const DEFAULTS = {
  TARGET_URL: "https://trustsquare.co/health",
  EXPECT_JSON_STATUS: "ok",
  FAILS_BEFORE_ALERT: "2",
  REPEAT_ALERT_MINUTES: "30",
  HEARTBEAT_UTC_HOUR: "6",
  ALERT_TO: "dmcontiki2@gmail.com",
  ALERT_FROM: "TrustSquare Uptime <hello@mail.trustsquare.co>",
  PROBE_TIMEOUT_MS: "10000",
};

const cfg = (env, k) => (env && env[k]) || DEFAULTS[k];

async function readState(env) {
  const blank = { consecutiveFails: 0, down: false, downSince: null, lastAlertAt: null, lastHeartbeatDay: null };
  if (!env.UPTIME_STATE) return { ...blank, _nokv: true };
  try {
    const raw = await env.UPTIME_STATE.get("state");
    return raw ? { ...blank, ...JSON.parse(raw) } : blank;
  } catch (e) {
    return { ...blank, _nokv: true };
  }
}

async function writeState(env, state) {
  if (!env.UPTIME_STATE) return;
  try {
    const { _nokv, ...clean } = state;
    await env.UPTIME_STATE.put("state", JSON.stringify(clean));
  } catch (e) { /* a KV write failure must never swallow an alert */ }
}

async function probe(env) {
  const url = cfg(env, "TARGET_URL");
  const started = Date.now();
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), parseInt(cfg(env, "PROBE_TIMEOUT_MS"), 10));
  try {
    const r = await fetch(url, {
      signal: ctl.signal,
      headers: { "User-Agent": "trustsquare-uptime-watcher/1.0" },
      cf: { cacheTtl: 0, cacheEverything: false },
    });
    const ms = Date.now() - started;
    if (r.status !== 200) return { ok: false, ms, reason: `HTTP ${r.status}` };
    const body = await r.text();
    let want = cfg(env, "EXPECT_JSON_STATUS");
    if (want) {
      let got = null;
      try { got = JSON.parse(body).status; } catch (e) { /* not JSON */ }
      if (got !== want) {
        return { ok: false, ms, reason: `200 but status=${JSON.stringify(got)} (wanted "${want}") — the process answers, the app does not` };
      }
    }
    return { ok: true, ms, reason: `200 in ${ms}ms` };
  } catch (e) {
    return { ok: false, ms: Date.now() - started, reason: `unreachable: ${e && e.name === "AbortError" ? "timeout" : String(e).slice(0, 120)}` };
  } finally {
    clearTimeout(timer);
  }
}

async function sendMail(env, subject, lines) {
  const key = env.RESEND_API_KEY;
  if (!key) return { sent: false, why: "RESEND_API_KEY not bound" };
  const html =
    `<div style="font-family:Inter,Arial,sans-serif;max-width:560px">` +
    `<h2 style="color:#0c1a2e;margin:0 0 10px">${subject}</h2>` +
    lines.map((l) => `<p style="margin:4px 0">${l}</p>`).join("") +
    `<p style="margin-top:16px;color:#667;font-size:12px">TrustSquare uptime watcher · Cloudflare edge · ` +
    `independent of the app server and of any desktop.</p></div>`;
  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: cfg(env, "ALERT_FROM"), to: [cfg(env, "ALERT_TO")], subject, html }),
    });
    let id = "", errText = "";
    try {
      const j = await r.json();
      if (j && j.id) id = String(j.id);
      else if (j && j.message) errText = String(j.message).slice(0, 160);
    } catch (e) { /* body not JSON — status alone decides */ }
    return { sent: r.ok, id, why: r.ok ? "" : `Resend HTTP ${r.status}${errText ? " — " + errText : ""}` };
  } catch (e) {
    return { sent: false, id: "", why: String(e).slice(0, 120) };
  }
}

// ── ALERT INGEST — POST /alert (ALERT-OFFORIGIN-1, 5 Sep 2026, DW-097) ──────
//
// WHY THIS EXISTS. The daily watch's RED alert used to be one SSH command to the
// origin: parse RESEND_API_KEY out of /etc/marketsquare/resend.watch.conf, then curl
// Resend from the box. That makes the alarm share a transport with the whole class of
// failure it exists to report. Observed twice in anger (DW-073 26 Aug, DW-097 5 Sep):
// the origin was unreachable, so the verdict was RED and the email could not be sent —
// David learned of it only by reading a report hours later.
//
// This Worker already owns everything the alarm needs and owes the origin nothing: its
// own Resend key (bound as a Worker secret, delivery proven end-to-end 29 Aug), its own
// egress at Cloudflare's edge, its own schedule. It was missing only a way to be ASKED.
//
// SAFETY, because this is a public URL that can send mail:
//   - bearer key (ALERT_INGEST_KEY), its own secret, useless for anything else;
//   - the RECIPIENT IS NEVER TAKEN FROM THE REQUEST — it is ALERT_TO, fixed in config,
//     so a leaked key can wake David but can never mail anyone else;
//   - subject and body are escaped and length-capped; the caller supplies a reason, not markup;
//   - a KV rate limit (12/hour) caps inbox and quota damage from a leaked key or a loop;
//   - dry:true authenticates and validates but sends NOTHING, so the regression ledger can
//     probe this whole path on every run for free, which is what stops it rotting unseen.
const ALERT_MAX_PER_HOUR = 12;

const esc = (s) => String(s == null ? "" : s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;").replace(/'/g, "&#39;");

// Length-equalised compare: never let response time leak how much of the key matched.
function keyMatches(given, want) {
  if (typeof given !== "string" || typeof want !== "string" || !want) return false;
  if (given.length !== want.length) return false;
  let diff = 0;
  for (let i = 0; i < want.length; i++) diff |= given.charCodeAt(i) ^ want.charCodeAt(i);
  return diff === 0;
}

async function rateLimit(env, now) {
  // Fails OPEN by design: if KV is unavailable the alert still goes. A rate limiter that
  // can silence an outage alarm is worse than the abuse it prevents.
  if (!env.UPTIME_STATE) return { allowed: true, note: "no KV — rate limit not enforced" };
  const hour = new Date(now).toISOString().slice(0, 13);
  const k = "alertcount:" + hour;
  try {
    const n = parseInt((await env.UPTIME_STATE.get(k)) || "0", 10) + 1;
    await env.UPTIME_STATE.put(k, String(n), { expirationTtl: 7200 });
    return n > ALERT_MAX_PER_HOUR
      ? { allowed: false, note: `rate limit: ${ALERT_MAX_PER_HOUR}/hour already sent this hour` }
      : { allowed: true, note: `${n}/${ALERT_MAX_PER_HOUR} this hour` };
  } catch (e) {
    return { allowed: true, note: "KV error — rate limit not enforced" };
  }
}

const jsonRes = (obj, status) => new Response(JSON.stringify(obj, null, 2), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
});

async function handleAlert(request, env, now) {
  const want = env.ALERT_INGEST_KEY;
  if (!want) {
    // Loud, never silent: a caller must be able to tell "refused" from "not wired up".
    return jsonRes({ ok: false, why: "ALERT_INGEST_KEY not bound on this Worker" }, 503);
  }
  const auth = request.headers.get("authorization") || "";
  const given = auth.startsWith("Bearer ") ? auth.slice(7).trim() : "";
  if (!keyMatches(given, want)) return jsonRes({ ok: false, why: "unauthorized" }, 401);

  let body;
  try {
    const raw = await request.text();
    if (raw.length > 16000) return jsonRes({ ok: false, why: "body too large" }, 413);
    body = JSON.parse(raw || "{}");
  } catch (e) {
    return jsonRes({ ok: false, why: "body must be JSON" }, 400);
  }

  const level = ["RED", "AMBER", "TEST"].includes(String(body.level || "").toUpperCase())
    ? String(body.level).toUpperCase() : "RED";
  const reason = String(body.reason || "unspecified").slice(0, 160);
  const lines = Array.isArray(body.lines) ? body.lines.slice(0, 30).map((l) => String(l).slice(0, 500)) : [];
  const to = cfg(env, "ALERT_TO");                    // fixed in config — NEVER from the request
  const subject = `WATCH ${level}: ${reason}`;
  const stamp = new Date(now).toISOString().replace("T", " ").slice(0, 19) + " UTC";

  if (body.dry === true) {
    // Authenticated and validated, sends nothing. The ledger's every-run probe.
    return jsonRes({
      ok: true, dry: true, would_send: true, to, subject,
      resend_key_bound: !!env.RESEND_API_KEY, kv: !!env.UPTIME_STATE, at: stamp,
    }, 200);
  }

  const rl = await rateLimit(env, now);
  if (!rl.allowed) return jsonRes({ ok: false, why: rl.note }, 429);

  const m = await sendMail(env, subject, [
    `<b>${esc(reason)}</b>`,
    ...lines.map((l) => esc(l)),
    `Raised at ${stamp} by the TrustSquare watch.`,
    `<b>This alert did not touch the origin server.</b> It was sent from Cloudflare's edge, ` +
    `so it still arrives when 178.104.73.239 is unreachable — which is exactly when it matters (DW-097).`,
  ]);
  return jsonRes(
    { ok: m.sent, sent: m.sent, id: m.id || "", why: m.why || "", to, subject, at: stamp, rate: rl.note },
    m.sent ? 200 : 502,
  );
}

const mins = (a, b) => Math.round((a - b) / 60000);

async function runCheck(env, now) {
  const state = await readState(env);
  const res = await probe(env);
  const strikes = parseInt(cfg(env, "FAILS_BEFORE_ALERT"), 10);
  const repeatAfter = parseInt(cfg(env, "REPEAT_ALERT_MINUTES"), 10);
  const stamp = new Date(now).toISOString().replace("T", " ").slice(0, 19) + " UTC";
  const actions = [];

  if (res.ok) {
    if (state.down) {
      const downFor = state.downSince ? mins(now, Date.parse(state.downSince)) : null;
      const m = await sendMail(env, "TrustSquare is BACK UP", [
        `<b>Recovered</b> at ${stamp}.`,
        downFor != null ? `It was down for about <b>${downFor} minute(s)</b>.` : "",
        `Probe: ${cfg(env, "TARGET_URL")} — ${res.reason}.`,
      ].filter(Boolean));
      actions.push(`recovery mail ${m.sent ? "sent" : "FAILED: " + m.why}`);
    }
    state.consecutiveFails = 0;
    state.down = false;
    state.downSince = null;
    state.lastAlertAt = null;
  } else {
    state.consecutiveFails = (state.consecutiveFails || 0) + 1;
    const due =
      state.consecutiveFails >= strikes &&
      (!state.lastAlertAt || mins(now, Date.parse(state.lastAlertAt)) >= repeatAfter);
    if (state.consecutiveFails >= strikes && !state.down) {
      state.down = true;
      state.downSince = new Date(now).toISOString();
    }
    if (due) {
      const m = await sendMail(env, "TrustSquare is DOWN", [
        `<b>${state.consecutiveFails} consecutive failed check(s)</b> as at ${stamp}.`,
        `Probe: ${cfg(env, "TARGET_URL")}`,
        `Reason: <b>${res.reason}</b>`,
        state.downSince ? `First failure at ${state.downSince.replace("T", " ").slice(0, 19)} UTC.` : "",
        `This watcher runs on Cloudflare's edge, so the server being unreachable does not stop the alert.`,
      ].filter(Boolean));
      state.lastAlertAt = new Date(now).toISOString();
      actions.push(`down mail ${m.sent ? "sent" : "FAILED: " + m.why}`);
    }
  }

  // HEARTBEAT — proof of life for the watcher itself. Without it, "no email" is ambiguous
  // between "all well" and "the monitor died three weeks ago".
  const d = new Date(now);
  const day = d.toISOString().slice(0, 10);
  if (d.getUTCHours() >= parseInt(cfg(env, "HEARTBEAT_UTC_HOUR"), 10) && state.lastHeartbeatDay !== day) {
    state.lastHeartbeatDay = day;
    const m = await sendMail(env, "TrustSquare uptime watcher — daily heartbeat", [
      `The external watcher is alive and checking every 5 minutes.`,
      `Latest probe: <b>${res.ok ? "UP" : "DOWN"}</b> — ${res.reason}.`,
      `Target: ${cfg(env, "TARGET_URL")}`,
      state._nokv ? `<b>Note:</b> KV is not bound, so repeat-suppression is off.` : "",
    ].filter(Boolean));
    actions.push(`heartbeat mail ${m.sent ? "sent" : "FAILED: " + m.why}`);
  }

  await writeState(env, state);
  return { at: stamp, ok: res.ok, reason: res.reason, ms: res.ms, consecutiveFails: state.consecutiveFails, down: state.down, actions, kv: !state._nokv };
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runCheck(env, Date.now()));
  },
  // Manual vantage: `curl https://<worker>.workers.dev/` runs one check and shows the state.
  // Useful for proving the watcher works without waiting for an outage.
  async fetch(request, env) {
    const url = new URL(request.url);
    // POST /alert — the off-origin alarm trigger (DW-097). Everything else keeps the
    // original behaviour: GET / runs one check, which is the liveness probe RG-0138 reads.
    if (url.pathname === "/alert") {
      if (request.method !== "POST") {
        return jsonRes({ ok: false, why: "POST only" }, 405);
      }
      return handleAlert(request, env, Date.now());
    }
    const out = await runCheck(env, Date.now());
    return new Response(JSON.stringify(out, null, 2), {
      headers: { "content-type": "application/json; charset=utf-8" },
    });
  },
};
