### EULA-SIGNOFF-1 (RUL-166) — nothing goes live without a signed EULA

David's own waiter-route test on the Quick door published live without him reading the EULA: the
one-tap publish (RUL-163 b) treated the tap as acceptance and stamped `eula_accepted_at` for any new
email. Now `/listings/quick-publish` publishes only for a signed-in member whose EULA is already
signed; everyone else gets a draft plus the way-back letter and signs the terms in the TrustSquare
app before publishing. The Quick door never records an acceptance. Guard: RG-0446.
