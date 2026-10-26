"""
instruction list, counts, blocks from SASS parser

1. Build a CFG to predict ILP and MLP per basic block. The longest chain will be value for ILP and MLP.
2. Detect loops: A back edge in the CFG indicates a loop. We need loop bounds from module 1.
3. Weight ILP by execution frequency. ILP may change depending on loops from step 2.
4. Adjust inst_count for loops and branches

TBD: Can we statically determine loop count from kernel params, or does this need to be supplied by user?

Outputs:
```
ILP (float)
MLP (float)
divergence penalty (units tbd) - used in o_div (divergence overhead)
# adjusted from loops
sfu_inst_count: int
mem_inst_count: int
sync_inst_count
"""

# organize CFG into Nodes and Edges (based on the structure of the DOT file
# in tests/fixtures/vecadd.bbcfg.dot).
from dataclasses import dataclass


@dataclass
class CFGNode:
    id: str
    label: str


@dataclass
class CFGEdge:
    source: str
    source_port: str | None
    source_compass: str | None
    target: str
    target_port: str | None
    target_compass: str | None
    attributes: str | None


@dataclass
class ControlFlowGraph:
    nodes: dict[str, CFGNode]
    edges: list[CFGEdge]
