# record.py

"""
Record utility for taking screenshots and recording videos during tests.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time
from datetime import datetime

from .logger import logger


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def _has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _write_ffmpeg_concat_file(list_path: str, segment_paths: list[str]) -> None:
    with open(list_path, "w", encoding="utf-8") as f:
        for p in segment_paths:
            # ffmpeg concat demuxer format
            escaped = p.replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")


def _validate_video_with_ffmpeg(video_path: str) -> bool:
    """Best-effort validation that ffmpeg can demux/decode the file."""
    try:
        proc = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                video_path,
                "-f",
                "null",
                "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _stitch_with_ffmpeg_concat(
    list_path: str, stitched_path: str, *, reencode: bool
) -> subprocess.CompletedProcess[str]:
    if reencode:
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_path,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            stitched_path,
        ]
    else:
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_path,
            "-c",
            "copy",
            stitched_path,
        ]

    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class Record:
    dir = None

    def __init__(self):
        self._lock = threading.Lock()
        self._active = False
        self._stop_event: threading.Event | None = None
        self._thread: threading.Thread | None = None
        self._segment_paths: list[str] = []
        self._session_suffix: str = "recording"
        self._session_ts: str = ""
        self._rotate_every_s: float = 170.0
        self._stitch: bool = True
        self._segment_started_at: float | None = None

        # Output directories (optional). If not set, fall back to `dir` then "reports".
        self.screenshots_dir: str | None = None
        self.videos_dir: str | None = None

    def set_dirs(
        self, *, screenshots_dir: str | None = None, videos_dir: str | None = None
    ):
        if screenshots_dir is not None:
            self.screenshots_dir = screenshots_dir
        if videos_dir is not None:
            self.videos_dir = videos_dir

    def _base_dir_for(self, kind: str) -> str:
        if kind == "screenshots":
            base = self.screenshots_dir
        elif kind == "videos":
            base = self.videos_dir
        else:
            base = None

        if not base:
            base = self.dir
        if not base:
            base = "reports"
        return _ensure_dir(str(base))

    def _filepath_for(self, kind: str, suffix: str, extension: str) -> str:
        base_dir = self._base_dir_for(kind)
        if kind == "screenshots":
            name = f"{self.timestamp()}_{suffix}.{extension}"
        else:
            name = f"{suffix}.{extension}"
        return self._dedupe_filepath(os.path.join(base_dir, name))

    def _dedupe_filepath(self, path: str) -> str:
        if not os.path.exists(path):
            return path

        base, ext = os.path.splitext(path)
        for i in range(2, 10_000):
            candidate = f"{base}_{i}{ext}"
            if not os.path.exists(candidate):
                return candidate

        # Extremely unlikely; fall back to timestamp.
        return f"{base}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}{ext}"

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d_%H%M%S")

    def filename(self, suffix):
        # Backward compatibility: keep old naming behavior for generic callers.
        return f"{self.timestamp()}_{suffix}"

    def filepath(self, suffix, extension):
        if not self.dir:
            self.dir = "reports"
        base_dir = _ensure_dir(str(self.dir))
        return os.path.join(base_dir, f"{self.filename(suffix)}.{extension}")

    def screenshot(self, suffix="screenshot"):
        from .driver import driver

        if driver.is_exist():
            filepath = self._filepath_for("screenshots", suffix, "png")
            driver.save_screenshot(filepath=filepath)
            logger.info("Screenshot saved: %s", filepath)
        else:
            logger.warn("Driver not initialized, cannot take screenshot.")

    def start_recording(
        self,
        *,
        suffix: str = "recording",
        rotate_every_s: float = 170.0,
        stitch: bool = True,
    ):
        from .driver import driver

        if not driver.is_exist():
            logger.warn("Driver not initialized, cannot start recording.")
            return

        with self._lock:
            if self._active:
                return

            self._active = True
            self._segment_paths = []
            self._session_suffix = suffix
            self._session_ts = self.timestamp()
            self._rotate_every_s = max(30.0, float(rotate_every_s))
            self._stitch = bool(stitch)

            self._stop_event = threading.Event()
            self._thread = threading.Thread(
                target=self._rotation_loop,
                name="RecordRotation",
                daemon=True,
            )

            # Start first segment immediately.
            # IMPORTANT: Don't set timeLimit == rotate_every_s.
            # If rotation happens right as Appium auto-stops, segments can miss the moov atom.
            time_limit_s = int(round(min(180.0, self._rotate_every_s + 30.0)))
            time_limit_s = max(30, time_limit_s)
            driver.start_recording_screen(time_limit_s=time_limit_s)
            self._segment_started_at = time.monotonic()
            logger.info("Started screen recording (segmented mode).")
            self._thread.start()

    def stop_recording(self, suffix: str | None = None):
        from .driver import driver

        if not driver.is_exist():
            logger.warn("Driver not initialized, cannot stop recording.")
            return

        with self._lock:
            if not self._active:
                return

            if suffix is not None:
                self._session_suffix = suffix

            if self._stop_event is not None:
                self._stop_event.set()

            thread = self._thread
        if thread is not None:
            thread.join(timeout=10)

        # Save final segment
        self._save_segment(driver, is_final=True)

        # Final output path (always keep a single file)
        stitched_path = self._filepath_for("videos", self._session_suffix, "mp4")
        segment_paths = list(self._segment_paths)

        with self._lock:
            self._active = False
            self._thread = None
            self._stop_event = None

        if not segment_paths:
            logger.warn("No recording segments captured.")
            return

        def _keep_single_video_fallback() -> None:
            existing = [p for p in segment_paths if os.path.exists(p)]
            if not existing:
                logger.warn("No recording segment files exist on disk.")
                return

            # Keep the last segment and rename it to the final output name.
            keep_path = existing[-1]
            try:
                if os.path.abspath(keep_path) != os.path.abspath(stitched_path):
                    # If the destination already exists (dedupe should avoid, but be safe), remove it.
                    if os.path.exists(stitched_path):
                        os.remove(stitched_path)
                    os.replace(keep_path, stitched_path)
                    keep_path = stitched_path
            except Exception as e:
                logger.warn("Failed to rename final segment to %s: %s", stitched_path, e)
                keep_path = existing[-1]

            removed = 0
            for p in segment_paths:
                if p == keep_path:
                    continue
                try:
                    if os.path.exists(p):
                        os.remove(p)
                        removed += 1
                except Exception as e:
                    logger.warn("Failed to delete segment %s: %s", p, e)

            logger.info("Screen recording saved (single file): %s", keep_path)
            if removed:
                logger.info("Deleted %d temporary recording segments.", removed)

        if self._stitch and _has_ffmpeg() and len(segment_paths) >= 2:
            missing = [p for p in segment_paths if not os.path.exists(p)]
            if missing:
                logger.warn(
                    "ffmpeg stitching skipped; missing %d segment(s). Keeping segments in: %s",
                    len(missing),
                    os.path.dirname(segment_paths[0]),
                )
                _keep_single_video_fallback()
                return

            base_dir = os.path.dirname(stitched_path)
            list_path = self._dedupe_filepath(
                os.path.join(base_dir, f"{self._session_suffix}_concat.txt")
            )
            _write_ffmpeg_concat_file(list_path, segment_paths)
            try:
                proc = _stitch_with_ffmpeg_concat(
                    list_path, stitched_path, reencode=False
                )
                stitched_ok = (
                    proc.returncode == 0
                    and os.path.exists(stitched_path)
                    and os.path.getsize(stitched_path) > 0
                    and _validate_video_with_ffmpeg(stitched_path)
                )

                if not stitched_ok:
                    logger.warn(
                        "ffmpeg stream-copy stitching failed; retrying with re-encode..."
                    )
                    proc2 = _stitch_with_ffmpeg_concat(
                        list_path, stitched_path, reencode=True
                    )
                    stitched_ok = (
                        proc2.returncode == 0
                        and os.path.exists(stitched_path)
                        and os.path.getsize(stitched_path) > 0
                        and _validate_video_with_ffmpeg(stitched_path)
                    )
                    if not stitched_ok:
                        proc = proc2

                if stitched_ok:
                    logger.info("Screen recording stitched: %s", stitched_path)

                    removed = 0
                    for p in segment_paths:
                        try:
                            if os.path.exists(p):
                                os.remove(p)
                                removed += 1
                        except Exception as e:
                            logger.warn("Failed to delete segment %s: %s", p, e)
                    try:
                        if os.path.exists(list_path):
                            os.remove(list_path)
                    except Exception as e:
                        logger.warn("Failed to delete concat list %s: %s", list_path, e)
                    logger.info("Deleted %d temporary recording segments.", removed)
                    return

                details = (proc.stderr or "").strip()
                if details:
                    logger.warn("ffmpeg stitching failed; ffmpeg said: %s", details)
                else:
                    logger.warn("ffmpeg stitching failed (rc=%s).", proc.returncode)
                # Always keep only one video even if stitching fails.
                try:
                    if os.path.exists(list_path):
                        os.remove(list_path)
                except Exception:
                    pass
                _keep_single_video_fallback()
                return
            except Exception as e:
                logger.warn("ffmpeg stitching exception: %s", e)
                try:
                    if os.path.exists(list_path):
                        os.remove(list_path)
                except Exception:
                    pass
                _keep_single_video_fallback()
                return

        # If we didn't stitch (ffmpeg missing / stitch disabled / only 1 segment), keep a single file.
        _keep_single_video_fallback()

    def _segment_path(self, index: int) -> str:
        base_dir = self._base_dir_for("videos")
        name = f"{self._session_suffix}_part{index:04d}.mp4"
        return self._dedupe_filepath(os.path.join(base_dir, name))

    def _save_segment(self, driver, *, is_final: bool) -> None:
        try:
            segment_path = self._segment_path(len(self._segment_paths) + 1)
            ok = driver.stop_recording_screen(filepath=segment_path)
            if ok:
                self._segment_paths.append(segment_path)
                logger.info(
                    "Saved recording segment%s: %s",
                    " (final)" if is_final else "",
                    segment_path,
                )
            else:
                logger.warn(
                    "Failed to save recording segment%s",
                    " (final)" if is_final else "",
                )
        except Exception as e:
            logger.warn(
                "Exception while saving recording segment%s: %s",
                " (final)" if is_final else "",
                e,
            )

    def _rotation_loop(self) -> None:
        from .driver import driver

        # Rotate based on the actual time the current segment started.
        started_at = self._segment_started_at or time.monotonic()
        next_rotate = started_at + self._rotate_every_s

        while True:
            stop_event = self._stop_event
            if stop_event is not None and stop_event.is_set():
                return

            now = time.monotonic()
            sleep_s = max(0.05, min(0.5, next_rotate - now))
            time.sleep(sleep_s)

            if time.monotonic() < next_rotate:
                continue

            with self._lock:
                if not self._active:
                    return

            # Rotate: stop/save current segment then immediately start a new one.
            self._save_segment(driver, is_final=False)

            # Small settle time before starting a new recording.
            # This reduces flakiness where segments are missing the moov atom.
            stop_event = self._stop_event
            if stop_event is not None and stop_event.wait(timeout=0.25):
                return

            try:
                time_limit_s = int(round(min(180.0, self._rotate_every_s + 30.0)))
                time_limit_s = max(30, time_limit_s)
                driver.start_recording_screen(time_limit_s=time_limit_s)
                self._segment_started_at = time.monotonic()
            except Exception as e:
                logger.warn("Failed to start next recording segment: %s", e)

            started_at = self._segment_started_at or time.monotonic()
            next_rotate = started_at + self._rotate_every_s


# Singleton
record = Record()
