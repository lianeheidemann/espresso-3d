"""Dataset definitions and input-image organization."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetItem:
    object_id: str
    input_image: Path
    ground_truth: Path
    category: str | None = None
