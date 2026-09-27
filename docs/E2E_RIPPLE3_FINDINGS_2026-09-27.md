# Ripple E2E walk 3 - 27 Sep 2026, 19:00-19:18 UTC (live trustsquare.co, phone width, fresh email identities)

PASSED end to end
- Ex1 Annatjie (new email identity qa-annatjie3): Quick (Email only, two areas) -> email link -> photo + Terms -> Publish (#428) -> Buzz link -> Sannie joined -> buzz delivered (email) -> employer reference confirmed by Sannie -> Karin "Join queue" (1T hold) -> Annatjie Accept -> Karin's 1T burnt.
- Ex2 Marietjie (qa-honey): Quick honey -> email link -> Publish (#430) -> Buzz link -> Karin joined (already signed in) -> Karin's Local Market request landed (no refusal) -> Accept -> seller paid 1T (lm_intro_deduct).
- Ex3 Jacques: My reports lists 4 paid reports; reopening one offers "Attach report to my listing"; Karin sees "Seller attached an AI market report" on the Krugerrand (#429).

OPEN (owner: whichever lane holds ms.js / bea_main.py / quick.html next)
1. NAMES: nobody is asked for a name. Buzz from_name, the join page, the Buzz link message and the buyer's prefilled name all read "dmcontiki2+qa-annatjie3" (the email's local part). Ask a first name in Quick's email pane and on join.html/confirm.html when the account has none.
2. HIDDEN CASUAL: a new home cleaner is invisible to strangers until one employer confirms or her ID is checked (RUL-115 STRANGER-GATE-1) - #428 was 404 to Karin until Sannie confirmed - and nothing tells her. The employer link is still the 5th trust-coach card. Put a Seller Hub card on a hidden casual listing: "Only people you send your link to can see this until someone you worked for confirms you" + the link button.
3. FAIR PRICE on Collectors / Local Market: /listings/{id}/value-tiers returns ready:false (server tier_resolvers.py predates FAIR-PRICE-LM-1; the ripple2b lane is adding it to deploy_manifest). Local Market also needs EBAY_APP_ID/EBAY_CERT_ID - neither is set.
4. AI Features cards still carry a "PRO" badge although every signed-in customer may run them (RUL-188).
5. After a Local Market Accept the Seller Hub still shows the old Tuppence balance (4 instead of 3) until reload.
6. Attached report shows name + date but no market range for the Krugerrand.
