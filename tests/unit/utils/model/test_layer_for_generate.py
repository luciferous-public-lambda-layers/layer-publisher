import pytest

from layer_publisher.utils.models.layer_for_generate import LayerForGenerate


def create_layer(
    *, runtime: str, architectures: list[str], region: str
) -> LayerForGenerate:
    return LayerForGenerate(
        identifier="zstd",
        hash="1223334444",
        packages="zstd",
        runtime=runtime,
        architectures=architectures,
        layer_version_arn="{runtime}:{arch}:{region}".format(
            runtime=runtime, arch=",".join(sorted(architectures)), region=region
        ),
        created_at="1223334444",
        region=region,
    )


class TestSort:
    @pytest.mark.parametrize(
        "array, expected",
        [
            (
                [
                    create_layer(
                        runtime="python3.12",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                    create_layer(
                        runtime="python3.13",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                    create_layer(
                        runtime="python3.10",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                    create_layer(
                        runtime="python3.11",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                    create_layer(
                        runtime="python3.9",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                ],
                [
                    create_layer(
                        runtime="python3.13",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                    create_layer(
                        runtime="python3.12",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                    create_layer(
                        runtime="python3.11",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                    create_layer(
                        runtime="python3.10",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                    create_layer(
                        runtime="python3.9",
                        architectures=["arm64", "x86_64"],
                        region="ap-northeast-1",
                    ),
                ],
            )
        ],
    )
    def test_normal(self, array: list[LayerForGenerate], expected):
        actual = sorted(array, key=lambda x: x.sort_key)
        assert actual == expected
