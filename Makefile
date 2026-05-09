# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) BSc APM Case Study 2025-2026
#
# Release-prep targets for the BSc APM Case Study testing environment
# and participant package.
#
# Targets:
#   seed                 Regenerate seed/seed.json and mock-cas/cas-config.json from seed/seed.yaml.
#   build-images         Build the openeclass and mock CAS images.
#   save-images          Save both images to release/<image>-<arch>.tar.
#   release              Assemble the testing environment release tarball at release/bsc-apm-<arch>.tar.gz.
#   participant-guide    Build the participant guide PDF.
#   participant-package  Assemble the participant package zip at release/participant-package.zip.
#   clean                Remove the release/ directory.
#   help                 Print this listing.

ARCH ?= $(shell uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
OPENECLASS_PATH ?= ../openeclass
OPENECLASS_REF ?= Release_4.3.3
RELEASE_DIR ?= release
TESTBED_STAGING_DIR = $(RELEASE_DIR)/staging-testbed
PACKAGE_STAGING_DIR = $(RELEASE_DIR)/staging-package

OPENECLASS_TAG = bsc-apm/openeclass:dev
MOCK_CAS_TAG = bsc-apm/mock-cas:dev

OPENECLASS_TAR = $(RELEASE_DIR)/openeclass-image-$(ARCH).tar
MOCK_CAS_TAR = $(RELEASE_DIR)/mock-cas-image-$(ARCH).tar
RELEASE_TARBALL = $(RELEASE_DIR)/bsc-apm-$(ARCH).tar.gz

UV ?= uv

GUIDE_DIR = participant/guide
GUIDE_TEX = participant-guide-cc.tex
GUIDE_PDF = $(GUIDE_DIR)/participant-guide-cc.pdf
TASK_DIR = participant/task
SKILLS_DIR = participant/skills
RELEASE_ZIP = $(RELEASE_DIR)/participant-package.zip

LATEXMK ?= latexmk

.PHONY: help seed check-openeclass-ref build-images save-images release participant-guide participant-package clean

help:
	@echo "Available targets:"
	@echo "  seed                 regenerate seed/seed.json and mock-cas/cas-config.json"
	@echo "  build-images         build openeclass and mock CAS images"
	@echo "  save-images          save built images to release/*.tar"
	@echo "  release              assemble $(RELEASE_TARBALL)"
	@echo "  participant-guide    build $(GUIDE_PDF)"
	@echo "  participant-package  assemble $(RELEASE_ZIP)"
	@echo "  clean                remove $(RELEASE_DIR)/"
	@echo ""
	@echo "Variables:"
	@echo "  ARCH=$(ARCH)"
	@echo "  OPENECLASS_PATH=$(OPENECLASS_PATH)"
	@echo "  OPENECLASS_REF=$(OPENECLASS_REF)"
	@echo "  RELEASE_DIR=$(RELEASE_DIR)"

seed:
	$(UV) run --no-project seed/generate_seed_json.py
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
	@mkdir -p $(TESTBED_STAGING_DIR)/seed
	cp README.md LICENSE install compose.yaml $(TESTBED_STAGING_DIR)/
	cp -r scripts docs $(TESTBED_STAGING_DIR)/
	cp seed/seed.php seed/seed.json $(TESTBED_STAGING_DIR)/seed/
	cp $(OPENECLASS_TAR) $(MOCK_CAS_TAR) $(TESTBED_STAGING_DIR)/
	tar -czf $(RELEASE_TARBALL) -C $(TESTBED_STAGING_DIR) .
	rm -rf $(TESTBED_STAGING_DIR)
	@echo "release tarball: $(RELEASE_TARBALL)"

participant-guide:
	cd $(GUIDE_DIR) && $(LATEXMK) -pdf $(GUIDE_TEX)

participant-package: participant-guide
	rm -rf $(PACKAGE_STAGING_DIR)
	mkdir -p $(PACKAGE_STAGING_DIR)/participant-package/task
	cp $(GUIDE_PDF) $(PACKAGE_STAGING_DIR)/participant-package/
	cp $(TASK_DIR)/PRD.md $(PACKAGE_STAGING_DIR)/participant-package/task/
	cp $(TASK_DIR)/PROMPT.md $(PACKAGE_STAGING_DIR)/participant-package/task/
	cp $(TASK_DIR)/README.txt $(PACKAGE_STAGING_DIR)/participant-package/task/
	mkdir -p $(PACKAGE_STAGING_DIR)/participant-package/.claude
	cp -r $(SKILLS_DIR) $(PACKAGE_STAGING_DIR)/participant-package/.claude/skills
	rm -f $(RELEASE_ZIP)
	cd $(PACKAGE_STAGING_DIR) && zip -r ../$(notdir $(RELEASE_ZIP)) participant-package
	rm -rf $(PACKAGE_STAGING_DIR)
	@echo "wrote $(RELEASE_ZIP)"

clean:
	rm -rf $(RELEASE_DIR)
