/**
 * TrustSquare Introduction Relay — Cloudflare Email Worker (INTRO-RELAY-1, 5 Aug 2026)
 *
 * WHAT IT DOES
 *   Catches mail addressed to intro-*@relay.trustsquare.co and hands it to the BEA
 *   (POST /intro/relay), which forwards it to the hidden counterparty. The real
 *   addresses never appear here beyond the sender's own (which the sender obviously
 *   knows) — the mapping lives only in the TrustSquare database.
 *
 * SETUP (Cloudflare dashboard — David's console step)
 *   1. Email > Email Routing on the trustsquare.co zone: enable routing for the
 *      relay.trustsquare.co subdomain (add the MX + TXT records Cloudflare shows).
 *   2. Workers > create worker "intro-relay" with this code.
 *   3. Email Routing > Routing rules: Catch-all on relay.trustsquare.co → Action:
 *      "Send to Worker" → intro-relay.  (Or a rule matching intro-*@ if preferred.)
 *   4. Worker > Settings > Variables: add secret RELAY_INBOUND_SECRET with the SAME
 *      value as the server .env's RELAY_INBOUND_SECRET.
 *   5. Resend: verify the relay.trustsquare.co subdomain (SPF/DKIM records) so the
 *      BEA may send From: intro-...@relay.trustsquare.co without landing in spam.
 *
 * The BEA endpoint enforces everything that matters (enrolled-parties-only, expiry,
 * size caps); this worker only parses and delivers. It fails CLOSED: any error → the
 * message is rejected, never silently dropped into a void.
 */

const BEA = "https://trustsquare.co/intro/relay";
const MAX_BODY = 100000; // keep in step with _RELAY_MAX_BODY server-side

export default {
  async email(message, env, ctx) {
    try {
      const toAlias = (message.to || "").toLowerCase();
      if (!toAlias.startsWith("intro-")) {
        message.setReject("Unknown recipient");
        return;
      }

      // Raw MIME → naive text extraction (v1: text only; attachments are dropped
      // server-side policy — the BEA caps and sanitises again regardless).
      const raw = await new Response(message.raw).text();
      let body = raw;
      // crude but safe: prefer the text/plain part when MIME-multipart
      const m = raw.match(/Content-Type:\s*text\/plain[\s\S]*?\r?\n\r?\n([\s\S]*?)(?:\r?\n--|$)/i);
      if (m) body = m[1];
      if (body.length > MAX_BODY) body = body.slice(0, MAX_BODY);

      const payload = {
        to_alias: toAlias,
        from_addr: message.from || "",
        subject: message.headers.get("subject") || "",
        body: body,
      };

      const r = await fetch(BEA, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Relay-Secret": env.RELAY_INBOUND_SECRET || "",
        },
        body: JSON.stringify(payload),
      });

      if (!r.ok) {
        // 404 = channel closed/expired · 403 = not an enrolled party · other = fault.
        // Reject so the sender gets an honest bounce instead of silence.
        message.setReject("This introduction channel is not available");
      }
    } catch (e) {
      message.setReject("Relay temporarily unavailable");
    }
  },
};
