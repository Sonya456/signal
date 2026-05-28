
## Market Data Processing API



Backend system for real-time cryptocurrency data processing, signal generation, and trading analysis.

Production-ready backend service with caching, modular architecture, and external API integration.


## 🔹 Main endpoint

GET /api/score?symbol=BTCUSDT

Example:

```json
{
  "score": 8,
  "probability": "HIGH",
  "long_alarm": true
}
```

### 🔹 Tech Stack

- Django + DRF  
- Pandas / NumPy  
- Binance API  
- JWT Authentication  
- Docker


### 🔹 Run (Docker)

```bash
docker compose build
docker compose up
```

### App:

http://localhost:8000