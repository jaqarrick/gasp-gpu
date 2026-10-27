import re
from abc import ABC, abstractmethod

from gasp.cfg import ControlFlowGraph
from gasp.logger import Logger

from .types import OpCategory, SASSInstruction


class SASSParser(ABC):
    """Base parser for SASS instructions."""

    def __init__(
        self,
        cfg: ControlFlowGraph,
        kernel: str,
        opcode_table: dict[str, OpCategory],
        logger: Logger,
    ):
        self.cfg: ControlFlowGraph = cfg
        self.logger: Logger = logger
        self.kernel: str = kernel  # name of the kernel
        self.opcode_table = opcode_table

        self.STORE_OPS = {
            OpCategory.GLOBAL_STORE,
            OpCategory.LOCAL_STORE,
            OpCategory.RUNTIME_STORE,
            OpCategory.SHARED_STORE,
        }

        self.SETP_OPCODES = {"ISETP", "FSETP", "DSETP", "HSETP2", "FSET", "HSET2"}

    def parse(self) -> dict[str, list[SASSInstruction]]:
        nodes = self.cfg.nodes
        result = dict[str, list[SASSInstruction]] = {}
        for node_id, node in nodes.items():
            raw_instructions = self._trim_raw_instruction(node.label)
            result[node_id] = [self._parse_instruction(raw) for raw in raw_instructions]
        return result

    def _trim_raw_instruction(self, label: str) -> list[str]:
        raw = label.replace("\\l", "\n")
        raw = raw.replace("\\\\", "\x00")
        raw = re.sub(r"\\(.)", r"\1", raw)
        raw = raw.replace("\x00", "\\")

        instructions = []
        for line in raw.splitlines():
            line = line.strip()
            if not line.endswith(";"):
                continue

            # strip DOT record port prefixes: {<entry>, |<exit0>, }
            line = re.sub(r"^[{|](<[^>]*>)?\s*", "", line)

            # trailing ;
            line = line.rstrip(";").strip()

            if line:
                instructions.append(line)

        return instructions

    def _parse_instruction(self, instruction: str) -> SASSInstruction:
        tokens = instruction.split()
        pos = 0

        predicate = None
        # predicates handling
        if tokens[0].startswith("@"):
            pred_token = tokens[0]
            pred_register = re.sub(r"^@!?", "", pred_token)
            predicate = pred_register
            pos = 1

        raw_opcode = tokens[pos]
        pos += 1

        base_opcode = raw_opcode.split(".")[0]

        op_category = self.opcode_table.get(base_opcode)

        if op_category is None:
            self.logger.warning(f"Unknown opcode: {base_opcode}")
            op_category = OpCategory.UNKNOWN

        raw_operands = " ".join(tokens[pos:])
        operands = [op.strip() for op in raw_operands.split(",") if op.strip()]
        src_registers = set()
        dest_registers = set()

        # PT and UPT are always true, so never are dependencies
        if predicate and predicate not in ("PT", "UPT"):
            src_registers.add(predicate)

        src, dst = self._parse_operands(operands, op_category, raw_opcode)

        dest_registers.update(dst)
        src_registers.update(src)

        self.logger.info(
            f"opcode:         {base_opcode}\n"
            f"  category:     {op_category!s}\n"
            f"  predicate:    {predicate}\n"
            f"  src_registers:  {src_registers}\n"
            f"  dest_registers: {dest_registers}"
        )

        return SASSInstruction(
            opcode=base_opcode,
            category=op_category,
            predicate=predicate,
            src_registers=src_registers,
            dest_registers=dest_registers,
        )

    def _is_op_needed(self, op: str) -> bool:
        # Constant value registers not needed
        if op in ("RZ", "URZ", "PT", "UPT"):
            return False
        # same goes for special registers
        if op.startswith("SR_"):
            return False
        # hex / decimal literals
        if op.startswith("0x") or op.lstrip("-").isdigit():
            return False
        # float literals
        if re.match(r"^-?\d+\.\d+", op):
            return False
        # branch targets '(.L_1)
        return not op.startswith("`")

    def _strip_constant_mem_address(self, raw: str) -> set[str]:
        regs = set()
        inner = re.search(r"\[(\w+)\]$", raw)
        if inner:
            reg = self._strip_operand(inner.group(1))
            if re.match(r"^U?R\d+$", reg) and self._is_op_needed(reg):
                regs.add(reg)
        return regs

    def _strip_operand(self, raw: str) -> str:
        op = raw.strip()
        op = op.strip("|")
        op = op.lstrip("-~")
        op = re.sub(r"\.(reuse|64)$", "", op)
        return op

    def _strip_operand_brackets(self, raw: str) -> set[str]:
        regs = set()
        inner = raw.strip("[]")
        # account for [R2+0x16]
        for tok in re.split(r"\+", inner):
            tok = re.sub(r"\.\d+$", "", tok.strip())
            tok = self._strip_operand(tok)
            if re.match(r"^U?R\d+$", tok) and self._is_op_needed(tok):
                regs.add(tok)

        return regs

    def _parse_operands(
        self, operands: list[str], category: OpCategory, raw_opcode: str
    ) -> tuple[set[str], set[str]]:

        opcode = raw_opcode.split(".")[0]
        modifiers = raw_opcode.upper().split(".")[1:]

        is_store_op = category in self.STORE_OPS
        is_pred_op = opcode in self.SETP_OPCODES
        """
        store operations:     no destination register only
                              [address], R1

        predicate ops:        two pred destinations,
                              followed by two registers src
                              followed by one pred src
                              P0 PT R1 R2 PT
        always end with PT?
        other ops:            a single dest and at least 1 src operand
                              R1 c[0x01][RZ]
        """

        src_registers = set()
        dst_registers = set()
        for i, op in enumerate(operands):
            op = self._strip_operand(op)

            if not self._is_op_needed(op):
                continue
            if op.startswith("c["):
                src_registers.update(self._strip_constant_mem_address(op))
                continue

            # get registers from address (arch-dependent syntax)
            regs = self._parse_operand_address(op)
            if regs:
                src_registers.update(regs)

            if re.match(r"^U?R\d+$|^U?P\d+$", op):
                if is_store_op:
                    src_registers.add(op)
                elif is_pred_op and i <= 1 or i == 0:
                    dst_registers.add(op)
                else:
                    src_registers.add(op)
                continue

            self.logger.warning(f"Unrecognized operand: {op}")

        # account for opcode modifiers
        registers_per_op = 1

        if "64" in modifiers or "WIDE" in modifiers:
            registers_per_op = 2
        elif "128" in modifiers:
            registers_per_op = 4

        if registers_per_op > 1:
            additional = set()

            for reg in dst_registers:
                # If more than 1 register is needed account for this
                # LGE.WIDE R1 -> becomes R1 + R2
                match = re.match(r"^(U?R)(\d+)$", reg)
                if match:
                    prefix, num = match.group(1), int(match.group(2))
                    for offset in range(1, registers_per_op):
                        additional.add(f"{prefix}{num + offset}")
            dst_registers.update(additional)

        return src_registers, dst_registers

    @abstractmethod
    def _parse_operand_address(self, op: str) -> set[str] | None:
        pass
