#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025-2026
"""Generate the mock CAS runtime config from seed.yaml.

The output is a small JSON file holding the test user's credentials
and the attribute set the mock CAS returns inside its CAS and SAML
responses. The mock-cas Docker image bakes this file in at build time
through a COPY step in the Dockerfile.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
INPUT_PATH = HERE / "seed.yaml"
OUTPUT_PATH = HERE.parent / "mock-cas" / "cas-config.json"


def main() -> None:
    """Read seed.yaml, write mock-cas/cas-config.json."""
    if not INPUT_PATH.is_file():
        print(f"seed input not found: {INPUT_PATH}", file=sys.stderr)
        sys.exit(1)
    data = yaml.safe_load(INPUT_PATH.read_text(encoding="utf-8"))
    user = data["user"]

    config = {
        "username": user["username"],
        "password": user["cas_password"],
        "display_name": user["display_name"],
        "email": user["email"],
        "givenname": user["givenname"],
        "surname": user["surname"],
        "studentid": user["studentid"],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
