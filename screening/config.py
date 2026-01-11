"""
Configuration for LLM-assisted Systematic Review Screening
==========================================================

Environment variables required:
- GEMINI_API_KEY: Google AI API key for Gemini models
- ANTHROPIC_API_KEY: Anthropic API key for Claude models

Usage:
    export GEMINI_API_KEY="your-key-here"
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for a single model."""
    name: str
    api_key_env: str
    temperature: float = 0.0


# Model configurations
# Layer 1: Fast screening with Gemini 2.5 Flash (best price-performance)
GEMINI_FLASH = ModelConfig(
    name="gemini-flash-latest",
    api_key_env="GEMINI_API_KEY",
    temperature=0.0
)

# Layer 2: Inclusion verification with Gemini 3 Pro Preview (state-of-the-art)
GEMINI_PRO = ModelConfig(
    name="gemini-3-pro-preview",
    api_key_env="GEMINI_API_KEY",
    temperature=0.5
)

# Layer 2: Cross-validation with Claude Sonnet 4.5 (best balance)
CLAUDE_SONNET = ModelConfig(
    name="claude-sonnet-4-5-20250929",
    api_key_env="ANTHROPIC_API_KEY",
    temperature=0.0
)

# Alternative: Claude Opus 4.5 for highest quality (higher cost)
CLAUDE_OPUS = ModelConfig(
    name="claude-opus-4-20250514",
    api_key_env="ANTHROPIC_API_KEY",
    temperature=0.0
)


# File paths
PATHS = {
    "input_ris": "MP_Liver_Update.ris",
    "screening_csv": "screening_records.csv",
    "layer1_output": "layer1_results.csv",
    "layer2_output": "layer2_results.csv",
    "final_output": "screening_final.csv",
}


# Exclusion criteria tags
EXCLUSION_TAGS = {
    "EXC-1": "Animal study",
    "EXC-2": "Pediatric population",
    "EXC-3": "Non-liver organ only",
    "EXC-4": "Non-comparative design",
    "EXC-5": "Combined perfusion (HOPE+NMP)",
    "EXC-6": "NRP alone without ex vivo MP",
    "EXC-7": "Review/meta-analysis",
    "EXC-8": "Editorial/letter/commentary",
    "EXC-9": "Case report (<5 cases)",
    "EXC-10": "Conference abstract only",
}

# Inclusion criteria tags
INCLUSION_TAGS = {
    "INC-1": "RCT or matched comparative study",
    "INC-2": "HOPE or NMP intervention",
    "INC-3": "SCS comparator",
    "INC-4": "Adult liver transplantation",
    "INC-5": "ECD or DCD donor",
}


def get_api_key(env_var: str) -> str:
    """Get API key from environment variable."""
    key = os.environ.get(env_var)
    if not key:
        raise ValueError(f"Environment variable {env_var} not set")
    return key
