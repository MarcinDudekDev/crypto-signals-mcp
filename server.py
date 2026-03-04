"""CryptoSignals MCP Server — Real-time crypto volume anomaly detection across 50+ tokens."""

import time
import httpx
from fastmcp import FastMCP

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
CACHE_TTL = 60  # seconds — avoids CoinGecko rate limits (free tier: 10-30 req/min)

mcp = FastMCP("CryptoSignals")

_cache: dict = {"data": None, "ts": 0}


async def _fetch_signals() -> list[dict]:
    now = time.time()
    if _cache["data"] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["data"]
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": "50",
        "page": "1",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(3):
            resp = await client.get(COINGECKO_URL, params=params)
            if resp.status_code == 429:
                import asyncio
                await asyncio.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            break
        else:
            resp.raise_for_status()
        raw = resp.json()

    signals = []
    for coin in raw:
        mc = coin.get("market_cap") or 0
        vol = coin.get("total_volume") or 0
        ratio = round(vol / mc * 100, 2) if mc > 0 else 0
        signals.append({
            "symbol": (coin.get("symbol") or "").upper(),
            "price": coin.get("current_price"),
            "change_24h": coin.get("price_change_percentage_24h"),
            "volume": vol,
            "market_cap": mc,
            "vol_mcap_ratio": ratio,
        })
    signals.sort(key=lambda s: s["vol_mcap_ratio"], reverse=True)
    _cache["data"] = signals
    _cache["ts"] = now
    return signals


@mcp.tool()
async def scan_all_tokens() -> dict:
    """Scan 50+ crypto tokens for volume anomalies.

    Returns the top tokens with unusual volume-to-market-cap ratios,
    indicating potential price movement signals. Includes price,
    24h change, volume, market cap, and vol/mcap ratio for each token.
    """
    signals = await _fetch_signals()
    return {"signals": signals, "count": len(signals), "source": "coingecko"}


@mcp.tool()
async def analyze_token(symbol: str) -> dict:
    """Get detailed volume analysis for a specific crypto token.

    Args:
        symbol: Token ticker symbol (e.g. BTC, ETH, SOL, DOGE)

    Returns metrics including price, volume, market cap, vol/mcap ratio,
    and anomaly assessment for the specified token.
    """
    signals = await _fetch_signals()
    symbol_upper = symbol.upper()
    match = [s for s in signals if s["symbol"] == symbol_upper]
    if match:
        token = match[0]
        r = token["vol_mcap_ratio"]
        token["anomaly_level"] = (
            "CRITICAL" if r > 20
            else "HIGH" if r > 5
            else "MODERATE" if r > 2
            else "LOW"
        )
        return {"token": token, "found": True}
    return {
        "found": False,
        "symbol": symbol_upper,
        "message": "Token not in top 50 by volume. Try a more popular token.",
    }


@mcp.tool()
async def get_anomaly_alerts() -> dict:
    """Get high-confidence volume anomaly alerts.

    Returns only tokens where the volume-to-market-cap ratio exceeds 5%,
    indicating significant and potentially actionable volume spikes.
    """
    signals = await _fetch_signals()
    high_confidence = [s for s in signals if s["vol_mcap_ratio"] > 5.0]
    return {
        "high_confidence_alerts": high_confidence,
        "total_scanned": len(signals),
        "alerts_found": len(high_confidence),
        "threshold": "vol_mcap_ratio > 5.0",
    }


if __name__ == "__main__":
    import os, sys
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        transport = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "stdio"
    else:
        transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        port = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 8788
    else:
        port = int(os.environ.get("PORT", "8788"))
    if transport == "sse":
        mcp.run(transport="sse", host="::", port=port)
    else:
        mcp.run()
