- **AIPROV-VERIFY-1 (21 Aug):** AI Providers card no longer paints a lane green on
  configuration alone. Amber = key present but never proven live; green = a real
  `/admin/ai-test` succeeded (decays 24h); red = last test failed. Test-button 401 now
  names itself as a dashboard-login expiry, not a provider fault. Ledger RG-0130 LOCKED.
  **Open for David:** `_apv3PendingFlip` is still hardcoded `true`, so the "flip pending
  preconditions" banner contradicts live flags (`active=openai, standing=openai`, key present).
