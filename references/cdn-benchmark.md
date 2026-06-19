# CDN Edge Cache Benchmark

Staging load test comparing cached vs. uncached edge responses over 10k requests.

- Median TTFB, uncached: 410ms
- Median TTFB, cached: 238ms (-42%)
- Cache hit ratio: 91% after 5 minute warmup
- p99 TTFB improved less (-18%), dominated by cold-cache misses on long-tail URLs

Methodology: synthetic GET-heavy traffic generated with k6, mirroring production path
distribution from the last 30 days of access logs.
