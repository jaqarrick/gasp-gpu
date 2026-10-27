from dataclasses import dataclass
from enum import Enum, auto


class OpCategory(Enum):
    FP32 = auto()
    FP64 = auto()
    FP16 = auto()
    INT = auto()
    SFU = auto()
    CONVERSION = auto()
    TENSOR = auto()
    GLOBAL_LOAD = auto()
    GLOBAL_STORE = auto()
    SHARED_LOAD = auto()
    SHARED_STORE = auto()
    LOCAL_LOAD = auto()
    LOCAL_STORE = auto()
    RUNTIME_LOAD = auto()
    RUNTIME_STORE = auto()
    CONST_LOAD = auto()

    ASYNC_COPY = auto()
    OTHER_MEM = auto()
    BARRIER = auto()
    CONTROL = auto()
    MOVEMENT = auto()
    PREDICATE = auto()
    UNIFORM = auto()
    MISC = auto()

    UNKNOWN = auto()


@dataclass
class SASSInstruction:
    opcode: str
    category: OpCategory
    predicate: str | None
    src_registers: set[str]
    dest_registers: set[str]
