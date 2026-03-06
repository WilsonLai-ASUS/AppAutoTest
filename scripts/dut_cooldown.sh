#!/usr/bin/env bash
set -euo pipefail

mode="${1:-}"

if [[ -z "${mode}" ]]; then
  echo "Usage: $0 <wait|mark|cooldown>" >&2
  exit 2
fi

DUT="${DUT:-}"
COOLDOWN_S="${COOLDOWN_S:-300}"
STATE_DIR="${STATE_DIR:-$HOME/.mobile-e2e}"

if [[ -z "${DUT}" ]]; then
  echo "DUT is required (env DUT)" >&2
  exit 2
fi

mkdir -p "${STATE_DIR}"
STATE_FILE="${STATE_DIR}/dut_${DUT}_last_finished_epoch"

case "${mode}" in
  wait)
    now=$(date +%s)
    last=0
    if [[ -f "${STATE_FILE}" ]]; then
      last=$(cat "${STATE_FILE}" || echo 0)
    fi

    if [[ "${last}" =~ ^[0-9]+$ ]]; then
      elapsed=$(( now - last ))
      if (( elapsed < COOLDOWN_S )); then
        wait_s=$(( COOLDOWN_S - elapsed ))
        echo "DUT ${DUT} cooling down: waiting ${wait_s}s (elapsed=${elapsed}s)"
        sleep "${wait_s}"
      else
        echo "DUT ${DUT} cooldown OK (elapsed=${elapsed}s)"
      fi
    else
      echo "Invalid last-finished timestamp in ${STATE_FILE}; ignoring" >&2
    fi
    ;;

  mark)
    echo "Marking DUT ${DUT} finished time"
    date +%s > "${STATE_FILE}"
    ;;

  cooldown)
    echo "Marking DUT ${DUT} finished time and cooling down for ${COOLDOWN_S}s"
    date +%s > "${STATE_FILE}"
    sleep "${COOLDOWN_S}"
    ;;

  *)
    echo "Unknown mode: ${mode}. Expected wait, mark, or cooldown" >&2
    exit 2
    ;;
esac
