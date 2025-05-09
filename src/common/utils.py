import gzip
import math
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter, Retry
from tqdm import tqdm


def download_file(url: str, dest_path: Path, chunk_size: int = 16_384) -> None:
    """
    Download a file with streaming, progress bar, and resume support.
    """
    # Temp file for partial downloads
    temp_path = dest_path.parent / (dest_path.name + ".part")

    # Determine where to resume from
    first_byte = os.path.getsize(temp_path) if os.path.exists(temp_path) else 0
    headers = {"Range": f"bytes={first_byte}-"} if first_byte else {}

    # Set up session with retries
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))

    # Stream the GET
    resp = session.get(url, headers=headers, stream=True, timeout=(5, 30))
    resp.raise_for_status()

    total_size = int(resp.headers.get("Content-Length", 0)) + first_byte
    mode = "ab" if first_byte else "wb"

    with (
        open(temp_path, mode) as f,
        tqdm(
            total=total_size,
            initial=first_byte,
            unit="B",
            unit_scale=True,
            desc=os.path.basename(dest_path),
        ) as bar,
    ):
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if not chunk:
                continue
            f.write(chunk)
            bar.update(len(chunk))

    # Move temp to final name once complete
    shutil.move(temp_path, dest_path)


def ungzip(in_path: Path, out_path: Path, delete: bool = True) -> None:
    with gzip.open(in_path, "rb") as f_in:
        with out_path.open("wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    if delete:
        in_path.unlink()


def get_time_since(dt: datetime) -> str:
    """Returns a string of weeks, days, hours since supplied `dt`
    Eg, timedelta(days=20, hours=5) => "2 Weeks, 6 Days, 5 Hours Ago"
        timedelta(days=1, hours=1) => "1 Week, 1 Hour Ago"
    """
    delta = datetime.now(timezone.utc) - dt

    days = delta.days
    seconds = delta.total_seconds() - (days * 24 * 60 * 60)
    hours = seconds // (60 * 60)
    config = {
        "Week": int(days // 7),
        "Day": int(days % 7),
        "Hour": int(hours),
    }

    parts = []
    for unit, num in config.items():
        if num > 0:
            part = f"{num} {unit}"
            if num > 1:
                part += "s"
            parts.append(part)

    time_since = ", ".join(parts)
    return f"{time_since} Ago"


def seconds_to_str(sec: float) -> str:
    """Returns a string of hours, minutes, seconds, etc by converting the delta
    Delta is assumed to be seconds
    """
    if not sec:
        return "0s"

    ms_str = f"{sec - math.trunc(sec):.3f}"
    ms_str_zero_truncated = ms_str[2:]  # Truncate the `0.` prefix on `0.56` etc
    s = int(sec % 60)
    m = int(sec // 60) % 60
    h = int(sec // (60 * 60)) % (60 * 60)

    config = {
        "h": h,
        "m": m,
        "s": s,
        "ms": ms_str_zero_truncated,
    }

    parts = []
    for sym, val in config.items():
        if val:
            parts.append(f"{val}{sym}")

    return "".join(parts)
