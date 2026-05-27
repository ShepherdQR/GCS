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

    def calculate(self, usage: TokenUsage, model_id: str, batch: bool = False,
                  cache_ttl: str = "5min") -> int:
        """Calculate cost in microdollars (1/1,000,000 USD).

        Rates are USD/1M tokens. Since tokens * (USD/1M) = microdollars,
        the product gives microdollars directly.
        """
        rates = self._find_rate(model_id)
        if rates is None:
            rates = {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30}

        input_rate = rates.get("batch_input", rates["input"]) if batch else rates["input"]
        output_rate = rates.get("batch_output", rates["output"]) if batch else rates["output"]
        cache_write_rate = self._resolve_cache_write(rates, cache_ttl)

        cost = (
            usage.input_tokens * input_rate
            + usage.output_tokens * output_rate
            + usage.cache_creation_tokens * cache_write_rate
            + usage.cache_read_tokens * rates.get("cache_read", rates["input"] * 0.1)
        )
        return int(cost)

    def calculate_usd(self, usage: TokenUsage, model_id: str, batch: bool = False,
                      cache_ttl: str = "5min") -> float:
        """Calculate cost in USD (float)."""
        rates = self._find_rate(model_id)
        if rates is None:
            rates = {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30}

        input_rate = rates.get("batch_input", rates["input"]) if batch else rates["input"]
        output_rate = rates.get("batch_output", rates["output"]) if batch else rates["output"]
        cache_write_rate = self._resolve_cache_write(rates, cache_ttl)

        cost = (
            usage.input_tokens * input_rate
            + usage.output_tokens * output_rate
            + usage.cache_creation_tokens * cache_write_rate
            + usage.cache_read_tokens * rates.get("cache_read", rates["input"] * 0.1)
        ) / 1_000_000.0
        return cost

    @staticmethod
    def _resolve_cache_write(rates: dict, cache_ttl: str) -> float:
        """Resolve cache write rate by TTL. Backward-compatible with 'cache_write' key."""
        ttl_key = f"cache_write_{cache_ttl}" if cache_ttl in ("5min", "1hour") else "cache_write_5min"
        if ttl_key in rates:
            return rates[ttl_key]
        if "cache_write" in rates:
            return rates["cache_write"]
        return rates.get("input", 3.00) * 1.25

    @staticmethod
    def usd_display(microdollars: int) -> str:
        """Format microdollars as a USD display string."""
        return f"${microdollars / 1_000_000:.2f}"

    @staticmethod
    def usd_display_f(usd: float) -> str:
        """Format float USD as display string."""
        return f"${usd:.2f}"

    # Models to compare in multi-model reports
    COMPARISON_MODELS = ["deepseek-v4-pro", "claude-sonnet-4-6", "claude-opus-4-7"]

    SHORT_NAMES = {
        "deepseek-v4-pro": "DeepSeek", "claude-sonnet-4-6": "Sonnet",
        "claude-opus-4-7": "Opus", "claude-haiku-4-5": "Haiku",
    }

    def calculate_multi_usd(self, usage: TokenUsage, batch: bool = False,
                            cache_ttl: str = "5min") -> dict[str, float]:
        """Calculate cost under all COMPARISON_MODELS. Returns {model_id: usd_float}."""
        results = {}
        for model_id in self.COMPARISON_MODELS:
            try:
                results[model_id] = self.calculate_usd(usage, model_id, batch=batch, cache_ttl=cache_ttl)
            except Exception:
                results[model_id] = 0.0
        return results

    @staticmethod
    def format_comparison(primary_cost: float, multi_costs: dict[str, float],
                          primary_model: str) -> str:
        """Format inline comparison: '$0.10 (vs Sonnet $2.81, Opus $4.69)'."""
        parts = []
        for mid, cost in multi_costs.items():
            if mid == primary_model:
                continue
            name = CostModel.SHORT_NAMES.get(mid, mid)
            parts.append(f"{name} ${cost:.2f}")
        if not parts:
            return f"${primary_cost:.2f}"
        return f"${primary_cost:.2f} (vs {', '.join(parts)})"
