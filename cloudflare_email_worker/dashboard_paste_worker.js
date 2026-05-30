/**
 * TrustSquare — Inbound Email Worker (DASHBOARD PASTE VERSION v2 · Session 94)
 * ------------------------------------------------------------------
 * Uses postal-mime (imported from npm — the dashboard editor bundles it
 * automatically). Reliably extracts subject, from, and the text body, then
 * forwards a compact JSON payload to the BEA triage endpoint.
 *
 * Variables (Settings → Variables and Secrets):
 *   BEA_INBOUND_URL       (plain text) = https://trustsquare.co/email/inbound
 *   EMAIL_INBOUND_SECRET  (secret)     = the Session 94 shared secret
 *
 * The worker never replies itself — BEA owns reply logic. It also forwards a
 * copy to the human inbox so triage augments delivery, never replaces it.
 */

import PostalMime from "postal-mime";

export default {
  async email(message, env, ctx) {
    // Envelope addresses (fallbacks).
    let from = message.from || "";
    let to = message.to || "";
    let subject = "";
    let body = "";
    let messageId = null;

    try {
      const parsed = await PostalMime.parse(message.raw);
      from = (parsed.from && parsed.from.address) ? parsed.from.address : from;
      subject = parsed.subject || "";
      body = (parsed.text || parsed.html || "").toString();
      messageId = parsed.messageId || null;
    } catch (err) {
      // Fall back to header read if parsing fails — never drop the message.
      try { subject = message.headers.get("subject") || ""; } catch (e) {}
      body = `[worker could not parse body: ${err}]`;
    }

    const payload = {
      from_addr: from,
      to_addr: to,
      subject: subject,
      body: body.slice(0, 20000),
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
      if (!resp.ok) console.log(`BEA triage returned ${resp.status} for ${from}`);
    } catch (err) {
      console.log(`Failed to reach BEA triage: ${err}`);
    }

    // Safety net: also deliver a copy to the human inbox.
    try {
      await message.forward("dmcontiki2@gmail.com");
    } catch (err) {
      console.log(`Forward to inbox failed: ${err}`);
    }
  },
};
