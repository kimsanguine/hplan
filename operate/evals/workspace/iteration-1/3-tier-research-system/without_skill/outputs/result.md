I've designed a 6-file Python system using the Prometheus-Atlas-Worker pattern:

- **Prometheus** breaks a research topic into a multi-phase plan
- **Atlas** dispatches tasks to workers in parallel per phase, handles retries and aggregation
- **Workers** (5 types) handle search, scraping, analysis, fact-checking, and report writing

Ready to implement when you approve.