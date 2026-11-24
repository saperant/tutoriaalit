################################################################
#
# minit
#
################################################################

MINIT_VERSION = 1.0
MINIT_SITE = $(BR2_EXTERNAL_TUT_PATH)/../../03-palvelut
MINIT_SITE_METHOD = local
MINIT_LICENSE = CC-BY-SA-4.0

define MINIT_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) \
		$(@D)/minit.c -o $(@D)/minit
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) \
		$(@D)/palvelu.c -o $(@D)/palvelu
endef

define MINIT_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/minit $(TARGET_DIR)/sbin/minit
	$(INSTALL) -D -m 0755 $(@D)/palvelu $(TARGET_DIR)/sbin/palvelu
	$(INSTALL) -D -m 0644 $(@D)/palvelut.conf \
		$(TARGET_DIR)/etc/palvelut.conf
endef

$(eval $(generic-package))
