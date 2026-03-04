"""CryptoSignals MCP Server — Real-time crypto volume anomaly detection across 50+ tokens."""

import httpx
from fastmcp import FastMCP

API_BASE = "https://frog03-20494.wykr.es"

mcp = FastMCP("CryptoSignals")


async def _fetch(path: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{API_BASE}{path}", params=params)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def scan_all_tokens() -> dict:
    """Scan 50+ crypto tokens for volume anomalies.

    Returns the top tokens with unusual volume-to-market-cap ratios,
    indicating potential price movement signals. Includes price,
    24h change, volume, market cap, and vol/mcap ratio for each token.
    """
    return await _fetch("/api/signals/free")


@mcp.tool()
async def analyze_token(symbol: str) -> dict:
    """Get detailed volume analysis for a specific crypto token.

    Args:
        symbol: Token ticker symbol (e.g. BTC, ETH, SOL, DOGE)

    Returns metrics including price, volume, market cap, vol/mcap ratio,
    and anomaly assessment for the specified token.
    """
    data = await _fetch("/api/signals/free")
    signals = data.get("signals", [])
    symbol_upper = symbol.upper()
    match = [s for s in signals if s.get("symbol", "").upper() == symbol_upper]
    if match:
        token = match[0]
        token["anomaly_level"] = (
            "CRITICAL" if token.get("vol_mcap_ratio", 0) > 20
            else "HIGH" if token.get("vol_mcap_ratio", 0) > 5
            else "MODERATE" if token.get("vol_mcap_ratio", 0) > 2
            else "LOW"
        )
        return {"token": token, "found": True}
    return {"found": False, "symbol": symbol_upper, "message": "Token not in current anomaly scan. It may not have significant volume anomalies right now."}


@mcp.tool()
async def get_anomaly_alerts() -> dict:
    """Get high-confidence volume anomaly alerts (confidence > 80%).

    Returns only tokens where the volume anomaly detection algorithm
    has high confidence that the volume spike is significant and
    potentially actionable. Premium feature for serious traders.
    """
    data = await _fetch("/api/signals/free")
    signals = data.get("signals", [])
    # Filter for high vol/mcap ratio (proxy for high confidence anomalies)
    high_confidence = [s for s in signals if s.get("vol_mcap_ratio", 0) > 5.0]
    return {
        "high_confidence_alerts": high_confidence,
        "total_scanned": len(signals),
        "alerts_found": len(high_confidence),
        "threshold": "vol_mcap_ratio > 5.0",
    }


if __name__ == "__main__":
    mcp.run()
