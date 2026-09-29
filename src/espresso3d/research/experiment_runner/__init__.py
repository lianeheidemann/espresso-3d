"""Reproducible benchmark orchestration."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    dataset: str
    engines: list[str]
    runs: int = 1
    seed: int = 42
    output_dir: Path = field(default_factory=lambda: Path("research/results"))


class ExperimentRunner:
    """Coordinates benchmark runs without depending on the graphical UI."""

    def __init__(self, config: ExperimentConfig):
        self.config = config

    def validate(self) -> None:
        if not self.config.engines:
            raise ValueError("At least one reconstruction engine is required.")
        if self.config.runs < 1:
            raise ValueError("runs must be >= 1")
