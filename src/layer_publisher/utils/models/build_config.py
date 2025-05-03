from __future__ import annotations

import json

from pydantic import BaseModel

from layer_publisher.utils.variables import FILE_BUILD_CONFIG


class BuildConfig(BaseModel):
    runtimes: list[str]

    @staticmethod
    def load() -> BuildConfig:
        with open(FILE_BUILD_CONFIG) as f:
            return BuildConfig(**json.load(f))
