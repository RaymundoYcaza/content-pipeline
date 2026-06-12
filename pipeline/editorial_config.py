from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import yaml


@dataclass
class DepthPolicy:
    profile: str = "medium"
    target_words_min: int = 600
    target_words_max: int = 800
    min_sections: int = 4
    max_sections: int = 7
    must_include_examples: bool = True
    must_include_actionable_steps: bool = True


@dataclass
class OpeningPolicy:
    required: bool = True
    style: str = "contextual_hook"
    first_paragraph_must_hook: bool = True


@dataclass
class ValidatorPolicy:
    reject_if_opening_generic: bool = True
    reject_if_hook_missing: bool = True
    reject_if_too_shallow: bool = True
    reject_if_out_of_length_range: bool = True
    reject_if_missing_examples_when_required: bool = True
    reject_if_missing_actionable_steps_when_required: bool = True


@dataclass
class EditorialConfig:
    depth_policy: DepthPolicy = field(default_factory=DepthPolicy)
    opening_policy: OpeningPolicy = field(default_factory=OpeningPolicy)
    opening_blacklist: List[str] = field(default_factory=list)
    hook_requirements: List[str] = field(default_factory=list)
    validator: ValidatorPolicy = field(default_factory=ValidatorPolicy)


def load_editorial_config(config_path: Path = Path("config/editorial.yaml")) -> EditorialConfig:
    if not config_path.exists():
        return EditorialConfig()

    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    ed = raw.get("editorial", {})

    depth_raw = ed.get("depth_policy", {})
    opening_raw = ed.get("opening_policy", {})
    validator_raw = ed.get("validator", {})

    return EditorialConfig(
        depth_policy=DepthPolicy(**depth_raw),
        opening_policy=OpeningPolicy(**opening_raw),
        opening_blacklist=ed.get("opening_blacklist", []),
        hook_requirements=ed.get("hook_requirements", []),
        validator=ValidatorPolicy(**validator_raw),
    )