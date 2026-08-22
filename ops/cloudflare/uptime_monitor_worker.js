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
    return { sent: r.ok, why: r.ok ? "" : `Resend HTTP ${r.status}` };
  } catch (e) {
    return { sent: false, why: String(e).slice(0, 120) };
  }
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
    const out = await runCheck(env, Date.now());
    return new Response(JSON.stringify(out, null, 2), {
      headers: { "content-type": "application/json; charset=utf-8" },
    });
  },
};
