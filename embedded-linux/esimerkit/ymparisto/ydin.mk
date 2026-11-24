# Uudelleenkäytettävä ARM64-ytimen rakennus QEMU:n virt-koneelle.
#
# Ota mukaan omasta Makefilestä:
#
#   include polku/ymparisto/ydin.mk
#   kohde: $(IMAGE)              # ydin, Image-muodossa
#
# Muuttujat (kaikki voi asettaa ennen include-riviä):
#   FRAGMENTIT   konfiguraatiofragmentit tinyconfigin päälle
#   VALIMUISTI   lähteiden ja käännösten hakemisto (oletus ~/.cache)
#
# Ydin käännetään kerran fragmenttien tiivistettä kohden ja jaetaan
# kaikkien esimerkkien kesken. Rinnakkaiset ajot odottavat lukossa.

YMPARISTO  := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
FRAGMENTIT ?= $(YMPARISTO)/perus.config
VALIMUISTI ?= $(HOME)/.cache/tutoriaalit/embedded-linux

# @alku muuttujat
YDINPAKETTI := /usr/src/linux-source-6.8.0/linux-source-6.8.0.tar.bz2
LAHDE       := $(VALIMUISTI)/linux-source-6.8.0
TIIVISTE    := $(shell cat $(FRAGMENTIT) | sha256sum | cut -c1-12)
YDIN        := $(VALIMUISTI)/ydin-$(TIIVISTE)
IMAGE       := $(YDIN)/arch/arm64/boot/Image
GEN_CPIO    := $(YDIN)/usr/gen_init_cpio
RISTI       := aarch64-linux-gnu-
# Toistettava käännös: ei aikaleimaa, käyttäjää eikä konetta.
YMAKE = $(MAKE) -C $(LAHDE) O=$(YDIN) ARCH=arm64 \
        CROSS_COMPILE=$(RISTI) \
        KBUILD_BUILD_TIMESTAMP=2026-01-01 \
        KBUILD_BUILD_USER=tutoriaali KBUILD_BUILD_HOST=kaantaja
# @loppu muuttujat

# Ilman ylemmän maken töidenjakoa käännetään kaikilla ytimillä.
YDIN_J := $(if $(findstring jobserver,$(MAKEFLAGS)),,-j$(shell nproc))
LUKKO  := flock $(VALIMUISTI)/.lukko

$(VALIMUISTI):
	mkdir -p $@

# Lähteet puretaan kerran. Documentation-hakemistosta tarvitaan vain
# Kconfig-tiedosto, joten muu dokumentaatio jätetään purkamatta.
$(LAHDE)/Makefile: | $(VALIMUISTI)
	$(LUKKO) sh -c 'test -f $@ || { \
	  tar -C $(VALIMUISTI) -xjf $(YDINPAKETTI) \
	    --exclude=linux-source-6.8.0/Documentation && \
	  tar -C $(VALIMUISTI) -xjf $(YDINPAKETTI) \
	    linux-source-6.8.0/Documentation/Kconfig; }'

# @alku konfigurointi
$(YDIN)/.config: $(FRAGMENTIT) $(YMPARISTO)/tarkista-config.sh \
                 | $(LAHDE)/Makefile
	+$(LUKKO) sh -c '\
	  $(YMAKE) -s tinyconfig && \
	  cd $(YDIN) && ARCH=arm64 \
	    $(LAHDE)/scripts/kconfig/merge_config.sh -m .config \
	    $(FRAGMENTIT) > merge.log && \
	  $(YMAKE) -s olddefconfig'
	$(YMPARISTO)/tarkista-config.sh $@ $(FRAGMENTIT)
# @loppu konfigurointi

# @alku kaannos
$(YDIN)/valmis: $(YDIN)/.config
	+$(LUKKO) $(YMAKE) $(YDIN_J) -s Image modules
	touch $@

$(IMAGE) $(GEN_CPIO): $(YDIN)/valmis
# @loppu kaannos

.PHONY: ydin ydin-menuconfig ydin-siivoa
ydin: $(IMAGE)

# Konfiguraation muokkaus valikolla (vaatii libncurses-dev).
ydin-menuconfig: $(YDIN)/.config
	$(YMAKE) menuconfig

ydin-siivoa:
	rm -rf $(VALIMUISTI)
