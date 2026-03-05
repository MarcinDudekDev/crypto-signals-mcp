# CryptoSignals MCP Server

MCP server for real-time crypto volume anomaly detection across 50+ tokens. Detects unusual trading activity, whale movements, and pump signals.

<a href="https://glama.ai/mcp/servers/@MarcinDudekDev/crypto-signals-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@MarcinDudekDev/crypto-signals-mcp/badge" alt="Crypto Signals MCP server" />
</a>

## Features

- **Volume anomaly detection** — Identifies tokens with unusual volume-to-market-cap ratios
- **50+ tokens monitored** — Continuous scanning across major cryptocurrencies
- **Anomaly classification** — Signals rated LOW, MODERATE, HIGH, or CRITICAL
- **High-confidence alerts** — Filter for only the most actionable signals
- **Live data** — Real-time prices, 24h changes, volume, and market cap

## Tools

| Tool | Description |
|------|-------------|
| `scan_all_tokens` | Scan all 50+ tokens for volume anomalies |
| `analyze_token` | Detailed analysis for a specific token (BTC, ETH, SOL, etc.) |
| `get_anomaly_alerts` | High-confidence alerts only (vol_mcap ratio above 5.0) |

## Quick Start

### Install

```bash
pip install fastmcp httpx
```

### Run

```bash
fastmcp run server.py
```

### Configure in Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "crypto-signals": {
      "command": "fastmcp",
      "args": ["run", "server.py"]
    }
  }
}
```

## Example Usage

Ask your AI assistant:
- "Scan all crypto tokens for volume anomalies"
- "Analyze Bitcoin for unusual trading activity"
- "Show me high-confidence crypto alerts"
- "Which tokens have whale movement signals right now?"

## How It Works

The server connects to a live anomaly detection API that monitors trading volume across 50+ cryptocurrencies. It calculates volume-to-market-cap ratios to identify statistically unusual trading activity — often an early indicator of price movement, whale accumulation, or pump activity.

## License

MIT