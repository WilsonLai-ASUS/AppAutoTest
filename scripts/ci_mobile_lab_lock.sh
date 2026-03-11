#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ci_mobile_lab_lock.sh acquire <lock_dir>
  ci_mobile_lab_lock.sh release <lock_dir>

Notes:
- <lock_dir> can be absolute or relative. If relative, it is resolved under $HOME.
- On acquire, exports CI_LOCK_DIR via $GITHUB_ENV when available.
- On release, only removes the lock when owned by this workflow run (by GITHUB_RUN_ID) if owner.json exists.

Env (optional):
  CI_LOCK_TIMEOUT_S   (default: 7200)
  CI_LOCK_STALE_TTL_S (default: 43200)
EOF
}

resolve_lock_dir() {
  local input_dir="$1"
  if [[ -z "${input_dir}" ]]; then
    echo "lock dir is empty" >&2
    exit 2
  fi
  if [[ "${input_dir}" = /* ]]; then
    printf '%s' "${input_dir}"
  else
    printf '%s' "${HOME}/${input_dir}"
  fi
}

stat_mtime_epoch() {
  local path="$1"

  # macOS/BSD: stat -f %m
  if stat -f %m "${path}" >/dev/null 2>&1; then
    stat -f %m "${path}" 2>/dev/null || true
    return 0
  fi

  # GNU/Linux: stat -c %Y
  if stat -c %Y "${path}" >/dev/null 2>&1; then
    stat -c %Y "${path}" 2>/dev/null || true
    return 0
  fi

  echo ""
}

write_github_env() {
  local key="$1"
  local value="$2"
  if [[ -n "${GITHUB_ENV:-}" ]]; then
    echo "${key}=${value}" >> "${GITHUB_ENV}"
  else
    echo "${key}=${value}"
  fi
}

acquire_lock() {
  local lock_dir
  lock_dir="$(resolve_lock_dir "$1")"

  mkdir -p "$(dirname "${lock_dir}")"

  echo "Acquiring lock: ${lock_dir}"
  local start_epoch
  start_epoch="$(date +%s)"

  local timeout_s stale_ttl_s
  timeout_s="${CI_LOCK_TIMEOUT_S:-7200}"
  stale_ttl_s="${CI_LOCK_STALE_TTL_S:-43200}"

  while ! mkdir "${lock_dir}" 2>/dev/null; do
    local owner_file mtime now_epoch age_s waited
    owner_file="${lock_dir}/owner.json"
    mtime=""

    if [[ -f "${owner_file}" ]]; then
      mtime="$(stat_mtime_epoch "${owner_file}")"
    fi
    if [[ -z "${mtime}" ]]; then
      mtime="$(stat_mtime_epoch "${lock_dir}")"
    fi

    if [[ -n "${mtime}" && "${mtime}" =~ ^[0-9]+$ ]]; then
      now_epoch="$(date +%s)"
      age_s=$(( now_epoch - mtime ))
      if (( age_s > stale_ttl_s )); then
        echo "Stale lock detected (age=${age_s}s > ttl=${stale_ttl_s}s). Removing: ${lock_dir}"
        rm -f "${owner_file}" || true
        rmdir "${lock_dir}" 2>/dev/null || true
      fi
    fi

    now_epoch="$(date +%s)"
    waited=$(( now_epoch - start_epoch ))
    if (( waited > timeout_s )); then
      echo "Timed out waiting for lock after ${waited}s: ${lock_dir}" >&2
      ls -la "${lock_dir}" || true
      exit 1
    fi

    echo "Lock is held by another job; waiting... (${waited}s)"
    sleep 15
  done

  local acquired_epoch
  acquired_epoch="$(date +%s)"

  cat > "${lock_dir}/owner.json" <<EOF
{
  "repo": "${GITHUB_REPOSITORY:-}",
  "run_id": "${GITHUB_RUN_ID:-}",
  "run_attempt": "${GITHUB_RUN_ATTEMPT:-}",
  "workflow": "${GITHUB_WORKFLOW:-}",
  "job": "${GITHUB_JOB:-}",
  "acquired_at_epoch": "${acquired_epoch}"
}
EOF

  write_github_env "CI_LOCK_DIR" "${lock_dir}"
  echo "Lock acquired."
}

release_lock() {
  local lock_dir
  lock_dir="$(resolve_lock_dir "$1")"

  if [[ ! -d "${lock_dir}" ]]; then
    echo "Lock directory not found; skipping release: ${lock_dir}"
    exit 0
  fi

  local owner_file
  owner_file="${lock_dir}/owner.json"

  # Only release if the lock looks like ours.
  if [[ -f "${owner_file}" ]]; then
    if command -v python3 >/dev/null 2>&1; then
      if ! LOCK_DIR="${lock_dir}" python3 - <<'PY'
import json
import os
import sys

lock_dir = os.environ["LOCK_DIR"]
run_id = os.environ.get("GITHUB_RUN_ID")
try:
    with open(os.path.join(lock_dir, "owner.json"), "r", encoding="utf-8") as f:
        owner = json.load(f)
except Exception:
    sys.exit(0)

if run_id is None or run_id == "":
    sys.exit(0)

sys.exit(0 if str(owner.get("run_id")) == str(run_id) else 3)
PY
      then
        echo "Lock is not owned by this run; skipping release."
        exit 0
      fi
    else
      echo "python3 not found; skipping ownership check and leaving lock in place." >&2
      exit 0
    fi
  fi

  rm -f "${owner_file}" || true
  rmdir "${lock_dir}" 2>/dev/null || true
  echo "Released lock: ${lock_dir}"
}

main() {
  if [[ $# -lt 1 ]]; then
    usage >&2
    exit 2
  fi

  local cmd="$1"
  shift || true

  case "${cmd}" in
    -h|--help|help)
      usage
      exit 0
      ;;
    acquire)
      if [[ $# -lt 1 ]]; then
        usage >&2
        exit 2
      fi
      acquire_lock "$1"
      ;;
    release)
      if [[ $# -lt 1 ]]; then
        usage >&2
        exit 2
      fi
      release_lock "$1"
      ;;
    *)
      echo "Unknown command: ${cmd}" >&2
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
