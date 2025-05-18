from pydantic import BaseModel


class LayerForGenerate(BaseModel):
    identifier: str
    hash: str
    packages: str
    note: str | None = None
    runtime: str
    architectures: list[str]
    layer_version_arn: str
    created_at: str
    region: str

    def parse_runtime(self) -> int:
        version = self.runtime[6:]
        major, minor = [int(x) for x in version.split(".")]
        return (major * 1000 + minor) * -1

    @property
    def sort_key(self) -> tuple[int, int, str]:
        mapping_arch = {"arm64,x86_64": 0, "x86_64": 1, "arm64": 2}

        version = self.parse_runtime()
        arch = mapping_arch[",".join(sorted(self.architectures))]
        return version, arch, self.region
