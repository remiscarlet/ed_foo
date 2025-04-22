import gzip
import os
import shutil
from pathlib import Path

import requests  # type: ignore
from requests.adapters import HTTPAdapter, Retry  # type: ignore
from tqdm import tqdm  # type: ignore


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
    os.replace(temp_path, dest_path)


def ungzip(in_path: Path, out_path: Path, delete: bool = True) -> None:
    with gzip.open(in_path, "rb") as f_in:
        with out_path.open("wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    if delete:
        in_path.unlink()
