#!/bin/bash
# SEC-GATE-1 (24 Sep 2026): the BEA (uvicorn :8000) and the orchestration strategist (:5001) listen on
# 0.0.0.0 with the host firewall inactive, so they could be reached directly, around nginx (Basic Auth
# realms, X-Real-IP) and around Cloudflare. nginx proxies to 127.0.0.1, AdvertAgent/CityLauncher/the
# maintenance agent call 127.0.0.1, containers call from the docker bridge - nothing legitimate needs
# these ports from outside. Idempotent; SSH/80/443 are never touched (no lockout path).
set -e
iptables -N TS_PORTGUARD 2>/dev/null || true
iptables -F TS_PORTGUARD
iptables -A TS_PORTGUARD -s 127.0.0.0/8 -j RETURN
iptables -A TS_PORTGUARD -s 172.16.0.0/12 -j RETURN
iptables -A TS_PORTGUARD -s 178.104.73.239/32 -j RETURN
iptables -A TS_PORTGUARD -j DROP
iptables -C INPUT -p tcp -m multiport --dports 8000,5001 -j TS_PORTGUARD 2>/dev/null \
  || iptables -I INPUT -p tcp -m multiport --dports 8000,5001 -j TS_PORTGUARD
echo "portguard: 8000,5001 closed to the internet (loopback, docker bridge and self allowed)"
