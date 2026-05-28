#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PUBLIC_DIR="${ROOT_DIR}/infra/cloudflare/hplan-installer/public/hplan"

bash "${ROOT_DIR}/scripts/build-installer-package.sh"

rm -rf "${PUBLIC_DIR}"
mkdir -p "${PUBLIC_DIR}"

cp "${ROOT_DIR}/scripts/setup.sh" "${PUBLIC_DIR}/install.sh"
cp "${ROOT_DIR}/dist/version.json" "${PUBLIC_DIR}/version.json"
cp "${ROOT_DIR}/dist/hplan-package.tar.gz" "${PUBLIC_DIR}/hplan-package.tar.gz"

echo "Prepared Worker assets in ${PUBLIC_DIR}"
