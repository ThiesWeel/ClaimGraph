Cached edge responses cut median TTFB by ~42% in staging (410ms -> 238ms), with a 91% cache
hit ratio after warmup. p99 improved less (-18%), driven by cold-cache misses on long-tail URLs.
