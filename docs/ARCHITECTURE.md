# Architecture

The participant testing environment runs three services in one Docker Compose stack under the pinned project name `eclass-env`. Container names are deterministic regardless of install path: `eclass-env-db-1`, `eclass-env-eclass-1`, `eclass-env-sso-1`.

## Services

### `db`

MariaDB 10.11 from the upstream multi-arch image. Holds the openeclass database; the named volume `db_data` persists database state across `down`/`up` cycles. The healthcheck queries the configured database; `eclass` waits on this healthcheck before starting.

### `eclass`

Open eClass platform from upstream gunet, built into a local image (`bsc-mock/openeclass:dev`) at release-prep time. Pinned to a specific upstream commit per release. Exposes port 80 on the host. Three named volumes (`config_data`, `courses_data`, `video_data`) preserve runtime state.

The image is exactly the upstream platform; no sidecars are baked in, and image identity does not diverge from the pinned commit.

### `sso`

Mock authentication service. Custom image (`bsc-mock/mock-cas:dev`) built from the `mock-cas/` source in this repository. Implements the Apereo CAS / SAML 1.1 surface that the [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) reference client expects against the University of Athens deployment. Exposes port 8082 on the host with self-signed TLS; the certificates live under `<prefix>/certs/` and are mounted read-only into the container.

The mock identifies itself as a mock to inspecting agents through page copy, the `Server: bsc-mock-cas` response header, and inline XML comments inside CAS and SAML responses.

## Network

The three services share the default bridge network the Compose stack creates. The eclass container reaches the mock authentication service through the docker bridge gateway IP `172.17.0.1` on port 8082; this matches the seeded `auth_settings` row inside the openeclass database.

The host reaches:

- `http://localhost/` (port 80) for the openeclass UI and API.
- `https://172.17.0.1:8082/` for the mock authentication service.

## Environment variables consumed by the participant's MCP server

The reference client at [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) reads the following environment variables. The values below are correct when the MCP server runs on the host machine and the testing environment is up:

| Variable | Value |
|---|---|
| `ECLASS_URL` | `http://localhost` |
| `ECLASS_USERNAME` | matches `seed/seed.yaml`'s `user.username` |
| `ECLASS_PASSWORD` | matches `seed/seed.yaml`'s `user.cas_password` |
| `ECLASS_SSO_DOMAIN` | `172.17.0.1:8082` |
| `ECLASS_SSO_PROTOCOL` | `https` |
| `SSL_CERT_FILE` | `<prefix>/certs/sso_cert.pem` |
| `REQUESTS_CA_BUNDLE` | `<prefix>/certs/sso_cert.pem` |
| `CURL_CA_BUNDLE` | `<prefix>/certs/sso_cert.pem` |
| `PYTHONHTTPSVERIFY` | `0` |

The grading machine sets these from its resolved `mock_root` path; participants set them in their MCP server's `.env` (the participant guide carries the concrete values once the seed data is finalised).
