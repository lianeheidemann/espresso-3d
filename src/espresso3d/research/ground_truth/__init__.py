"""Ground-truth mesh utilities.

Normalization and registration/alignment functions belong here so geometric
metrics are computed in a documented common coordinate system.
"""

from pathlib import Path


def validate_ground_truth(path: Path) -> Path:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return path
