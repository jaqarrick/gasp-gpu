import json
import sys
from dataclasses import dataclass
from pathlib import Path

from gasp.logger import Logger

PROFILES_DIR = Path("hardware/profiles")

GPU_PROFILES = {
    "b200": PROFILES_DIR / "b200.placeholder.json",
    "h100": PROFILES_DIR / "h100.placeholder.json",
    "a100": PROFILES_DIR / "a100.placeholder.json",
}


@dataclass
class HardwareProfile:
    architecture: str
    chip: str
    arch: str

    # spec
    warp_size: int
    simd_width: int
    sfu_width: int
    sms_per_gpu: int
    max_warps_per_sm: int
    max_blocks_per_sm: int
    max_registers_per_sm: int
    max_shared_mem_per_sm_bytes: int
    l2_cache_size_bytes: int
    max_l1_cache_size_bytes: int

    # profiled
    launch_overhead_cycles: int
    departure_delay_cycles: int
    sync_factor_cycles: int
    dram_latency_cycles: int
    l1_cache_hit_latency_cycles: int
    l2_cache_hit_latency_cycles: int
    bank_penalty_cycles: int
    sfu_inst_latency_cycles: int
    fp32_inst_latency_cycles: int
    int32_inst_latency_cycles: int
    fp64_inst_latency_cycles: int
    dram_bandwidth_bytes_per_cycle: int
    clock_rate_ghz: float


def load_hardware_profile(gpu: str, logger: Logger):
    path = GPU_PROFILES.get(gpu)

    if path is None:
        logger.error(f"No profile defined for gpu: {gpu}")
        sys.exit(1)
    else:
        logger.info(f"loading {gpu} hardware profile from {path}")

    with open(path) as f:
        profile = json.load(f)
    spec = profile.pop("spec")
    profiled = profile.pop("profiled")
    flat = {**profile, **spec, **profiled}
    return HardwareProfile(**flat)
