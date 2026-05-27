"""Cost model based on provider pricing tables."""

from pathlib import Path
from typing import Optional
import yaml

from tools.token_audit.parser import TokenUsage


# Default pricing (USD per 1M tokens) — overridden by config.yaml
# Source: official API pricing pages, May 2026
DEFAULT_PRICING = {
    "anthropic": {
        "claude-opus-4-7":  {"input": 5.00, "output": 25.00, "cache_write": 6.25, "cache_read": 0.50},
        "claude-sonnet-4-6": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
        "claude-haiku-4-5":  {"input": 1.00, "output": 5.00, "cache_write": 1.25, "cache_read": 0.10},
    },
    "other": {
        "deepseek-v4-pro": {"input": 0.435, "output": 0.87, "cache_write": 0.435, "cache_read": 0.0035},
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
        self.config: dict = {}
        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
            if "pricing" in self.config:
                self._merge_pricing(self.config["pricing"])

    @property
    def default_model(self) -> str:
        """Default pricing model for reports (from config)."""
        return self.config.get("report", {}).get("default_pricing_model", "deepseek-v4-pro")

    def resolve_model(self, pricing_flag: str, actual_model: str = "") -> str:
        """Resolve a --pricing flag value to a concrete model ID.

        - 'deepseek' → deepseek-v4-pro (default report pricing)
        - 'anthropic' → the actual model used, or sonnet as fallback
        - specific model name → that model
        """
        if not pricing_flag:
            return self.default_model
        if pricing_flag == "deepseek":
            return "deepseek-v4-pro"
        if pricing_flag == "anthropic":
            return actual_model or "claude-sonnet-4-6"
        return pricing_flag

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
        """Calculate cost in microdollars (1/1,000,000 USD).

        Rates are USD/1M tokens. Since tokens * (USD/1M) = microdollars,
        the product gives microdollars directly.
        """
        rates = self._find_rate(model_id)
        if rates is None:
            rates = {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30}

        cost = (
            usage.input_tokens * rates["input"]
            + usage.output_tokens * rates["output"]
            + usage.cache_creation_tokens * rates.get("cache_write", rates["input"] * 1.25)
            + usage.cache_read_tokens * rates.get("cache_read", rates["input"] * 0.1)
        )
        return int(cost)

    def calculate_usd(self, usage: TokenUsage, model_id: str) -> float:
        """Calculate cost in USD (float)."""
        rates = self._find_rate(model_id)
        if rates is None:
            rates = {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30}

        cost = (
            usage.input_tokens * rates["input"]
            + usage.output_tokens * rates["output"]
            + usage.cache_creation_tokens * rates.get("cache_write", rates["input"] * 1.25)
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
