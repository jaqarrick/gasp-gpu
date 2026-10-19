import argparse
import math
import os
import sys

from gasp import __version__
from gasp.cuda import CUDAExtractor
from gasp.logger import Logger

from .constants import DEFAULT_BLOCK_SIZE, DEFAULT_PROBLEM_SIZE, GPU_TO_ARCH
from .types import Args


def cu_file(path: str) -> str:
    if not path.endswith(".cu"):
        raise argparse.ArgumentTypeError(f"expected a .cu file, got '{path}'")
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"file not found: {path}")
    return path

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gasp",
        description="GASP: GPU Analytical Static Predictor"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--gpu", help="built-in GPU name (e.g., b200)")
    group.add_argument("--profile", help="path to custom hardware profile JSON")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")    
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("input", type=cu_file, metavar="FILE", help="path to .cu file")

    parser.add_argument("--block-size", type=int, default=None, help="Number of threads per block to be launched")
    parser.add_argument("--grid-size", type=int, default=None, help="Size of the grid")
    parser.add_argument("--problem-size", type=int, default=None, help="Size of the input")

    return parser


def main() -> None:
    parser = build_parser()
    raw = parser.parse_args()
    args = Args(**vars(raw))
    verbose = args.verbose
    profile = args.profile
    gpu = args.gpu.lower()
    input_file = args.input
    grid_size = args.grid_size
    block_size = args.block_size
    problem_size = args.problem_size

    logger = Logger(verbose)
    logger.info("Verbose mode enabled")

    if block_size is None: 
        logger.info(f"No argument for --block-size supplied. Defaulting to {DEFAULT_BLOCK_SIZE}")
        block_size = DEFAULT_BLOCK_SIZE

    if problem_size is None:
        logger.info(f"No argument for --problem-size supplied. Defaulting to {DEFAULT_PROBLEM_SIZE}")
        problem_size = DEFAULT_PROBLEM_SIZE

    if grid_size is None:
        grid_size = math.ceil(problem_size / block_size)
        logger.info(f"No argument for --grid_size supplied. Defaulting to ceil(problem_size / block_size) = {grid_size}")

    arch = GPU_TO_ARCH.get(gpu.lower())

    if arch is None:
        logger.error(f"No architecture defined for GPU {gpu}")
        sys.exit(1)
    
    logger.table(
        "Configuration",
        ["Parameter", "Value"],
        [
            ["GPU", str(gpu or "Not provided")],
            ["Profile", str(profile or "Not provided")],
            ["Input", input_file],
            ["Block Size", str(block_size)],
            ["Grid Size", str(grid_size)],
            ["Problem Size", str(problem_size)],
            ["Verbose", str(verbose)],
        ],
    )

    logger.info(f"Extracting SASS and resource usage from {input_file}")

    extractor = CUDAExtractor(input_file, arch, logger)
    result = extractor.process()

    print(result["resources"])



if __name__ == "__main__":
    main()