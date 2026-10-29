#!/bin/bash
set -euo pipefail
[[ "$(uname -s)" == Darwin ]] || { echo "macOS에서 실행하세요." >&2; exit 1; }
if ! xcrun --find swiftc >/dev/null 2>&1; then
  echo "먼저 macOS 개발 도구를 설치해 주세요. 설치 창에서 완료한 뒤 이 명령을 다시 실행하세요."
  xcode-select --install
  exit 1
fi
SOURCE=""
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
  SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
fi
TEMP=""
cleanup() { if [[ -n "$TEMP" ]]; then rm -rf -- "$TEMP"; fi; }
trap cleanup EXIT
if [[ ! -f "$SOURCE/scripts/setup.py" || ! -f "$SOURCE/Sources/MenuApp.swift" ]]; then
  TEMP="$(mktemp -d "${TMPDIR:-/tmp}/windows-steam-install.XXXXXX")"
  curl --fail --location --silent --show-error \
    https://codeload.github.com/Ggumnamu1325/windows-steam/tar.gz/refs/heads/main \
    -o "$TEMP/source.tar.gz"
  tar -xzf "$TEMP/source.tar.gz" -C "$TEMP"
  SOURCE="$TEMP/windows-steam-main"
fi
/usr/bin/python3 "$SOURCE/scripts/setup.py" "$@" </dev/tty
