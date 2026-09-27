#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: tools/desk-sync.sh [--status] [--config PATH]

Synchronizes a desk repository from a configuration file.

Required config keys:
  DESK_REPO_URL    Git remote URL
  DESK_LOCAL_DIR   Local checkout directory
  DESK_BRANCH      Branch to clone or fast-forward
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PATH="$SCRIPT_DIR/desk-sync.conf"
STATUS_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --status)
      STATUS_ONLY=1
      shift
      ;;
    --config)
      if [[ $# -lt 2 ]]; then
        echo "Fehler: --config erwartet einen Pfad." >&2
        exit 2
      fi
      CONFIG_PATH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Fehler: unbekanntes Argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Fehler: Konfiguration fehlt: $CONFIG_PATH" >&2
  echo "Kopiere tools/desk-sync.conf.example nach tools/desk-sync.conf und setze die Werte." >&2
  exit 1
fi

# shellcheck source=/dev/null
source "$CONFIG_PATH"

require_config() {
  local key="$1"
  local value="${!key:-}"
  if [[ -z "$value" ]]; then
    echo "Fehler: $key ist in $CONFIG_PATH nicht gesetzt." >&2
    exit 1
  fi
}

require_config DESK_REPO_URL
require_config DESK_LOCAL_DIR
require_config DESK_BRANCH

if [[ "$STATUS_ONLY" -eq 1 ]]; then
  echo "Config: $CONFIG_PATH"
  echo "Remote: $DESK_REPO_URL"
  echo "Local:  $DESK_LOCAL_DIR"
  echo "Branch: $DESK_BRANCH"
fi

if [[ ! -d "$DESK_LOCAL_DIR/.git" ]]; then
  if [[ "$STATUS_ONLY" -eq 1 ]]; then
    echo "Status: not cloned"
    exit 0
  fi
  mkdir -p "$(dirname "$DESK_LOCAL_DIR")"
  git clone --branch "$DESK_BRANCH" "$DESK_REPO_URL" "$DESK_LOCAL_DIR"
  exit 0
fi

if [[ "$STATUS_ONLY" -eq 1 ]]; then
  git -C "$DESK_LOCAL_DIR" status --short --branch
  exit 0
fi

current_branch="$(git -C "$DESK_LOCAL_DIR" rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" != "$DESK_BRANCH" ]]; then
  echo "Fehler: Checkout ist auf Branch '$current_branch', erwartet '$DESK_BRANCH'." >&2
  exit 1
fi

git -C "$DESK_LOCAL_DIR" fetch origin "$DESK_BRANCH"

local_rev="$(git -C "$DESK_LOCAL_DIR" rev-parse HEAD)"
remote_rev="$(git -C "$DESK_LOCAL_DIR" rev-parse "origin/$DESK_BRANCH")"
base_rev="$(git -C "$DESK_LOCAL_DIR" merge-base HEAD "origin/$DESK_BRANCH")"

if [[ "$local_rev" == "$remote_rev" ]]; then
  echo "Desk-Repo ist aktuell: $DESK_LOCAL_DIR"
elif [[ "$local_rev" == "$base_rev" ]]; then
  git -C "$DESK_LOCAL_DIR" pull --ff-only origin "$DESK_BRANCH"
else
  echo "Fehler: lokaler Stand divergiert von origin/$DESK_BRANCH; bitte manuell rebasen oder mergen." >&2
  exit 1
fi

