from pydantic import BaseModel


class Layer(BaseModel):
    identifier: str
    ignoreVersions: list[str] | None
    isArchitectureSplit: bool
