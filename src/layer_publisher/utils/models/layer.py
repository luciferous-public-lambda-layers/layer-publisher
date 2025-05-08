from __future__ import annotations

import json

from pydantic import BaseModel

from layer_publisher.utils.variables import FILE_LAYER_INFO


class Layer(BaseModel):
    identifier: str
    packages: list[str]
    ignoreVersions: list[str] | None
    isArchitectureSplit: bool
    note: str | None

    def get_ignore_versions(self) -> list[str]:
        if self.ignoreVersions:
            return self.ignoreVersions
        else:
            return []

    @staticmethod
    def load() -> Layer:
        with open(FILE_LAYER_INFO) as f:
            return Layer(**json.load(f))
