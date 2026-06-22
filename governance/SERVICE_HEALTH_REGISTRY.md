# Service Health Registry

## Dynamic System Performance Forecasts

| Time Horizon | Predicted Risk Description | Probability | Blast Radius Impact | Expected System Impact |
| :--- | :--- | :--- | :--- | :--- |
| 7 Days | PostgreSQL Lock Contention under concurrent execution spikes in uawos_state_utils. | Low (12%) | Critical (Score: 100) | Degraded API latency during high concurrent intake schedules. |
| 30 Days | Local Ollama gateway context saturation during complex multi-agent simulations. | Medium (38%) | High (Score: 65) | Agent planning loops timing out, resulting in fallback deterministic completions. |
| 60 Days | Storage capacity warning on Qdrant collections with unindexed metadata vectors. | Medium (45%) | Medium (Score: 45) | Short-term memory recall degradation and vector retrieval latency spikes. |
| 90 Days | Circular dependency deadlock within executing planning graphs. | High (65%) | Critical (Score: 85) | Cascading task cancellations and state engine freeze. |

*Last updated: 2026-06-22T06:49:00+0530*
