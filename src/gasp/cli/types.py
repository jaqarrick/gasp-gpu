# types.py
from dataclasses import dataclass


@dataclass
class Args:
    input: str
    gpu: str | None
    verbose: bool
    profile: str | None
    block_size: int | None
    grid_size: int | None
    problem_size: int | None