import pytest

import layer_publisher.generate.complete_generate as index


class TestClassifyLayers:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "all_layers": [
                        index.Layer(
                            identifier="zstd",
                            hash="111111111",
                            packages="zstd",
                            runtime="python3.13",
                            architectures=["arm64", "x86_64"],
                            layer_version_arn="test_arn_01",
                            created_at="111111111",
                            region="ap-northeast-1",
                        ),
                        index.Layer(
                            identifier="zstd",
                            hash="111111111",
                            packages="zstd",
                            runtime="python3.13",
                            architectures=["arm64", "x86_64"],
                            layer_version_arn="test_arn_01",
                            created_at="111111111",
                            region="ap-northeast-1",
                        ),
                    ]
                }
            )
        ],
    )
    def test_normal(self, option, expected):
        actual = index.classify_layers(**option)
        assert actual == expected
