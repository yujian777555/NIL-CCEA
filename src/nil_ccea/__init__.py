"""NIL-CCEA 最小可审计实验组件。"""

from .factorial import generate_binary_configurations
from .interaction import estimate_pairwise_interaction
from .manifest import build_run_manifest, configuration_hash
from .runner import MockRunner

__all__ = [
    "MockRunner",
    "build_run_manifest",
    "configuration_hash",
    "estimate_pairwise_interaction",
    "generate_binary_configurations",
]
