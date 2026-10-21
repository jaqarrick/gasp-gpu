from gasp.common.constants import GPU_TO_ARCH

def test_known_gpus():
    assert GPU_TO_ARCH["b200"] == "sm_100"
    assert GPU_TO_ARCH["h100"] == "sm_90"
    assert GPU_TO_ARCH["a100"] == "sm_80"

def test_unknown_gpu():
    assert GPU_TO_ARCH.get("foo") is None