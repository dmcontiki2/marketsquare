/**
 * TrustSquare — Inbound Email Worker  (Session 94)
 * ------------------------------------------------------------------
 * Cloudflare Email Worker. Cloudflare Email Routing delivers inbound
 * mail for the catch-all / configured @trustsquare.co addresses to this
 * worker. The worker parses the message and POSTs a compact JSON payload
 * to the BEA triage endpoint, which classifies it with Claude and either
 * drafts or (if enabled) auto-replies.
 *
 * Secrets (set via `wrangler secret put`):
 *   BEA_INBOUND_URL      e.g. https://trustsquare.co/email/inbound
 *   EMAIL_INBOUND_SECRET must match EMAIL_INBOUND_SECRET in the server's
 *                        /etc/environment (BEA reads it from there).
 *
 * Safety: the worker NEVER sends a reply itself. It only forwards to BEA.
 * BEA owns all reply logic and its conservative auto-send gate.
 *
 * Parsing: uses postal-mime (add with `npm i postal-mime`). If parsing
 * fails for any reason the worker still forwards the raw headers so no
 * message is silently dropped.
 */

import PostalMime from "postal-mime";

export default {
  async email(message, env, ctx) {
    const from = message.from || "";
    const to = (message.to && message.to.length) ? message.to : "";
    const subject = message.headers.get("subject") || "";
    const messageId = message.headers.get("message-id") || null;

    let body = "";
    try {
      const parser = new PostalMime();
      const raw = new Response(message.raw);
      const buf = await raw.arrayBuffer();
      const parsed = await parser.parse(buf);
      body = (parsed.text || parsed.html || "").toString();
    } catch (err) {
      // Parsing failed — forward what we have so the message is not lost.
      body = `[worker could not parse body: ${err}]`;
    }

    const payload = {
      from_addr: from,
      to_addr: to,
      subject: subject,
      body: body.slice(0, 20000), // cap; BEA trims further before the model
      message_id: messageId,
    };

    try {
      const resp = await fetch(env.BEA_INBOUND_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Inbound-Secret": env.EMAIL_INBOUND_SECRET,
        },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) {
        console.log(`BEA triage returned ${resp.status} for ${from}`);
      }
    } catch (err) {
      // Never throw — a thrown worker bounces the mail. Log and move on.
      console.log(`Failed to reach BEA triage: ${err}`);
    }

    // Always forward a copy to the human inbox as a safety net, so triage
    // augments rather than replaces normal delivery. Remove this line once
    // you trust auto-triage fully.
    try {
      await message.forward("dmcontiki2@gmail.com");
    } catch (err) {
      console.log(`Forward to inbox failed: ${err}`);
    }
  },
};
