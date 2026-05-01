#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) BSc APM Case Study 2025-2026
"""Runtime configuration loader for the mock CAS service.

Reads a JSON configuration file describing the single mock test user and
the runtime parameters of the service. When the configuration file is
absent, built-in defaults are returned so the service is runnable
without a mounted config file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG_PATH = "/etc/mock-cas/cas-config.json"


@dataclass(frozen=True)
class Config:
    """Runtime configuration for the mock CAS service.

    Attributes:
        username: The single mock test user's username.
        password: Plaintext password the user submits at the CAS form.
        display_name: Human-readable display name returned as a CAS attribute.
        email: Email attribute returned in CAS and SAML assertions.
        givenname: Given-name attribute returned in CAS and SAML assertions.
        surname: Surname attribute returned in CAS and SAML assertions.
        studentid: Student-id attribute returned in CAS and SAML assertions.
        port: The TCP port the service binds to.
        cert_path: Path to the TLS certificate file mounted into the image.
        key_path: Path to the TLS private-key file mounted into the image.
        bridge_subnet: CIDR for /admin/reset source-IP gating.
    """

    username: str
    password: str
    display_name: str
    email: str
    givenname: str
    surname: str
    studentid: str
    port: int = 8082
    cert_path: str = "/etc/mock-cas/certs/sso_cert.pem"
    key_path: str = "/etc/mock-cas/certs/sso_key.pem"
    bridge_subnet: str = "172.16.0.0/12"


_DEFAULTS = Config(
    username="student1",
    password="mockpass123",
    display_name="Demo Student",
    email="student1@example.edu",
    givenname="Demo",
    surname="Student",
    studentid="STU0001",
)


def load_config(path: str | None = None) -> Config:
    """Load the runtime configuration.

    Args:
        path: Path to the JSON config file. Falls back to the value of the
            ``MOCK_CAS_CONFIG`` environment variable, then to
            ``DEFAULT_CONFIG_PATH``. If the resolved path does not exist,
            the built-in defaults are returned and the caller can run the
            service standalone.

    Returns:
        A populated :class:`Config` instance.

    Raises:
        ValueError: If the JSON file is present but cannot be parsed or is
            missing required fields.
    """
    import os

    resolved = path or os.environ.get("MOCK_CAS_CONFIG") or DEFAULT_CONFIG_PATH
    file_path = Path(resolved)
    if not file_path.is_file():
        return _DEFAULTS

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"mock CAS config at {file_path} is not valid JSON: {exc}") from exc

    try:
        return Config(**data)
    except TypeError as exc:
        raise ValueError(
            f"mock CAS config at {file_path} is missing required fields: {exc}"
        ) from exc
