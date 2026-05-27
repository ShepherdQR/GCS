"""Cost model based on provider pricing tables."""

from pathlib import Path
from typing import Optional
import yaml

from tools.token_audit.parser import TokenUsage


# Default pricing (USD per 1M tokens) — overridden by config.yaml
DEFAULT_PRICING = {
    "anthropic": {
        "claude-opus-4-7":  {"input": 15.00, "output": 75.00, "cache_write": 30.00, "cache_read": 1.50},
        "claude-sonnet-4-6": {"input": 3.00, "output": 15.00, "cache_write": 6.00, "cache_read": 0.30},
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00, "cache_write": 6.00, "cache_read": 0.30},
        "claude-haiku-4-5":  {"input": 0.80, "output": 4.00, "cache_write": 1.60, "cache_read": 0.08},
    },
    "other": {
        "deepseek-v4-pro": {"input": 0.50, "output": 2.00, "cache_write": 0.50, "cache_read": 0.05},
    },
}

# Model ID aliases (normalize to canonical name)
MODEL_ALIASES = {
    "claude-sonnet-4-6": "claude-sonnet-4-6",
    "claude-sonnet-4.6": "claude-sonnet-4-6",
    "sonnet": "claude-sonnet-4-6",
    "claude-opus-4-7": "claude-opus-4-7",
    "claude-opus-4.7": "claude-opus-4-7",
    "opus": "claude-opus-4-7",
    "claude-haiku-4-5": "claude-haiku-4-5",
    "claude-haiku-4.5": "claude-haiku-4-5",
    "haiku": "claude-haiku-4-5",
    "deepseek-v4-pro": "deepseek-v4-pro",
    "deepseek": "deepseek-v4-pro",
}


class CostModel:
    """Calculate USD costs for token usage."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = str(Path(__file__).parent / "config.yaml")
        self.pricing = DEFAULT_PRICING.copy()
        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            if "pricing" in cfg:
                self._merge_pricing(cfg["pricing"])

    def _merge_pricing(self, cfg_pricing: dict) -> None:
        """Merge config pricing into defaults."""
        for provider, models in cfg_pricing.items():
            if provider not in self.pricing:
                self.pricing[provider] = {}
            for model, rates in models.items():
                self.pricing[provider][model] = rates

    def _find_rate(self, model_id: str) -> Optional[dict]:
        """Find the pricing rate for a model, trying aliases first."""
        canonical = MODEL_ALIASES.get(model_id.lower(), model_id.lower())
        # Search all providers
        for provider, models in self.pricing.items():
            if canonical in models:
                return models[canonical]
            # Fuzzy match
            for name, rates in models.items():
                if name in canonical or canonical in name:
                    return rates
        return None

    def calculate(self, usage: TokenUsage, model_id: str) -> int:
        """Calculate cost in microdollars (1/1,000,000 USD)."""
        rates = self._find_rate(model_id)
        if rates is None:
            # Unknown model — use conservative estimate based on Sonnet pricing
            rates = self.pricing.get("anthropic", {}).get(
                "claude-sonnet-4-6",
                {"input": 3.00, "output": 15.00, "cache_write": 6.00, "cache_read": 0.30},
            )

        cost = (
            usage.input_tokens * rates["input"]
            + usage.output_tokens * rates["output"]
            + usage.cache_creation_tokens * rates.get("cache_write", rates["input"] * 2)
            + usage.cache_read_tokens * rates.get("cache_read", rates["input"] * 0.1)
        )
        # cost is in USD per 1M tokens → multiply then divide by 1M to get USD
        # then multiply by 1M to get microdollars
        return int(cost)  # Already in microdollars because input_tokens / 1e6 * price_in_usd * 1e6

    def calculate_usd(self, usage: TokenUsage, model_id: str) -> float:
        """Calculate cost in USD (float)."""
        rates = self._find_rate(model_id)
        if rates is None:
            rates = self.pricing.get("anthropic", {}).get(
                "claude-sonnet-4-6",
                {"input": 3.00, "output": 15.00, "cache_write": 6.00, "cache_read": 0.30},
            )

        cost = (
            usage.input_tokens * rates["input"]
            + usage.output_tokens * rates["output"]
            + usage.cache_creation_tokens * rates.get("cache_write", rates["input"] * 2)
            + usage.cache_read_tokens * rates.get("cache_read", rates["input"] * 0.1)
        ) / 1_000_000.0
        return cost

    @staticmethod
    def usd_display(microdollars: int) -> str:
        """Format microdollars as a USD display string."""
        return f"${microdollars / 1_000_000:.2f}"

    @staticmethod
    def usd_display_f(usd: float) -> str:
        """Format float USD as display string."""
        return f"${usd:.2f}"
