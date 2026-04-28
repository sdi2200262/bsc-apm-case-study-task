# Release-prep targets for the BSc APM Case Study testing environment.
#
# Targets:
#   seed          Regenerate seed/seed.sql and mock-cas/cas-config.json from seed/seed.yaml.
#   build-images  Build the openeclass and mock CAS images.
#   save-images   Save both images to release/<image>-<arch>.tar.
#   release       Assemble the GitHub release tarball at release/bsc-apm-<arch>.tar.gz.
#   clean         Remove the release/ directory.
#   help          Print this listing.

ARCH ?= $(shell uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
OPENECLASS_PATH ?= ../openeclass
OPENECLASS_REF ?= Release_4.3.3
RELEASE_DIR ?= release
STAGING_DIR = $(RELEASE_DIR)/staging

OPENECLASS_TAG = bsc-apm/openeclass:dev
MOCK_CAS_TAG = bsc-apm/mock-cas:dev

OPENECLASS_TAR = $(RELEASE_DIR)/openeclass-image-$(ARCH).tar
MOCK_CAS_TAR = $(RELEASE_DIR)/mock-cas-image-$(ARCH).tar
RELEASE_TARBALL = $(RELEASE_DIR)/bsc-apm-$(ARCH).tar.gz

UV ?= uv

.PHONY: help seed check-openeclass-ref build-images save-images release clean

help:
	@echo "Available targets:"
	@echo "  seed          regenerate seed/seed.sql and mock-cas/cas-config.json"
	@echo "  build-images  build openeclass and mock CAS images"
	@echo "  save-images   save built images to release/*.tar"
	@echo "  release       assemble $(RELEASE_TARBALL)"
	@echo "  clean         remove $(RELEASE_DIR)/"
	@echo ""
	@echo "Variables:"
	@echo "  ARCH=$(ARCH)"
	@echo "  OPENECLASS_PATH=$(OPENECLASS_PATH)"
	@echo "  OPENECLASS_REF=$(OPENECLASS_REF)"
	@echo "  RELEASE_DIR=$(RELEASE_DIR)"

seed:
	$(UV) run --no-project seed/generate_sql.py
	$(UV) run --no-project seed/generate_cas_config.py

check-openeclass-ref:
	@actual=$$(git -C $(OPENECLASS_PATH) rev-parse HEAD); \
	expected=$$(git -C $(OPENECLASS_PATH) rev-parse $(OPENECLASS_REF)); \
	if [ "$$actual" != "$$expected" ]; then \
	  echo "openeclass at $(OPENECLASS_PATH) is not at $(OPENECLASS_REF)"; \
	  echo "  expected: $$expected"; \
	  echo "  actual:   $$actual"; \
	  echo "run: git -C $(OPENECLASS_PATH) checkout $(OPENECLASS_REF)"; \
	  exit 1; \
	fi

build-images: check-openeclass-ref
	docker build -t $(OPENECLASS_TAG) $(OPENECLASS_PATH)
	docker build -t $(MOCK_CAS_TAG) mock-cas/

save-images: build-images
	@mkdir -p $(RELEASE_DIR)
	docker save $(OPENECLASS_TAG) -o $(OPENECLASS_TAR)
	docker save $(MOCK_CAS_TAG) -o $(MOCK_CAS_TAR)

release: seed save-images
	@mkdir -p $(STAGING_DIR)/seed
	cp README.md LICENSE install compose.yaml $(STAGING_DIR)/
	cp -r scripts docs $(STAGING_DIR)/
	cp seed/seed.sql $(STAGING_DIR)/seed/
	cp $(OPENECLASS_TAR) $(MOCK_CAS_TAR) $(STAGING_DIR)/
	tar -czf $(RELEASE_TARBALL) -C $(STAGING_DIR) .
	rm -rf $(STAGING_DIR)
	@echo "release tarball: $(RELEASE_TARBALL)"

clean:
	rm -rf $(RELEASE_DIR)
