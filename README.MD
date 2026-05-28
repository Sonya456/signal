
## Crypto Signal API (Django)

Lightweight backend app for real-time crypto analysis and trading signals.

## 🔹 What it does
- analyzes Binance market data
- calculates indicators (EMA, RSI, Volume)
- detects trend, breakout, support/resistance
- generates **LONG score (0–10)** with probability

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

### 🔹 Tech stack

Django + DRF
Pandas / NumPy
Binance API
JWT auth
Docker

### 🔹 Run (Docker)

docker compose build
docker compose up

### App:

http://localhost:8000