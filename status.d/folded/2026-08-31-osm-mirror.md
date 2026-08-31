- **OSM-MIRROR-1 + RG-0231 (launch eve):** the RUL-083 resume at pool=10 tripped
  overpass-api.de's IP protection (probed: 200 pre-burst, connection-refused after; DDG/Bing
  fine). Fixed at class level: OVERPASS_URL env-driven in ALL SIX overpass callers (the first
  patch changed nothing — scraper_worker._run_osm had its own hardcoded copy, and the new
  RG-0231 tripwire then caught four more), server .env → overpass.openstreetmap.fr
  (planet-verified), OSM_CONCURRENCY 10→2. Engine active; queue jobs sit in backoff from the
  failed pass and retry via the mirror on their own schedule. Staging rate = morning
  measurement, not tonight's promise.
