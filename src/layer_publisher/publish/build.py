from typing import TypedDict

from pydantic_settings import BaseSettings

from layer_publisher.utils.models import BuildConfig, Layer
from layer_publisher.utils.variables import FILE_INSTALL_SCRIPT


class EnvironmentVariables(BaseSettings):
    my_runner_name: str
    max_concurrency: int
    concurrency_index: int


class BaseLines(TypedDict):
    arm: list[str]
    amd: list[str]


def main():
    env = EnvironmentVariables()
    config = BuildConfig.load()
    layer = Layer.load()
    print(layer)
    print(env)
    print("=" * 20)
    base_lines = generate_lines(
        layer=layer,
        all_runtimes=config.runtimes,
    )
    lines = filter_lines(
        base_lines=base_lines, env=env, is_architecture_split=layer.isArchitectureSplit
    )
    write_script(lines=lines)


def generate_lines(*, layer: Layer, all_runtimes: list[str]) -> BaseLines:
    result = {"amd": [], "arm": []}
    text_packages = " ".join(layer.packages)
    for arch in result.keys():
        for runtime in all_runtimes:
            if runtime in layer.get_ignore_versions():
                continue
            result[arch].append(
                f"./build.sh --packages {text_packages} --arch {arch} --runtime {runtime}"
            )
    return result


def filter_lines(
    *, base_lines: BaseLines, env: EnvironmentVariables, is_architecture_split: bool
) -> list[str]:
    if "arm" in env.my_runner_name:
        if is_architecture_split:
            lines = base_lines["arm"]
        else:
            lines = []
    else:
        lines = base_lines["amd"]
    return [
        x
        for i, x in enumerate(lines)
        if i % env.max_concurrency == env.concurrency_index
    ]


def write_script(*, lines: list[str]):
    text = "\n".join(lines)
    print(text)
    with open(FILE_INSTALL_SCRIPT, "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
