import pytest

import layer_publisher.publish.publish.before_publish as index
from layer_publisher.utils.models import Layer


class TestFilterRuntimes:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "all_runtimes": [
                        "python3.13",
                        "python3.12",
                        "python3.11",
                        "python3.10",
                        "python3.9",
                    ],
                    "ignore_versions": [],
                },
                ["python3.13", "python3.12", "python3.11", "python3.10", "python3.9"],
            ),
            (
                {
                    "all_runtimes": [
                        "python3.13",
                        "python3.12",
                        "python3.11",
                        "python3.10",
                        "python3.9",
                    ],
                    "ignore_versions": ["python3.9"],
                },
                [
                    "python3.13",
                    "python3.12",
                    "python3.11",
                    "python3.10",
                ],
            ),
            (
                {
                    "all_runtimes": [
                        "python3.13",
                        "python3.12",
                        "python3.11",
                        "python3.10",
                        "python3.9",
                    ],
                    "ignore_versions": ["python3.11", "python3.9"],
                },
                [
                    "python3.13",
                    "python3.12",
                    "python3.10",
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.filter_runtimes(**option)
        assert actual == expected


class TestCalcDescriptionData:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "layer": Layer(
                        identifier="aws-cloudwatch-logs-url",
                        packages=["aws-cloudwatch-logs-url==1.0.3"],
                        ignoreVersions=None,
                        isArchitectureSplit=False,
                        note=None,
                    ),
                },
                index.DescriptionData(
                    identifier="aws-cloudwatch-logs-url",
                    hash="c16ed0728d85b2c89896f7ab9322391a3535b22c43f01399790223f8",
                    packages="aws-cloudwatch-logs-url==1.0.3",
                    note=None,
                ),
            ),
            (
                {
                    "layer": Layer(
                        identifier="aws-cloudwatch-logs-url",
                        packages=["aws-cloudwatch-logs-url==1.0.3"],
                        ignoreVersions=None,
                        isArchitectureSplit=False,
                        note="Generate AWS CloudWatch Logs URL",
                    ),
                },
                index.DescriptionData(
                    identifier="aws-cloudwatch-logs-url",
                    hash="18e0a12138130629ce205c6a6004e7fec302d90fe8d11cb478ddb610",
                    packages="aws-cloudwatch-logs-url==1.0.3",
                    note="Generate AWS CloudWatch Logs URL",
                ),
            ),
            (
                {
                    "layer": Layer(
                        identifier="web-scraper",
                        packages=["feedparser==6.0.11", "beautifulsoup4==4.13.4"],
                        ignoreVersions=None,
                        isArchitectureSplit=False,
                        note="web scraping tools",
                    ),
                },
                index.DescriptionData(
                    identifier="web-scraper",
                    hash="6b6c1a3edf6b01d96e8097162afdbc216380b5a8438e6cf763855c18",
                    packages="feedparser==6.0.11, beautifulsoup4==4.13.4",
                    note="web scraping tools",
                ),
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.calc_description_data(**option)
        assert actual == expected


class TestGenerateLogicalNameSuffix:
    @pytest.mark.parametrize(
        "option, expected",
        [
            ({"arch": index.Architecture.NONE, "runtime": "python3.10"}, ["Python310"]),
            ({"arch": index.Architecture.ARM, "runtime": "python3.9"}, ["Python39Arm"]),
            (
                {"arch": index.Architecture.AMD, "runtime": "python3.13"},
                ["Python313Amd"],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.generate_logical_name_suffix(**option)
        assert [actual] == expected


class TestGenerateLogicalNameLayer:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {"arch": index.Architecture.NONE, "runtime": "python3.13"},
                ["LayerPython313"],
            ),
            (
                {"arch": index.Architecture.AMD, "runtime": "python3.9"},
                ["LayerPython39Amd"],
            ),
            (
                {"arch": index.Architecture.ARM, "runtime": "python3.10"},
                ["LayerPython310Arm"],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.generate_logical_name_layer(**option)
        assert [actual] == expected


class Test_GenerateLayerCodeUri:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {"arch": index.Architecture.ARM, "runtime": "python3.13"},
                ["      CodeUri: modules/arm/python3.13"],
            ),
            (
                {"arch": index.Architecture.AMD, "runtime": "python3.11"},
                ["      CodeUri: modules/amd/python3.11"],
            ),
            (
                {"arch": index.Architecture.NONE, "runtime": "python3.9"},
                ["      CodeUri: modules/amd/python3.9"],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index._generate_layer_code_uri(**option)
        assert actual == expected


class Test_GenerateLayerLayerName:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "identifier": "aws-cloudwatch-logs-url",
                    "arch": index.Architecture.NONE,
                    "runtime": "python3.13",
                },
                ["      LayerName: LuciferousPublicLayerAwsCloudwatchLogsUrlPython313"],
            ),
            (
                {
                    "identifier": "zstd",
                    "arch": index.Architecture.ARM,
                    "runtime": "python3.9",
                },
                ["      LayerName: LuciferousPublicLayerZstdPython39Arm"],
            ),
            (
                {
                    "identifier": "zstd",
                    "arch": index.Architecture.AMD,
                    "runtime": "python3.10",
                },
                ["      LayerName: LuciferousPublicLayerZstdPython310Amd"],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index._generate_layer_layer_name(**option)
        assert actual == expected


class Test_GenerateLayerCompatibleArchitectures:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {"arch": index.Architecture.NONE},
                [
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "        - x86_64",
                ],
            ),
            (
                {"arch": index.Architecture.AMD},
                [
                    "      CompatibleArchitectures:",
                    "        - x86_64",
                ],
            ),
            (
                {"arch": index.Architecture.ARM},
                [
                    "      CompatibleArchitectures:",
                    "        - arm64",
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index._generate_layer_compatible_architectures(**option)
        assert actual == expected


class Test_GenerateLayerCompatibleRuntimes:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {"runtime": "python3.13"},
                ["      CompatibleRuntimes:", "        - python3.13"],
            ),
            (
                {"runtime": "python3.12"},
                ["      CompatibleRuntimes:", "        - python3.12"],
            ),
            (
                {"runtime": "python3.11"},
                ["      CompatibleRuntimes:", "        - python3.11"],
            ),
            (
                {"runtime": "python3.10"},
                ["      CompatibleRuntimes:", "        - python3.10"],
            ),
            (
                {"runtime": "python3.9"},
                ["      CompatibleRuntimes:", "        - python3.9"],
            ),
            (
                {"runtime": "python3.13"},
                ["      CompatibleRuntimes:", "        - python3.13"],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index._generate_layer_compatible_runtimes(**option)
        assert actual == expected


class TestGenerateLayer:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "arch": index.Architecture.NONE,
                    "runtime": "python3.13",
                    "desc_data": index.DescriptionData(
                        identifier="aws-cloudwatch-logs-url",
                        hash="1223334444",
                        packages="aws-cloudwatch-logs-url==1.0.3",
                    ),
                },
                [
                    "  LayerPython313:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.13",
                    "      LayerName: LuciferousPublicLayerAwsCloudwatchLogsUrlPython313",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.13",
                    "      Description: |",
                    "        identifier=== aws-cloudwatch-logs-url",
                    "        hash=== 1223334444",
                    "        packages=== aws-cloudwatch-logs-url==1.0.3",
                    "",
                ],
            ),
            (
                {
                    "arch": index.Architecture.NONE,
                    "runtime": "python3.13",
                    "desc_data": index.DescriptionData(
                        identifier="aws-cloudwatch-logs-url",
                        hash="1223334444",
                        packages="aws-cloudwatch-logs-url==1.0.3",
                        note="test data",
                    ),
                },
                [
                    "  LayerPython313:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.13",
                    "      LayerName: LuciferousPublicLayerAwsCloudwatchLogsUrlPython313",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.13",
                    "      Description: |",
                    "        identifier=== aws-cloudwatch-logs-url",
                    "        hash=== 1223334444",
                    "        packages=== aws-cloudwatch-logs-url==1.0.3",
                    "        note=== test data",
                    "",
                ],
            ),
            (
                {
                    "arch": index.Architecture.ARM,
                    "runtime": "python3.10",
                    "desc_data": index.DescriptionData(
                        identifier="web-scraper",
                        hash="1223334444",
                        packages="feedparser==6.0.11, beautifulsoup4==4.13.4",
                    ),
                },
                [
                    "  LayerPython310Arm:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/arm/python3.10",
                    "      LayerName: LuciferousPublicLayerWebScraperPython310Arm",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "      CompatibleRuntimes:",
                    "        - python3.10",
                    "      Description: |",
                    "        identifier=== web-scraper",
                    "        hash=== 1223334444",
                    "        packages=== feedparser==6.0.11, beautifulsoup4==4.13.4",
                    "",
                ],
            ),
            (
                {
                    "arch": index.Architecture.AMD,
                    "runtime": "python3.9",
                    "desc_data": index.DescriptionData(
                        identifier="zstd",
                        hash="1223334444",
                        packages="zstd==1.5.7.0",
                    ),
                },
                [
                    "  LayerPython39Amd:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.9",
                    "      LayerName: LuciferousPublicLayerZstdPython39Amd",
                    "      CompatibleArchitectures:",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.9",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.generate_layer(**option)
        assert actual == expected


class Test_GeneratePermissionLogicalName:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {"arch": index.Architecture.NONE, "runtime": "python3.13"},
                ["  PermissionPython313:"],
            ),
            (
                {"arch": index.Architecture.ARM, "runtime": "python3.9"},
                ["  PermissionPython39Arm:"],
            ),
            (
                {"arch": index.Architecture.AMD, "runtime": "python3.11"},
                ["  PermissionPython311Amd:"],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index._generate_permission_logical_name(**option)
        assert actual == expected


class Test_GeneratePermissionLayerVersionArn:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {"arch": index.Architecture.NONE, "runtime": "python3.13"},
                ["      LayerVersionArn: !Ref LayerPython313"],
            ),
            (
                {"arch": index.Architecture.AMD, "runtime": "python3.9"},
                ["      LayerVersionArn: !Ref LayerPython39Amd"],
            ),
            (
                {"arch": index.Architecture.ARM, "runtime": "python3.11"},
                ["      LayerVersionArn: !Ref LayerPython311Arm"],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index._generate_permission_layer_version_arn(**option)
        assert actual == expected


class TestGeneratePermission:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {"arch": index.Architecture.NONE, "runtime": "python3.13"},
                [
                    "  PermissionPython313:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython313",
                    "",
                ],
            ),
            (
                {"arch": index.Architecture.AMD, "runtime": "python3.9"},
                [
                    "  PermissionPython39Amd:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython39Amd",
                    "",
                ],
            ),
            (
                {"arch": index.Architecture.ARM, "runtime": "python3.11"},
                [
                    "  PermissionPython311Arm:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython311Arm",
                    "",
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.generate_permission(**option)
        assert actual == expected


class TestGenerateTemplate:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "all_architectures": [index.Architecture.NONE],
                    "target_runtimes": [
                        "python3.13",
                        "python3.12",
                        "python3.11",
                        "python3.10",
                        "python3.9",
                    ],
                    "desc_data": index.DescriptionData(
                        identifier="aws-cloudwatch-logs-url",
                        hash="1223334444",
                        packages="aws-cloudwatch-logs-url==1.0.3",
                    ),
                },
                [
                    "Transform: AWS::Serverless-2016-10-31",
                    "Resources:",
                    "  LayerPython313:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.13",
                    "      LayerName: LuciferousPublicLayerAwsCloudwatchLogsUrlPython313",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.13",
                    "      Description: |",
                    "        identifier=== aws-cloudwatch-logs-url",
                    "        hash=== 1223334444",
                    "        packages=== aws-cloudwatch-logs-url==1.0.3",
                    "",
                    "  PermissionPython313:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython313",
                    "",
                    "  LayerPython312:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.12",
                    "      LayerName: LuciferousPublicLayerAwsCloudwatchLogsUrlPython312",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.12",
                    "      Description: |",
                    "        identifier=== aws-cloudwatch-logs-url",
                    "        hash=== 1223334444",
                    "        packages=== aws-cloudwatch-logs-url==1.0.3",
                    "",
                    "  PermissionPython312:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython312",
                    "",
                    "  LayerPython311:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.11",
                    "      LayerName: LuciferousPublicLayerAwsCloudwatchLogsUrlPython311",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.11",
                    "      Description: |",
                    "        identifier=== aws-cloudwatch-logs-url",
                    "        hash=== 1223334444",
                    "        packages=== aws-cloudwatch-logs-url==1.0.3",
                    "",
                    "  PermissionPython311:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython311",
                    "",
                    "  LayerPython310:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.10",
                    "      LayerName: LuciferousPublicLayerAwsCloudwatchLogsUrlPython310",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.10",
                    "      Description: |",
                    "        identifier=== aws-cloudwatch-logs-url",
                    "        hash=== 1223334444",
                    "        packages=== aws-cloudwatch-logs-url==1.0.3",
                    "",
                    "  PermissionPython310:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython310",
                    "",
                    "  LayerPython39:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.9",
                    "      LayerName: LuciferousPublicLayerAwsCloudwatchLogsUrlPython39",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.9",
                    "      Description: |",
                    "        identifier=== aws-cloudwatch-logs-url",
                    "        hash=== 1223334444",
                    "        packages=== aws-cloudwatch-logs-url==1.0.3",
                    "",
                    "  PermissionPython39:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython39",
                    "",
                ],
            ),
            (
                {
                    "all_architectures": [
                        index.Architecture.AMD,
                        index.Architecture.ARM,
                    ],
                    "target_runtimes": [
                        "python3.13",
                        "python3.12",
                        "python3.11",
                        "python3.10",
                        "python3.9",
                    ],
                    "desc_data": index.DescriptionData(
                        identifier="zstd",
                        hash="1223334444",
                        packages="zstd==1.5.7.0",
                    ),
                },
                [
                    "Transform: AWS::Serverless-2016-10-31",
                    "Resources:",
                    "  LayerPython313Amd:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.13",
                    "      LayerName: LuciferousPublicLayerZstdPython313Amd",
                    "      CompatibleArchitectures:",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.13",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython313Amd:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython313Amd",
                    "",
                    "  LayerPython312Amd:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.12",
                    "      LayerName: LuciferousPublicLayerZstdPython312Amd",
                    "      CompatibleArchitectures:",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.12",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython312Amd:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython312Amd",
                    "",
                    "  LayerPython311Amd:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.11",
                    "      LayerName: LuciferousPublicLayerZstdPython311Amd",
                    "      CompatibleArchitectures:",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.11",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython311Amd:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython311Amd",
                    "",
                    "  LayerPython310Amd:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.10",
                    "      LayerName: LuciferousPublicLayerZstdPython310Amd",
                    "      CompatibleArchitectures:",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.10",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython310Amd:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython310Amd",
                    "",
                    "  LayerPython39Amd:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/amd/python3.9",
                    "      LayerName: LuciferousPublicLayerZstdPython39Amd",
                    "      CompatibleArchitectures:",
                    "        - x86_64",
                    "      CompatibleRuntimes:",
                    "        - python3.9",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython39Amd:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython39Amd",
                    "",
                    "  LayerPython313Arm:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/arm/python3.13",
                    "      LayerName: LuciferousPublicLayerZstdPython313Arm",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "      CompatibleRuntimes:",
                    "        - python3.13",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython313Arm:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython313Arm",
                    "",
                    "  LayerPython312Arm:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/arm/python3.12",
                    "      LayerName: LuciferousPublicLayerZstdPython312Arm",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "      CompatibleRuntimes:",
                    "        - python3.12",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython312Arm:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython312Arm",
                    "",
                    "  LayerPython311Arm:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/arm/python3.11",
                    "      LayerName: LuciferousPublicLayerZstdPython311Arm",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "      CompatibleRuntimes:",
                    "        - python3.11",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython311Arm:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython311Arm",
                    "",
                    "  LayerPython310Arm:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/arm/python3.10",
                    "      LayerName: LuciferousPublicLayerZstdPython310Arm",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "      CompatibleRuntimes:",
                    "        - python3.10",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython310Arm:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython310Arm",
                    "",
                    "  LayerPython39Arm:",
                    "    Type: AWS::Serverless::LayerVersion",
                    "    Properties:",
                    "      RetentionPolicy: Retain",
                    "      CodeUri: modules/arm/python3.9",
                    "      LayerName: LuciferousPublicLayerZstdPython39Arm",
                    "      CompatibleArchitectures:",
                    "        - arm64",
                    "      CompatibleRuntimes:",
                    "        - python3.9",
                    "      Description: |",
                    "        identifier=== zstd",
                    "        hash=== 1223334444",
                    "        packages=== zstd==1.5.7.0",
                    "",
                    "  PermissionPython39Arm:",
                    "    Type: AWS::Lambda::LayerVersionPermission",
                    "    DeletionPolicy: Retain",
                    "    UpdateReplacePolicy: Retain",
                    "    Properties:",
                    "      Action: lambda:GetLayerVersion",
                    "      Principal: '*'",
                    "      LayerVersionArn: !Ref LayerPython39Arm",
                    "",
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.generate_template(**option)
        assert actual.split("\n") == expected


class TestGenerateScript:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "bucket_name": "test-s3-bucket",
                    "identifier": "aws-cloudwatch-logs-url",
                },
                [
                    "aws cloudformation package --s3-bucket test-s3-bucket --template-file sam.yml --output-template-file template.yml",
                    "sam deploy --stack-name LayerAwsCloudwatchLogsUrl --template-file template.yml",
                ],
            ),
            (
                {"bucket_name": "test-s3-bucket", "identifier": "zstd"},
                [
                    "aws cloudformation package --s3-bucket test-s3-bucket --template-file sam.yml --output-template-file template.yml",
                    "sam deploy --stack-name LayerZstd --template-file template.yml",
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.generate_script(**option)
        assert actual.split("\n") == expected
