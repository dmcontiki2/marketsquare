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
    let hasAttachments = false;
    try {
      const parser = new PostalMime();
      const raw = new Response(message.raw);
      const buf = await raw.arrayBuffer();
      const parsed = await parser.parse(buf);
      body = (parsed.text || parsed.html || "").toString();
      hasAttachments = !!(parsed.attachments && parsed.attachments.length);
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
      has_attachments: hasAttachments,
    };

    let triaged = false;
    try {
      const resp = await fetch(env.BEA_INBOUND_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Inbound-Secret": env.EMAIL_INBOUND_SECRET,
        },
        body: JSON.stringify(payload),
      });
      triaged = resp.ok;
      if (!resp.ok) {
        console.log(`BEA triage returned ${resp.status} for ${from}`);
      }
    } catch (err) {
      // Never throw — a thrown worker bounces the mail. Log and move on.
      console.log(`Failed to reach BEA triage: ${err}`);
    }

    // ONE-INBOX-1 (24 Aug 2026, David: user emails must not route to my personal
    // inbox). Routine customer mail lives in BEA triage — the support pipeline.
    // The personal forward is a DEAD-LETTER lane only: it fires when triage was
    // NOT reached, so no message can ever be lost, but the personal inbox stops
    // being the router. E2E-proven before this change: triage classifies, refs
    // and auto-replies from support@mail.trustsquare.co within seconds.
    // Attachments are WORKING DOCUMENTS (wave lane 1: "reply with your stock
    // list -- we do it for you"): triage only carries a 20KB text body, so a
    // mail bearing attachments must still reach a human mailbox or the
    // concierge lane starves. Routine attachment-free mail stays pipeline-only.
    // EMAIL-FIREWALL-1 (RUL-069, 30 Aug 2026): after launch the personal inbox is
    // sealed off from customer mail entirely. Armed by env.CUSTOMER_FIREWALL="1"
    // (wrangler var, David's flip at launch):
    //  - attachment mail no longer routes to the personal inbox; the triage payload
    //    carries has_attachments so the pipeline owns the concierge follow-up;
    //  - if triage is unreachable, reject at SMTP time so the sender's own server
    //    tells them delivery failed -- a bounce is honest, silent loss is not, and
    //    the worker has no storage to hold mail. Escalation to David happens in the
    //    admin surfaces (/admin/email-triage, fault queue, escalation brief), never
    //    by forwarding a customer's email to a personal mailbox.
    // Pre-launch (flag unset) the ONE-INBOX-1 dead-letter behaviour is unchanged.
    if (env.CUSTOMER_FIREWALL === "1") {
      if (!triaged) {
        console.log(`FIREWALL: triage unreachable, rejecting mail from ${from}`);
        message.setReject("TrustSquare support intake is temporarily unavailable; please retry shortly or use the in-app support channel.");
      }
      return;
    }
    if (!triaged || hasAttachments) {
      try {
        await message.forward("dmcontiki2@gmail.com");
      } catch (err) {
        console.log(`Dead-letter forward failed: ${err}`);
      }
    }
  },
};
