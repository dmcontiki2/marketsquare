### Board after SEC-GATE-1 went live (read 24 Sep 2026 ~09:10Z, by the screen-walk session)

Six entries red, all HTTP 401 on reads the new gate now closes to non-admins: RG-0118 (inbound rail
status), RG-0203 (/dashboard/ai-funds), RG-0293 + RG-0315 + RG-0402 (/onboard/funnel -- now admin +
local), RG-0388 (/trust/employer-link now answers 401 where the entry expects 404); RG-0372 blind (401
on /users/{email}/trust). PROBED: the public funnel beacon POST /onboard/step still answers 200, and
the screen walk (all five languages) reads OK on the gated build. These are the ledger's probes
following the new policy -- the SEC-GATE-1 lane's follow-through (it holds the work lock); not
touched here so two sessions do not rewrite the same probes.
