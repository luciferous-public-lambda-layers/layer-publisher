#!/usr/bin/env bash

set -xeuo pipefail

usage() {
  cat <<'EOT'
build.sh --arch <amd|arm> --runtime <Python Runtime> --packages <PyPI Modules>

  --arch CPU architecture. "amd" or "arm"
  --runtime Lambda Python Runtime
  --packages PyPI Modules
EOT
}

# 初期化
ARG_ARCH=""
ARG_RUNTIME=""
ARG_PACKAGES=()

# 引数の解析
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --arch)
            ARG_ARCH="$2"
            shift 2
            ;;
        --runtime)
            ARG_RUNTIME="$2"
            shift 2
            ;;
        --packages)
            shift
            # --packages の後ろに続く全ての値をARG_PACKAGES配列に格納
            while [[ $# -gt 0 && ! $1 =~ ^-- ]]; do
                ARG_PACKAGES+=("$1")
                shift
            done
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# 結果の表示
arch=$ARG_ARCH
runtime=$ARG_RUNTIME
packages="${ARG_PACKAGES[*]}"

echo "arch=:$arch:"
echo "runtime=:$runtime:"
echo "packages=:$packages:"

if [[ -z "$arch" || -z "$runtime" || -z "$packages" ]]; then
  usage
  exit 1
fi

container_image="public.ecr.aws/sam/build-${runtime}:latest"
container_name="build"

# modules/<{amd, arm}>/<{python3.13, python3.12}>/python

docker container run \
  --name $container_name \
  "$container_image" \
  pip install \
  $packages \
  -t "/tmp/dist/modules/${arch}/${runtime}/python"

docker container cp "${container_name}:/tmp/dist" .
docker container rm "${container_name}"