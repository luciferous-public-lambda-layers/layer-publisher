import pytest

import layer_publisher.publish.build as index
from layer_publisher.utils.models import Layer


class TestGenerateLines:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "layer": Layer(
                        identifier="aws-cloudwatch-logs-url",
                        packages=["aws-cloudwatch-logs-url==1.0.3"],
                        ignoreVersions=None,
                        isArchitectureSplit=True,
                    ),
                    "all_runtimes": [
                        "python3.13",
                        "python3.12",
                        "python3.11",
                        "python3.10",
                        "python3.9",
                    ],
                },
                {
                    "amd": [
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.13",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.12",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.11",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.10",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.9",
                    ],
                    "arm": [
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.13",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.12",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.11",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.10",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.9",
                    ],
                },
            ),
            (
                {
                    "layer": Layer(
                        identifier="scraping-tool",
                        packages=["feedparser==6.0.11", "beautifulsoup4==4.13.4"],
                        ignoreVersions=None,
                        isArchitectureSplit=True,
                    ),
                    "all_runtimes": [
                        "python3.13",
                        "python3.12",
                        "python3.11",
                        "python3.10",
                        "python3.9",
                    ],
                },
                {
                    "amd": [
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch amd --runtime python3.13",
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch amd --runtime python3.12",
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch amd --runtime python3.11",
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch amd --runtime python3.10",
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch amd --runtime python3.9",
                    ],
                    "arm": [
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch arm --runtime python3.13",
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch arm --runtime python3.12",
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch arm --runtime python3.11",
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch arm --runtime python3.10",
                        "build.sh --packages feedparser==6.0.11 beautifulsoup4==4.13.4 --arch arm --runtime python3.9",
                    ],
                },
            ),
            (
                {
                    "layer": Layer(
                        identifier="aws-cloudwatch-logs-url",
                        packages=["aws-cloudwatch-logs-url==1.0.3"],
                        ignoreVersions=["python3.11", "python3.9"],
                        isArchitectureSplit=True,
                    ),
                    "all_runtimes": [
                        "python3.13",
                        "python3.12",
                        "python3.10",
                    ],
                },
                {
                    "amd": [
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.13",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.12",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.10",
                    ],
                    "arm": [
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.13",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.12",
                        "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.10",
                    ],
                },
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.generate_lines(**option)
        assert actual == expected


class TestFilterLines:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "base_lines": {
                        "amd": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.9",
                        ],
                        "arm": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.9",
                        ],
                    },
                    "env": index.EnvironmentVariables(
                        my_runner_name="ubuntu-24.04",
                        max_concurrency=2,
                        concurrency_index=0,
                    ),
                    "is_architecture_split": False,
                },
                [
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.13",
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.11",
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.9",
                ],
            ),
            (
                {
                    "base_lines": {
                        "amd": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.9",
                        ],
                        "arm": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.9",
                        ],
                    },
                    "env": index.EnvironmentVariables(
                        my_runner_name="ubuntu-24.04",
                        max_concurrency=2,
                        concurrency_index=1,
                    ),
                    "is_architecture_split": False,
                },
                [
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.12",
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.10",
                ],
            ),
            (
                {
                    "base_lines": {
                        "amd": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.9",
                        ],
                        "arm": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.9",
                        ],
                    },
                    "env": index.EnvironmentVariables(
                        my_runner_name="ubuntu-24.04-arm",
                        max_concurrency=2,
                        concurrency_index=1,
                    ),
                    "is_architecture_split": False,
                },
                [],
            ),
            (
                {
                    "base_lines": {
                        "amd": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.9",
                        ],
                        "arm": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.9",
                        ],
                    },
                    "env": index.EnvironmentVariables(
                        my_runner_name="ubuntu-24.04-arm",
                        max_concurrency=2,
                        concurrency_index=0,
                    ),
                    "is_architecture_split": True,
                },
                [
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.13",
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.11",
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.9",
                ],
            ),
            (
                {
                    "base_lines": {
                        "amd": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch amd --runtime python3.9",
                        ],
                        "arm": [
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.13",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.12",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.11",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.10",
                            "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.9",
                        ],
                    },
                    "env": index.EnvironmentVariables(
                        my_runner_name="ubuntu-24.04-arm",
                        max_concurrency=2,
                        concurrency_index=1,
                    ),
                    "is_architecture_split": True,
                },
                [
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.12",
                    "build.sh --packages aws-cloudwatch-logs-url==1.0.3 --arch arm --runtime python3.10",
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.filter_lines(**option)
        assert actual == expected
