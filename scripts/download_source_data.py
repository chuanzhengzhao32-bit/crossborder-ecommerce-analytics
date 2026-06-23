"""Download and verify the UCI Online Retail II source workbook."""

from __future__ import annotations

import hashlib
import shutil
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
ZIP_PATH = RAW_DIR / "online_retail_ii.zip"
EXTRACT_DIR = RAW_DIR / "uci_online_retail_ii"
SOURCE_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
EXPECTED_SHA256 = "572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not ZIP_PATH.exists():
        print(f"Downloading {SOURCE_URL}")
        with urllib.request.urlopen(SOURCE_URL) as response, ZIP_PATH.open("wb") as output:
            shutil.copyfileobj(response, output)

    actual_hash = sha256(ZIP_PATH)
    if actual_hash != EXPECTED_SHA256:
        raise RuntimeError(
            f"Source checksum mismatch: expected {EXPECTED_SHA256}, got {actual_hash}"
        )

    workbook_path = EXTRACT_DIR / "online_retail_II.xlsx"
    if not workbook_path.exists():
        EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(ZIP_PATH) as archive:
            archive.extractall(EXTRACT_DIR)

    print(f"Verified archive: {ZIP_PATH}")
    print(f"SHA-256: {actual_hash}")
    print(f"Workbook: {workbook_path}")


if __name__ == "__main__":
    main()

