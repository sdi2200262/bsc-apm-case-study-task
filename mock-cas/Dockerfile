# syntax=docker/dockerfile:1
FROM python:3.12-alpine

LABEL org.opencontainers.image.title="bsc-mock-cas"
LABEL org.opencontainers.image.description="Mock CAS authentication service for the BSc Thesis Case Study testing environment."
LABEL org.opencontainers.image.licenses="GPL-3.0-or-later"

WORKDIR /opt/mock-cas

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

ENV MOCK_CAS_CONFIG=/etc/mock-cas/cas-config.json \
    MOCK_CAS_PORT=8082

EXPOSE 8082

CMD ["python", "-m", "mock_cas.server"]
