- **RESTART-REDFLASH-1 fixed and locked (RG-0318).** The ops map flashing all-red was a
  one-second deploy restart (23:24:56 and 23:29:16 UTC, 6 Sep), not an outage — server probed
  healthy throughout, `NRestarts=0`, zero journal errors. Every polled dashboard feed now retries
  once at 2.5s before a chip is called offline; 401/403/404 still go red immediately.
