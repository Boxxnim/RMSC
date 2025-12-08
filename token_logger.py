"""
Token Usage Logging and Cost Estimation
========================================

Tracks API token usage and estimates costs for all models in the pipeline.
Generates detailed cost reports for transparency in publications.

Usage:
    from token_logger import TokenLogger, PRICING
    
    logger = TokenLogger()
    logger.log_usage("gemini-3-pro-preview", input_tokens=500, output_tokens=200)
    logger.print_summary()
    logger.save_report("cost_report.json")
"""

import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from pathlib import Path


# Pricing per 1M tokens (as of December 2024)
# Source: https://ai.google.dev/pricing and https://anthropic.com/pricing
PRICING = {
    # Gemini models (per 1M tokens)
    "gemini-flash-latest": {"input": 0.40, "output": 2.50},
    "gemini-3-pro-preview": {"input": 2.00, "output": 12.00},
    
    # Claude models (per 1M tokens)
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},

}


@dataclass
class UsageRecord:
    """Single API call usage record."""
    timestamp: str
    model: str
    layer: str
    record_id: Optional[str]
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float


import threading

@dataclass
class TokenLogger:
    """Tracks token usage across all API calls."""
    
    records: List[UsageRecord] = field(default_factory=list)
    totals: Dict[str, Dict[str, int]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def get_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing for a model, with fallback to estimate."""
        if model in PRICING:
            return PRICING[model]
        # Fallback: try to find a partial match or use conservative estimate
        for key in PRICING:
            if key in model or model in key:
                return PRICING[key]
        # Default fallback for unknown models
        return {"input": 1.00, "output": 5.00}
    
    def log_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        layer: str = "L2",
        record_id: Optional[str] = None
    ) -> UsageRecord:
        """Log a single API call's token usage."""
        pricing = self.get_pricing(model)
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            model=model,
            layer=layer,
            record_id=record_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost
        )
        
        with self._lock:
            self.records.append(record)
            
            # Update totals
            if model not in self.totals:
                self.totals[model] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "input_cost": 0.0,
                    "output_cost": 0.0,
                    "total_cost": 0.0,
                    "api_calls": 0
                }
            
            self.totals[model]["input_tokens"] += input_tokens
            self.totals[model]["output_tokens"] += output_tokens
            self.totals[model]["input_cost"] += input_cost
            self.totals[model]["output_cost"] += output_cost
            self.totals[model]["total_cost"] += total_cost
            self.totals[model]["api_calls"] += 1
        
        return record
    
    def get_total_cost(self) -> float:
        """Get total cost across all models."""
        return sum(m["total_cost"] for m in self.totals.values())
    
    def get_total_tokens(self) -> Dict[str, int]:
        """Get total input and output tokens."""
        return {
            "input": sum(m["input_tokens"] for m in self.totals.values()),
            "output": sum(m["output_tokens"] for m in self.totals.values())
        }
    
    def print_summary(self) -> None:
        """Print a formatted summary of token usage and costs."""
        print(f"\n{'='*70}")
        print("TOKEN USAGE & COST SUMMARY")
        print(f"{'='*70}")
        
        print(f"\n{'Model':<35} {'Calls':>8} {'Input':>12} {'Output':>12} {'Cost':>10}")
        print("-" * 70)
        
        for model, stats in sorted(self.totals.items()):
            print(f"{model:<35} {stats['api_calls']:>8} "
                  f"{stats['input_tokens']:>12,} {stats['output_tokens']:>12,} "
                  f"${stats['total_cost']:>9.4f}")
        
        print("-" * 70)
        totals = self.get_total_tokens()
        total_cost = self.get_total_cost()
        total_calls = sum(m["api_calls"] for m in self.totals.values())
        
        print(f"{'TOTAL':<35} {total_calls:>8} "
              f"{totals['input']:>12,} {totals['output']:>12,} "
              f"${total_cost:>9.4f}")
        
        print(f"\n{'='*70}")
        print(f"Estimated total cost: ${total_cost:.4f}")
        print(f"{'='*70}\n")
    
    def save_report(self, filepath: str) -> None:
        """Save detailed usage report to JSON file."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_cost": self.get_total_cost(),
                "total_tokens": self.get_total_tokens(),
                "by_model": self.totals
            },
            "pricing_used": PRICING,
            "detailed_records": [asdict(r) for r in self.records]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Detailed usage report saved to: {filepath}")
    
    def save_summary_csv(self, filepath: str) -> None:
        """Save summary to CSV for easy inclusion in papers."""
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Model", "API Calls", "Input Tokens", "Output Tokens",
                "Input Cost ($)", "Output Cost ($)", "Total Cost ($)"
            ])
            
            for model, stats in sorted(self.totals.items()):
                writer.writerow([
                    model,
                    stats["api_calls"],
                    stats["input_tokens"],
                    stats["output_tokens"],
                    f"{stats['input_cost']:.4f}",
                    f"{stats['output_cost']:.4f}",
                    f"{stats['total_cost']:.4f}"
                ])
            
            # Total row
            totals = self.get_total_tokens()
            total_cost = self.get_total_cost()
            total_calls = sum(m["api_calls"] for m in self.totals.values())
            total_input_cost = sum(m["input_cost"] for m in self.totals.values())
            total_output_cost = sum(m["output_cost"] for m in self.totals.values())
            
            writer.writerow([
                "TOTAL",
                total_calls,
                totals["input"],
                totals["output"],
                f"{total_input_cost:.4f}",
                f"{total_output_cost:.4f}",
                f"{total_cost:.4f}"
            ])
        
        print(f"Summary CSV saved to: {filepath}")


# Singleton instance for global access
_global_logger: Optional[TokenLogger] = None


def get_logger() -> TokenLogger:
    """Get or create global token logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = TokenLogger()
    return _global_logger


def reset_logger() -> None:
    """Reset the global logger."""
    global _global_logger
    _global_logger = TokenLogger()


if __name__ == "__main__":
    # Demo usage
    logger = TokenLogger()
    
    # Simulate some API calls
    logger.log_usage("gemini-flash-latest", 1000, 200, "L1", "record_1")
    logger.log_usage("gemini-flash-latest", 1200, 180, "L1", "record_2")
    logger.log_usage("gemini-3-pro-preview", 800, 250, "L2", "record_1")
    logger.log_usage("claude-sonnet-4-5-20250929", 850, 300, "L2", "record_1")
    
    logger.print_summary()
    logger.save_report("demo_cost_report.json")
    logger.save_summary_csv("demo_cost_summary.csv")
