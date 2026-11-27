"""Entrypoint: render the 26 November 2026 world-news image.

Writes one PNG summing up the day's news to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png when that is set). Pure standard
library; no network, no files read besides this repository's own code.
The output is deterministic: two runs write identical bytes.
"""

import os
import sys

# The grader runs `python3 -P -s /bot/main.py`: -P keeps the script's
# directory off sys.path, so a sibling `import draw` fails there even
# though it works in a plain run. Point sys.path at this file's own
# directory first so the sibling import resolves in both cases.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draw


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    draw.render(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
