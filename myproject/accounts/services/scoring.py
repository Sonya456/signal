def calculate_score(signals):
    score = 0
    reasons = []

    if signals["trend"] == "bullish":
        score += 2
        reasons.append("Trend bullish (+2)")
    elif signals["trend"] == "neutral":
        score += 1

    if signals["structure"] == "strong_bull":
        score += 2

    if signals["breakout"] == "confirmed":
        score += 2

    if signals["distance"] == "far":
        score += 1

    if signals["support"] == "strong":
        score += 1

    if signals["rsi"] in ["oversold", "strong"]:
        score += 1

    if signals["volume"] in ["spike", "increasing"]:
        score += 1

    return score, reasons