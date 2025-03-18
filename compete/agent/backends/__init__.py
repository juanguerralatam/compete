# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
# Source Attribution:
# The majority of this code is derived from the following sources:
# - Chatarena GitHub Repository: https://github.com/Farama-Foundation/chatarena

from ...config import BackendConfig

from .base import IntelligenceBackend
from .ollama import OllamaChat

ALL_BACKENDS = [
    OllamaChat,
]

BACKEND_REGISTRY = {backend.type_name: backend for backend in ALL_BACKENDS}


# Load a backend from a config dictionary
def load_backend(config: BackendConfig):
    try:
        backend_cls = BACKEND_REGISTRY[config.backend_type]
    except KeyError:
        raise ValueError(f"Unknown backend type: {config.backend_type}")

    backend = backend_cls.from_config(config)
    return backend
