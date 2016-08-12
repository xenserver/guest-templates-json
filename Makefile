USE_BRANDING := yes
IMPORT_VERSIONS := yes
include $(B_BASE)/common.mk
include $(B_BASE)/rpmbuild.mk

PKG_VERSION := 1.0

REPO = $(call git_loc,guest-templates)
CSET_NUMBER := $(shell $(shell $(call git_cset_number,guest-templates)); echo $$CSET_NUMBER)

.PHONY: build
build: srpm
	$(RPMBUILD) --target $(DOMAIN0_ARCH_OPTIMIZED) -bb $(RPM_SPECSDIR)/guest-templates-new.spec

.PHONY: srpm
srpm: $(RPM_DIRECTORIES)
	cd $(REPO) && git archive --format=tar --prefix=guest-templates-new-$(PKG_VERSION)/ HEAD:json-templates/ \
		| bzip2 > $(RPM_SOURCESDIR)/guest-templates-new-$(PKG_VERSION).tar.bz2
	sed 's/@VERSION@/$(PKG_VERSION)/; s/@RELEASE@/$(CSET_NUMBER)/' < guest-templates-new.spec > $(RPM_SPECSDIR)/guest-templates-new.spec
	$(RPMBUILD) --target $(DOMAIN0_ARCH_OPTIMIZED) -bs $(RPM_SPECSDIR)/guest-templates-new.spec

.PHONY: clean
clean:
	rm -f $(OUTPUT)
	$(MAKE) -C $(REPO) clean
