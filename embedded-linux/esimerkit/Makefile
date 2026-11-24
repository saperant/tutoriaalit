# Sulautettu Linux: esimerkit ARM64:lle QEMU:n virt-koneessa.
#
#   make             kääntää ytimen (kerran), rakentaa esimerkkien
#                    juuritiedostojärjestelmät ja levykuvat, käynnistää
#                    ne QEMU:ssa ja vertaa tulosteet tiedostoihin
#                    testit/<testi>.odotettu
#   make aja E=03    käynnistää initramfs-esimerkin päätteessä (02-04)
#   make siivoa      poistaa build/-hakemiston; ydin säilyy välimuistissa
#   make ydin-siivoa poistaa myös ytimen lähteet ja käännöksen
#
# Ydin käännetään hakemistoon $(VALIMUISTI) (ks. ymparisto/ydin.mk).

include ymparisto/ydin.mk
.DEFAULT_GOAL := kaikki

B         := build
QEMU      := ymparisto/aja-qemu.sh
UBOOT     := /usr/lib/u-boot/qemu_arm64/u-boot.bin
# Kiinteä aikaleima tekee arkistoista ja levykuvista toistettavia.
AIKA      := 1767225600
# @alku ristiin
CC_ARM    := $(RISTI)gcc
CFLAGS    := -O2 -std=c11 -D_GNU_SOURCE -Wall -Wextra -Werror
# @loppu ristiin
KOMENTO   := console=ttyAMA0 loglevel=1 panic=-1
# Testin tuloste: konsolin rivinvaihdot \r\n -> \n ja paluuarvo loppuun.
TULOS      = { $(1); echo "paluuarvo $$?"; } 2>&1 | tr -d '\r'

TESTIT := 01-ristiin 02-init 02-loki 03-palvelut 04-otsake 04-ikconfig \
          04-rikki 04-moduuli 05-laitepuu 05-pl011 05-anturi 06-extlinux \
          06-skripti 06-kasin 07-juuri 08-palvelut 08-paniikki 09-viitteet
TULOKSET := $(TESTIT:%=$(B)/%.tulos) $(B)/tyylit.ok

.PHONY: kaikki aja siivoa
kaikki: $(TULOKSET)

$(B):
	mkdir -p $@

# Yleinen vertailu: build/X.tulos syntyy build/X.uusi-tiedostosta.
$(B)/%.tulos: $(B)/%.uusi testit/%.odotettu
	diff -u testit/$*.odotettu $<
	cp $< $@

# Python- ja shell-tiedostojen tarkistukset.
PYTHON   := $(wildcard */*.py)
SKRIPTIT := $(wildcard */*.sh)
$(B)/tyylit.ok: $(PYTHON) $(SKRIPTIT) | $(B)
	ruff check -q --no-cache $(PYTHON)
	mypy --strict --no-error-summary --cache-dir=$(B)/mypy $(PYTHON)
	shellcheck $(SKRIPTIT)
	touch $@

# --- 01: ristiinkääntäminen ---------------------------------------------
# @alku 01
$(B)/tietoja-isanta: 01-ristiin/tietoja.c | $(B)
	gcc $(CFLAGS) $< -o $@
$(B)/tietoja-staattinen: 01-ristiin/tietoja.c | $(B)
	$(CC_ARM) $(CFLAGS) -static $< -o $@
$(B)/tietoja-dynaaminen: 01-ristiin/tietoja.c | $(B)
	$(CC_ARM) $(CFLAGS) $< -o $@
# @loppu 01

$(B)/01-ristiin.uusi: $(B)/tietoja-isanta $(B)/tietoja-staattinen \
                      $(B)/tietoja-dynaaminen
	{ echo "== isanta"; $(B)/tietoja-isanta; \
	  echo "== qemu-aarch64, staattinen"; \
	  qemu-aarch64 $(B)/tietoja-staattinen; \
	  echo "== qemu-aarch64, dynaaminen ilman sysrootia"; \
	  { qemu-aarch64 $(B)/tietoja-dynaaminen; echo "paluuarvo $$?"; } \
	    2>&1 | sed 's/: No such/:\n    No such/'; \
	  echo "== qemu-aarch64 -L /usr/aarch64-linux-gnu, dynaaminen"; \
	  qemu-aarch64 -L /usr/aarch64-linux-gnu $(B)/tietoja-dynaaminen; \
	  echo "== readelf"; \
	  $(RISTI)readelf -h $(B)/tietoja-dynaaminen | \
	    sed -n 's/^ *\(Class\|Machine\): *\(.*\)/\1: \2/p'; \
	  $(RISTI)readelf -l $(B)/tietoja-dynaaminen | \
	    grep -o 'interpreter: [^]]*'; \
	  echo "staattisen tulkkeja: $$($(RISTI)readelf -l \
	    $(B)/tietoja-staattinen | grep -c interpreter)"; \
	} > $@ 2>&1

# --- 02: init ja initramfs ----------------------------------------------
# @alku initramfs
$(B)/%.init: | $(B)
	$(CC_ARM) $(CFLAGS) -static $(filter %.c,$^) -o $@

$(B)/02.init: 02-init/init.c
$(B)/02.cpio.gz: 02-init/initramfs.lista $(B)/02.init $(GEN_CPIO)
	INIT=$(B)/02.init $(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
# @loppu initramfs

# @alku 02
$(B)/02-init.uusi: $(B)/02.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -a "$(KOMENTO)") > $@
# @loppu 02

# Ytimen oma käynnistysloki: valitut rivit ilman aikoja ja osoitteita.
# @alku loki
LOKIRIVIT := -e 's/^\(Linux version [^ ]* ([^)]*)\).*/\1/p' \
             -e '/^Machine model:/p' -e '/^Kernel command line:/p' \
             -e 's/^\(Memory: \).*/\1.../p' \
             -e 's/^\(9000000.pl011: ttyAMA0\) .*/\1/p' \
             -e '/^Unpacking initramfs/p' -e '/^Run /p' \
             -e '/^reboot:/p' -e '/^paluuarvo/p'
$(B)/02-loki.uusi: $(B)/02.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< \
	    -a "console=ttyAMA0 panic=-1") | sed -n $(LOKIRIVIT) > $@
# @loppu loki

# --- 03: palvelut -------------------------------------------------------
$(B)/03-minit.init: 03-palvelut/minit.c
$(B)/03-palvelu.init: 03-palvelut/palvelu.c
$(B)/03.cpio.gz: 03-palvelut/initramfs.lista 03-palvelut/palvelut.conf \
                 $(B)/03-minit.init $(B)/03-palvelu.init $(GEN_CPIO)
	MINIT=$(B)/03-minit.init PALVELU=$(B)/03-palvelu.init \
	PALVELUT_CONF=03-palvelut/palvelut.conf \
	    $(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
$(B)/03-palvelut.uusi: $(B)/03.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -a "$(KOMENTO)") > $@

# --- 04: ydin -----------------------------------------------------------
$(B)/04-otsake.uusi: 04-ydin/otsake.py $(IMAGE) | $(B)
	$(call TULOS,python3 $< $(IMAGE)) > $@

# @alku ikconfig
$(B)/04-ikconfig.uusi: $(IMAGE) | $(B)
	$(LAHDE)/scripts/extract-ikconfig $(IMAGE) | \
	    grep -E '^CONFIG_(LOCALVERSION|SERIAL_AMBA_PL011|TMPFS)=' > $@
# @loppu ikconfig

# Väärä fragmentti konfiguroidaan omaan hakemistoonsa (ei käännöstä).
# @alku rikki
RIKKI := $(abspath $(B)/04-rikki)
$(B)/04-rikki.uusi: 04-ydin/rikki.config $(LAHDE)/Makefile | $(B)
	+$(YMAKE) -s O=$(RIKKI) tinyconfig
	cd $(RIKKI) && ARCH=arm64 $(LAHDE)/scripts/kconfig/merge_config.sh \
	    -m .config $(abspath $<) > /dev/null
	+$(YMAKE) -s O=$(RIKKI) olddefconfig
	$(call TULOS,ymparisto/tarkista-config.sh $(RIKKI)/.config $<) > $@
# @loppu rikki

# @alku moduuli
MODUULI := $(abspath $(B)/04-moduuli)
$(MODUULI)/hei.ko: 04-ydin/moduuli/hei.c 04-ydin/moduuli/Kbuild \
                   $(YDIN)/valmis | $(B)
	mkdir -p $(MODUULI) && cp $(filter 04-ydin/%,$^) $(MODUULI)/
	+$(YMAKE) -s M=$(MODUULI) modules
# @loppu moduuli
$(B)/04-lataaja.init: 04-ydin/lataaja.c
$(B)/04.cpio.gz: 04-ydin/initramfs.lista $(B)/04-lataaja.init \
                 $(MODUULI)/hei.ko $(GEN_CPIO)
	LATAAJA=$(B)/04-lataaja.init MODUULI=$(MODUULI)/hei.ko \
	    $(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
$(B)/04-moduuli.uusi: $(B)/04.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -a "$(KOMENTO)") > $@

# --- 05: laitepuu -------------------------------------------------------
# @alku dumpdtb
$(B)/virt.dtb: $(QEMU) | $(B)
	$(QEMU) -- -machine dumpdtb=$@ 2> $@.loki || { cat $@.loki; exit 1; }
$(B)/virt.dts: $(B)/virt.dtb
	dtc -q -I dtb -O dts -o $@ $<
$(B)/muokattu.dtb: $(B)/virt.dts 05-laitepuu/anturi.dtsi
	cat $^ | dtc -q -I dts -O dtb -o $@ -
# @loppu dumpdtb

# @alku fdtget
$(B)/05-laitepuu.uusi: 05-laitepuu/kysely.sh $(B)/virt.dtb
	$(call TULOS,$< $(B)/virt.dtb) > $@
# @loppu fdtget

# Tekstissä näytetty solmu on sama kuin QEMU:n laitepuussa.
$(B)/05-pl011.uusi: 05-laitepuu/pl011.dts $(B)/virt.dts
	sed -n '/^\tpl011@9000000 {/,/^\t};/s/^\t//p' $(B)/virt.dts \
	    | expand -t4 | diff $< - > /dev/null
	echo "pl011.dts vastaa QEMU:n laitepuuta" > $@

$(B)/05-tutkija.init: 05-laitepuu/tutkija.c
$(B)/05.cpio.gz: 05-laitepuu/initramfs.lista $(B)/05-tutkija.init \
                 $(GEN_CPIO)
	TUTKIJA=$(B)/05-tutkija.init $(GEN_CPIO) -t $(AIKA) $< \
	    | gzip -n -9 > $@
# Ilman -a-valitsinta ydin saa komentorivinsä laitepuun chosen-solmusta.
$(B)/05-anturi.uusi: $(B)/05.cpio.gz $(B)/muokattu.dtb $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -d $(B)/muokattu.dtb) > $@

# --- 06: U-Boot ---------------------------------------------------------
# @alku levy
# Levykuva: MBR, yksi ext4-osio 1 MiB:n kohdalta. mke2fs -d kopioi
# hakemiston sisällön ilman pääkäyttäjän oikeuksia.
LEVYAIKA := E2FSPROGS_FAKE_TIME=$(AIKA) SOURCE_DATE_EPOCH=$(AIKA)
$(B)/%.img: 06-uboot/levykuva.py $(B)/%-osio/valmis
	python3 $< $@ 32 > /dev/null
	$(LEVYAIKA) mke2fs -q -t ext4 -E offset=1048576 -U clear \
	    -d $(B)/$*-osio $@ 31M
# @loppu levy

$(B)/extlinux-osio/valmis: 06-uboot/extlinux.conf $(B)/02.cpio.gz $(IMAGE)
	rm -rf $(@D) && mkdir -p $(@D)/extlinux
	cp 06-uboot/extlinux.conf $(@D)/extlinux/
	cp $(IMAGE) $(@D)/Image && cp $(B)/02.cpio.gz $(@D)/initramfs.cpio.gz
	touch $@
# @alku mkimage
$(B)/skripti-osio/valmis: 06-uboot/boot.cmd $(B)/02.cpio.gz $(IMAGE)
	rm -rf $(@D) && mkdir -p $(@D)
	$(LEVYAIKA) mkimage -A arm64 -T script -C none -d $< $(@D)/boot.scr \
	    > /dev/null
	cp $(IMAGE) $(@D)/Image && cp $(B)/02.cpio.gz $(@D)/initramfs.cpio.gz
	touch $@
# @loppu mkimage

# U-Bootin oma tuloste vaihtelee versioittain, joten siitä otetaan
# vain valitun käynnistystavan rivit.
UBOOTRIVIT := -e '/^Retrieving file/p' -e '/^Starting kernel/p' \
              -e 's/^ *[0-9]  *\([a-z]*\)  *ready  *virtio .* /tapa: \1 /p' \
              -e '/^init: komentorivi/p' -e '/^reboot:/p' -e '/^paluuarvo/p'
$(B)/06-%.uusi: $(B)/%.img
	$(call TULOS,$(QEMU) -b $(UBOOT) -l $< < /dev/null) \
	    | sed -n $(UBOOTRIVIT) > $@
$(B)/06-kasin.uusi: 06-uboot/kasin.vaiheet $(B)/extlinux.img \
                    08-kaynnistystesti/kaynnistystesti.py
	$(call TULOS,python3 08-kaynnistystesti/kaynnistystesti.py $< -- \
	    $(QEMU) -b $(UBOOT) -l $(B)/extlinux.img) > $@

# --- 07: pysyvä juuri ---------------------------------------------------
# @alku juuri
$(B)/07.init: 07-juuri/init.c
$(B)/juuri.img: $(B)/07.init 07-juuri/laite.conf
	rm -rf $(B)/juuri && mkdir -p $(B)/juuri/sbin $(B)/juuri/etc
	mkdir -p $(B)/juuri/proc $(B)/juuri/dev $(B)/juuri/run
	cp $(B)/07.init $(B)/juuri/sbin/init
	cp 07-juuri/laite.conf $(B)/juuri/etc/
	rm -f $@ && truncate -s 16M $@
	$(LEVYAIKA) mke2fs -q -t ext4 -U clear -E root_owner=0:0 \
	    -d $(B)/juuri $@
$(B)/07-juuri.uusi: $(B)/juuri.img $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -l $< \
	    -a "$(KOMENTO) root=/dev/vda ro rootfstype=ext4 init=/sbin/init") \
	    > $@
# @loppu juuri

# --- 08: käynnistystestit -----------------------------------------------
# @alku 08
KTESTI := python3 08-kaynnistystesti/kaynnistystesti.py
KTESTI_PY := 08-kaynnistystesti/kaynnistystesti.py
$(B)/08-palvelut.uusi: 08-kaynnistystesti/palvelut.vaiheet $(B)/03.cpio.gz \
                       $(KTESTI_PY)
	$(call TULOS,$(KTESTI) $< -- $(QEMU) -k $(IMAGE) \
	    -i $(B)/03.cpio.gz -a "$(KOMENTO)") > $@
$(B)/08-rikki.cpio.gz: 08-kaynnistystesti/rikki.lista $(GEN_CPIO) | $(B)
	$(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
$(B)/08-paniikki.uusi: 08-kaynnistystesti/palvelut.vaiheet \
                       $(B)/08-rikki.cpio.gz $(KTESTI_PY)
	$(call TULOS,$(KTESTI) $< -- $(QEMU) -k $(IMAGE) \
	    -i $(B)/08-rikki.cpio.gz -a "$(KOMENTO)") > $@
# @loppu 08

# --- 09: Buildroot ja Yocto (ei ajeta, viittaukset tarkistetaan) --------
$(B)/09-viitteet.uusi: 09-buildroot/tarkista.sh \
                       $(wildcard 09-buildroot/*/*/*/*) | $(B)
	$(call TULOS,$<) > $@

# Levykuvat ja arkistot ovat välituotteita, mutta ne säilytetään.
.SECONDARY:

# --- käsiajo ------------------------------------------------------------
aja: $(B)/$(E).cpio.gz $(IMAGE)
	$(QEMU) -t 600 -k $(IMAGE) -i $< -a "$(KOMENTO)"

siivoa:
	rm -rf $(B)
