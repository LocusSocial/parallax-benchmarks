#!/usr/bin/env python3
"""Export a reproducible result without exposing machine-specific local paths."""

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


def sanitized(body: bytes, source: Path) -> bytes:
    text = body.decode("utf-8", errors="replace")
    replacements = {
        str(source): "<run-root>",
        str(Path.home()): "<home>",
    }
    for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(old, new)
    text = re.sub(r"session id: [^\n]+", "session id: <redacted>", text)
    text = re.sub(r"(?:session_id|turn_id)=[^\s]+", "session_id=<redacted>", text)
    text = re.sub(
        r"\b01a[0-9a-f]{5,}-[0-9a-f-]{20,}\b", "<session-id>", text, flags=re.IGNORECASE
    )
    return text.encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"output already exists: {output}")
    output.mkdir(parents=True)

    for filename in ("before.json", "after.json", "prompt.md"):
        (output / filename).write_bytes(sanitized((source / filename).read_bytes(), source))
    shutil.copytree(
        source / "workspace",
        output / "workspace",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )

    transcript = sanitized((source / "transcript.log").read_bytes(), source)
    final_message = sanitized((source / "final-message.md").read_bytes(), source)
    (output / "transcript.log").write_bytes(transcript)
    (output / "final-message.md").write_bytes(final_message)

    metadata = json.loads((source / "metadata.json").read_text(encoding="utf-8"))
    metadata["command"] = [
        str(item).replace(str(source), "<run-root>").replace(str(Path.home()), "<home>")
        for item in metadata["command"]
    ]
    metadata["public_transcript_sha256"] = hashlib.sha256(transcript).hexdigest()
    metadata["raw_transcript_retained_privately"] = True
    (output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(output)


if __name__ == "__main__":
    main()
