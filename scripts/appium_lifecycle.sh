#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  appium_lifecycle.sh ensure [--port 4723] [--base-path /] [--log appium.log]
  appium_lifecycle.sh stop   [--pid <pid>] [--wait 10]

Behavior:
- ensure:
  - If the port is already listening, outputs: started=false, was_running=true, pid=<listener pid>
  - If Appium is not installed, outputs: started=false, was_running=false, pid=
  - Otherwise starts Appium in background (nohup) and outputs: started=true, was_running=false, pid=<appium pid>

Outputs (GitHub Actions):
  Writes started/was_running/pid to $GITHUB_OUTPUT when available.
USAGE
}

write_output() {
  local key="$1"
  local value="$2"
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    echo "${key}=${value}" >> "${GITHUB_OUTPUT}"
  else
    # Fallback for local debugging
    echo "${key}=${value}"
  fi
}

is_listening() {
  local port="$1"
  lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
}

listener_pid() {
  local port="$1"
  lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null | head -1 || true
}

cmd="${1:-}"
shift || true

port="4723"
base_path="/"
log_file="appium.log"
wait_s="30"
pid=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      port="$2"; shift 2;;
    --base-path)
      base_path="$2"; shift 2;;
    --log)
      log_file="$2"; shift 2;;
    --pid)
      pid="$2"; shift 2;;
    --wait)
      wait_s="$2"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2;;
  esac
done

case "${cmd}" in
  ensure)
    write_output started false
    write_output was_running false
    write_output pid ""

    if is_listening "${port}"; then
      write_output was_running true
      write_output pid "$(listener_pid "${port}")"
      exit 0
    fi

    if ! command -v appium >/dev/null 2>&1; then
      echo "appium command not found; assuming Appium is managed outside the workflow" >&2
      exit 0
    fi

    echo "Starting Appium server on :${port} (base-path=${base_path})" >&2
    nohup appium --port "${port}" --base-path "${base_path}" --log-no-colors --log-timestamp > "${log_file}" 2>&1 &
    pid="$!"

    write_output started true
    write_output pid "${pid}"

    # Wait for the socket to be available. Driver loading can take a few seconds,
    # so poll up to wait_s seconds instead of a fixed sleep.
    for _ in $(seq 1 "${wait_s}"); do
      if is_listening "${port}"; then
        exit 0
      fi
      sleep 1
    done

    echo "Appium failed to listen on :${port} within ${wait_s}s" >&2
    if [[ -f "${log_file}" ]]; then
      echo "=== tail -n 200 ${log_file} ===" >&2
      tail -n 200 "${log_file}" >&2 || true
      echo "=== end tail ${log_file} ===" >&2
    fi
    exit 2
    ;;

  stop)
    if [[ -z "${pid}" ]]; then
      echo "No PID provided; skip stopping." >&2
      exit 0
    fi

    if ! kill -0 "${pid}" >/dev/null 2>&1; then
      echo "PID ${pid} is not running; skip." >&2
      exit 0
    fi

    echo "Stopping Appium PID ${pid}" >&2
    kill -TERM "${pid}" || true

    # Wait up to wait_s seconds for graceful shutdown
    for _ in $(seq 1 "${wait_s}"); do
      if ! kill -0 "${pid}" >/dev/null 2>&1; then
        echo "Appium stopped." >&2
        exit 0
      fi
      sleep 1
    done

    echo "Appium did not stop in time; forcing kill." >&2
    kill -KILL "${pid}" || true
    ;;

  *)
    usage
    exit 2
    ;;
esac
