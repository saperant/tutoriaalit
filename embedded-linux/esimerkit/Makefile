# Sulautettu Linux: esimerkit ARM64:lle QEMU:n virt-koneessa.
#
#   make             kääntää ytimen (kerran), rakentaa esimerkkien
#                    juuritiedostojärjestelmät ja levykuvat, käynnistää
#                    ne QEMU:ssa ja vertaa tulosteet tiedostoihin
#                    testit/<testi>.odotettu
#   make aja E=07    käynnistää initramfs-esimerkin päätteessä
#                    (03, 04, 06, 07 tai 11-kaynnistys)
#   make siivoa      poistaa build/-hakemiston; ydin säilyy välimuistissa
#   make ydin-siivoa poistaa myös ytimen lähteet ja käännöksen
#
# Ydin käännetään hakemistoon $(VALIMUISTI) (ks. ymparisto/ydin.mk).

# Ydin: perusfragmentti ja vianetsinnän lisäykset (luku 11).
FRAGMENTIT := $(abspath ymparisto/perus.config \
                        11-vianetsinta/vianetsinta.config)
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

TESTIT := 02-ristiin 03-ikconfig 03-rikki 03-moduuli 04-init 04-loki \
          05-otsake 05-extlinux 05-skripti 05-kasin 06-laitepuu 06-pl011 \
          06-puu 06-anturi 07-palvelut 08-juuri 09-viitteet 10-palvelut \
          10-paniikki 11-kaynnistys 11-elf 11-jaljitys 11-gdb \
          11-kaatuminen 11-vedos
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

# --- 02: ristiinkääntäminen --------------------------------------------
# @alku kaannokset
$(B)/tietoja-isanta: 02-ristiin/tietoja.c | $(B)
	gcc $(CFLAGS) $< -o $@
$(B)/tietoja-staattinen: 02-ristiin/tietoja.c | $(B)
	$(CC_ARM) $(CFLAGS) -static $< -o $@
$(B)/tietoja-dynaaminen: 02-ristiin/tietoja.c | $(B)
	$(CC_ARM) $(CFLAGS) $< -o $@
# @loppu kaannokset

$(B)/02-ristiin.uusi: $(B)/tietoja-isanta $(B)/tietoja-staattinen \
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

# --- 03: ydin ----------------------------------------------------------
# @alku ikconfig
$(B)/03-ikconfig.uusi: $(IMAGE) | $(B)
	$(LAHDE)/scripts/extract-ikconfig $(IMAGE) | \
	    grep -E '^CONFIG_(LOCALVERSION|SERIAL_AMBA_PL011|TMPFS)=' > $@
# @loppu ikconfig

# Väärä fragmentti konfiguroidaan omaan hakemistoonsa (ei käännöstä).
# @alku rikki
RIKKI := $(abspath $(B)/03-rikki)
$(B)/03-rikki.uusi: 03-ydin/rikki.config $(LAHDE)/Makefile | $(B)
	+$(YMAKE) -s O=$(RIKKI) tinyconfig
	cd $(RIKKI) && ARCH=arm64 $(LAHDE)/scripts/kconfig/merge_config.sh \
	    -m .config $(abspath $<) > /dev/null
	+$(YMAKE) -s O=$(RIKKI) olddefconfig
	$(call TULOS,ymparisto/tarkista-config.sh $(RIKKI)/.config $<) > $@
# @loppu rikki

# @alku moduuli
MODUULI := $(abspath $(B)/03-moduuli)
$(MODUULI)/hei.ko: 03-ydin/moduuli/hei.c 03-ydin/moduuli/Kbuild \
                   $(YDIN)/valmis | $(B)
	mkdir -p $(MODUULI) && cp $(filter 03-ydin/%,$^) $(MODUULI)/
	+$(YMAKE) -s M=$(MODUULI) modules
# @loppu moduuli
$(B)/03-lataaja.init: 03-ydin/lataaja.c
$(B)/03.cpio.gz: 03-ydin/initramfs.lista $(B)/03-lataaja.init \
                 $(MODUULI)/hei.ko $(GEN_CPIO)
	LATAAJA=$(B)/03-lataaja.init MODUULI=$(MODUULI)/hei.ko \
	    $(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
$(B)/03-moduuli.uusi: $(B)/03.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -a "$(KOMENTO)") > $@

# --- 04: init ja initramfs ---------------------------------------------
# @alku initramfs
$(B)/%.init: | $(B)
	$(CC_ARM) $(CFLAGS) -static $(filter %.c,$^) -o $@

$(B)/04.init: 04-init/init.c
$(B)/04.cpio.gz: 04-init/initramfs.lista $(B)/04.init $(GEN_CPIO)
	INIT=$(B)/04.init $(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
# @loppu initramfs

# @alku ajo
$(B)/04-init.uusi: $(B)/04.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -a "$(KOMENTO)") > $@
# @loppu ajo

# Ytimen oma käynnistysloki: valitut rivit ilman aikoja ja osoitteita.
# @alku loki
LOKIRIVIT := -e 's/^\(Linux version [^ ]* ([^)]*)\).*/\1/p' \
             -e '/^Machine model:/p' -e '/^Kernel command line:/p' \
             -e 's/^\(Memory: \).*/\1.../p' \
             -e 's/^\(9000000.pl011: ttyAMA0\) .*/\1/p' \
             -e '/^Unpacking initramfs/p' -e '/^Run /p' \
             -e '/^reboot:/p' -e '/^paluuarvo/p'
$(B)/04-loki.uusi: $(B)/04.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< \
	    -a "console=ttyAMA0 panic=-1") | sed -n $(LOKIRIVIT) > $@
# @loppu loki

# --- 05: käynnistysketju ja U-Boot -------------------------------------
$(B)/05-otsake.uusi: 05-uboot/otsake.py $(IMAGE) | $(B)
	$(call TULOS,python3 $< $(IMAGE)) > $@

# @alku levy
# Levykuva: MBR, yksi ext4-osio 1 MiB:n kohdalta. mke2fs -d kopioi
# hakemiston sisällön ilman pääkäyttäjän oikeuksia.
LEVYAIKA := E2FSPROGS_FAKE_TIME=$(AIKA) SOURCE_DATE_EPOCH=$(AIKA)
$(B)/%.img: 05-uboot/levykuva.py $(B)/%-osio/valmis
	python3 $< $@ 32 > /dev/null
	$(LEVYAIKA) mke2fs -q -t ext4 -E offset=1048576 -U clear \
	    -d $(B)/$*-osio $@ 31M
# @loppu levy

$(B)/extlinux-osio/valmis: 05-uboot/extlinux.conf $(B)/04.cpio.gz $(IMAGE)
	rm -rf $(@D) && mkdir -p $(@D)/extlinux
	cp 05-uboot/extlinux.conf $(@D)/extlinux/
	cp $(IMAGE) $(@D)/Image && cp $(B)/04.cpio.gz $(@D)/initramfs.cpio.gz
	touch $@
# @alku mkimage
$(B)/skripti-osio/valmis: 05-uboot/boot.cmd $(B)/04.cpio.gz $(IMAGE)
	rm -rf $(@D) && mkdir -p $(@D)
	$(LEVYAIKA) mkimage -A arm64 -T script -C none -d $< $(@D)/boot.scr \
	    > /dev/null
	cp $(IMAGE) $(@D)/Image && cp $(B)/04.cpio.gz $(@D)/initramfs.cpio.gz
	touch $@
# @loppu mkimage

# U-Bootin oma tuloste vaihtelee versioittain, joten siitä otetaan
# vain valitun käynnistystavan rivit.
UBOOTRIVIT := -e '/^Retrieving file/p' -e '/^Starting kernel/p' \
              -e 's/^ *[0-9]  *\([a-z]*\)  *ready  *virtio .* /tapa: \1 /p' \
              -e '/^init: komentorivi/p' -e '/^reboot:/p' -e '/^paluuarvo/p'
$(B)/05-%.uusi: $(B)/%.img
	$(call TULOS,$(QEMU) -b $(UBOOT) -l $< < /dev/null) \
	    | sed -n $(UBOOTRIVIT) > $@
$(B)/05-kasin.uusi: 05-uboot/kasin.vaiheet $(B)/extlinux.img \
                    10-kaynnistystesti/kaynnistystesti.py
	$(call TULOS,python3 10-kaynnistystesti/kaynnistystesti.py $< -- \
	    $(QEMU) -b $(UBOOT) -l $(B)/extlinux.img) > $@

# --- 06: laitepuu ------------------------------------------------------
# @alku dumpdtb
$(B)/virt.dtb: $(QEMU) | $(B)
	$(QEMU) -- -machine dumpdtb=$@ 2> $@.loki || { cat $@.loki; exit 1; }
$(B)/virt.dts: $(B)/virt.dtb
	dtc -q -I dtb -O dts -o $@ $<
$(B)/muokattu.dtb: $(B)/virt.dts 06-laitepuu/anturi.dtsi
	cat $^ | dtc -q -I dts -O dtb -o $@ -
# @loppu dumpdtb

# @alku fdtget
$(B)/06-laitepuu.uusi: 06-laitepuu/kysely.sh $(B)/virt.dtb
	$(call TULOS,$< $(B)/virt.dtb) > $@
# @loppu fdtget

# Tekstissä näytetty solmu on sama kuin QEMU:n laitepuussa.
$(B)/06-pl011.uusi: 06-laitepuu/pl011.dts $(B)/virt.dts
	sed -n '/^\tpl011@9000000 {/,/^\t};/s/^\t//p' $(B)/virt.dts \
	    | expand -t4 | diff $< - > /dev/null
	echo "pl011.dts vastaa QEMU:n laitepuuta" > $@

# Tekstin kaavio on piirretty samasta laitepuusta.
$(B)/06-puu.uusi: 06-laitepuu/puu.py 06-laitepuu/puu.dot $(B)/virt.dtb
	python3 $< $(B)/virt.dtb pl011@9000000 | diff 06-laitepuu/puu.dot -
	echo "puu.dot vastaa QEMU:n laitepuuta" > $@

$(B)/06-tutkija.init: 06-laitepuu/tutkija.c
$(B)/06.cpio.gz: 06-laitepuu/initramfs.lista $(B)/06-tutkija.init \
                 $(GEN_CPIO)
	TUTKIJA=$(B)/06-tutkija.init $(GEN_CPIO) -t $(AIKA) $< \
	    | gzip -n -9 > $@
# Ilman -a-valitsinta ydin saa komentorivinsä laitepuun chosen-solmusta.
$(B)/06-anturi.uusi: $(B)/06.cpio.gz $(B)/muokattu.dtb $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -d $(B)/muokattu.dtb) > $@

# --- 07: palvelut ------------------------------------------------------
$(B)/07-minit.init: 07-palvelut/minit.c
$(B)/07-palvelu.init: 07-palvelut/palvelu.c
$(B)/07.cpio.gz: 07-palvelut/initramfs.lista 07-palvelut/palvelut.conf \
                 $(B)/07-minit.init $(B)/07-palvelu.init $(GEN_CPIO)
	MINIT=$(B)/07-minit.init PALVELU=$(B)/07-palvelu.init \
	PALVELUT_CONF=07-palvelut/palvelut.conf \
	    $(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
$(B)/07-palvelut.uusi: $(B)/07.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -a "$(KOMENTO)") > $@

# --- 08: pysyvä juuri --------------------------------------------------
# @alku juuri
$(B)/08.init: 08-juuri/init.c
$(B)/juuri.img: $(B)/08.init 08-juuri/laite.conf
	rm -rf $(B)/juuri && mkdir -p $(B)/juuri/sbin $(B)/juuri/etc
	mkdir -p $(B)/juuri/proc $(B)/juuri/dev $(B)/juuri/run
	cp $(B)/08.init $(B)/juuri/sbin/init
	cp 08-juuri/laite.conf $(B)/juuri/etc/
	rm -f $@ && truncate -s 16M $@
	$(LEVYAIKA) mke2fs -q -t ext4 -U clear -E root_owner=0:0 \
	    -d $(B)/juuri $@
$(B)/08-juuri.uusi: $(B)/juuri.img $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -l $< \
	    -a "$(KOMENTO) root=/dev/vda ro rootfstype=ext4 init=/sbin/init") \
	    > $@
# @loppu juuri

# --- 09: Buildroot ja Yocto (ei ajeta, viittaukset tarkistetaan) --------
$(B)/09-viitteet.uusi: 09-buildroot/tarkista.sh \
                       $(wildcard 09-buildroot/*/*/*/*) | $(B)
	$(call TULOS,$<) > $@

# --- 10: käynnistystestit ----------------------------------------------
# @alku testit
KTESTI := python3 10-kaynnistystesti/kaynnistystesti.py
KTESTI_PY := 10-kaynnistystesti/kaynnistystesti.py
$(B)/10-palvelut.uusi: 10-kaynnistystesti/palvelut.vaiheet $(B)/07.cpio.gz \
                       $(KTESTI_PY)
	$(call TULOS,$(KTESTI) $< -- $(QEMU) -k $(IMAGE) \
	    -i $(B)/07.cpio.gz -a "$(KOMENTO)") > $@
$(B)/10-rikki.cpio.gz: 10-kaynnistystesti/rikki.lista $(GEN_CPIO) | $(B)
	$(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
$(B)/10-paniikki.uusi: 10-kaynnistystesti/palvelut.vaiheet \
                       $(B)/10-rikki.cpio.gz $(KTESTI_PY)
	$(call TULOS,$(KTESTI) $< -- $(QEMU) -k $(IMAGE) \
	    -i $(B)/10-rikki.cpio.gz -a "$(KOMENTO)") > $@
# @loppu testit

# --- 11: vianetsintä kohteessa ------------------------------------------
V := 11-vianetsinta
# @alku symbolit
# Isännälle jää ohjelma virheenjäljitystietoineen, kohteeseen menee
# riisuttu kopio. Koodin osoitteet ovat molemmissa samat.
CFLAGS_V := -Og -g -ffile-prefix-map=$(V)/= -std=c11 -D_GNU_SOURCE \
            -Wall -Wextra -Werror
$(B)/anturi: $(V)/anturi.c | $(B)
	$(CC_ARM) $(CFLAGS_V) -static $< -o $@
$(B)/anturi.kohde: $(B)/anturi
	$(RISTI)strip -o $@ $<
# @loppu symbolit

# Käynnistyskokeet: sama pieni ohjelma eri tavoin kelvottomana.
$(B)/hei-staattinen: $(V)/hei.c | $(B)
	$(CC_ARM) $(CFLAGS) -static $< -o $@
$(B)/hei-dynaaminen: $(V)/hei.c | $(B)
	$(CC_ARM) $(CFLAGS) $< -o $@
$(B)/hei-isanta: $(V)/hei.c | $(B)
	gcc $(CFLAGS) -static $< -o $@
$(B)/11-kokeile.init: $(V)/kokeile.c
$(B)/11-kaynnistys.cpio.gz: $(V)/kaynnistys.lista $(V)/skripti \
                            $(B)/11-kokeile.init $(B)/hei-staattinen \
                            $(B)/hei-dynaaminen $(B)/hei-isanta $(GEN_CPIO)
	KOKEILE=$(B)/11-kokeile.init STAATTINEN=$(B)/hei-staattinen \
	DYNAAMINEN=$(B)/hei-dynaaminen ISANTA=$(B)/hei-isanta \
	SKRIPTI=$(V)/skripti $(GEN_CPIO) -t $(AIKA) $< | gzip -n -9 > $@
$(B)/11-kaynnistys.uusi: $(B)/11-kaynnistys.cpio.gz $(IMAGE)
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -a "$(KOMENTO)") > $@
# @alku elf
$(B)/11-elf.uusi: $(V)/elf.sh $(B)/hei-staattinen $(B)/hei-dynaaminen \
                  $(B)/hei-isanta
	$(call TULOS,$^) > $@
# @loppu elf

# Järjestelmäkutsujen jäljitys QEMU:n käyttäjätilan emulaattorilla.
# Prosessin numero ja osoitteet vaihtelevat, joten ne poistetaan.
# @alku jaljitys
$(B)/11-jaljitys.uusi: $(B)/anturi
	{ qemu-aarch64 $(B)/anturi /etc/anturi.conf; echo "paluuarvo $$?"; \
	  qemu-aarch64 -strace -D $(B)/jaljitys.loki $(B)/anturi \
	      /etc/anturi.conf 2> /dev/null; \
	  grep -E ' (openat|read|write|close|exit_group)\(' \
	      $(B)/jaljitys.loki | sed -E -e 's/^[0-9]+ //' \
	      -e 's/0x[0-9a-f]+/0x../' -e 's/ = -1 /\n    = -1 /'; \
	} > $@ 2>&1
# @loppu jaljitys

# Etädebuggaus: qemu-aarch64 -g on gdb-palvelin kuten gdbserver.
# Osoitteet korvataan, koska ne riippuvat kääntäjän versiosta.
GDB       := gdb-multiarch -q -batch -nx -iex "directory $(V)" \
             -iex "set print entry-values no"
PORTTI    := 11711
OSOITTEET := sed -E -e '/^warning: |^\[Inferior|^\[New LWP|^$$/d' \
                    -e 's/0x[0-9a-f]{4,}/0x../g' -e 's/\t/  /'
# @alku gdb
$(B)/11-gdb.uusi: $(V)/istunto.gdb $(B)/anturi $(V)/rikki.conf
	qemu-aarch64 -g $(PORTTI) $(B)/anturi $(V)/rikki.conf 2> /dev/null & \
	$(GDB) -ex "target remote :$(PORTTI)" -x $< $(B)/anturi 2>&1 \
	    | $(OSOITTEET) > $@; wait
# @loppu gdb

# Kaatuminen koko järjestelmässä: ytimen loki konsolilta ja ydinvedos
# kirjoitettavalta datalevyltä. Levy tehdään joka ajolle tyhjänä.
$(B)/11-tutki.init: $(V)/tutki.c
$(B)/11-vedos.cpio.gz: $(V)/vedos.lista $(V)/rikki.conf \
                       $(B)/11-tutki.init $(B)/anturi.kohde $(GEN_CPIO)
	TUTKI=$(B)/11-tutki.init ANTURI=$(B)/anturi.kohde \
	RIKKI_CONF=$(V)/rikki.conf $(GEN_CPIO) -t $(AIKA) $< \
	    | gzip -n -9 > $@
# @alku kaatuminen
$(B)/11-kaatuminen.loki: $(B)/11-vedos.cpio.gz $(IMAGE)
	rm -f $(B)/data.img $(B)/core.anturi
	truncate -s 16M $(B)/data.img
	$(LEVYAIKA) mke2fs -q -t ext4 -U clear -E root_owner=0:0 $(B)/data.img
	$(call TULOS,$(QEMU) -k $(IMAGE) -i $< -w $(B)/data.img \
	    -a "$(KOMENTO)") > $@
	debugfs -R "dump /core.anturi $(B)/core.anturi" $(B)/data.img \
	    2> /dev/null
# @loppu kaatuminen

# Lokin pc-osoite muunnetaan riviksi isännällä; itse osoite korvataan.
# @alku addr2line
$(B)/11-kaatuminen.uusi: $(B)/11-kaatuminen.loki $(B)/anturi
	{ sed -E -e 's/(ESR|pc :) *[0-9a-fx]+/\1 ../' \
	         -e 's/\[[0-9a-f]+\+[0-9a-f]+\]/[..]/' \
	         -e 's/(exception:|ESR \.\.,) /\1\n      /g' $<; \
	  echo "== addr2line"; \
	  $(RISTI)addr2line -f -s -e $(B)/anturi \
	      $$(sed -n 's/^loki: pc : //p' $<); } > $@
# @loppu addr2line

# @alku vedos
$(B)/11-vedos.uusi: $(V)/vedos.gdb $(B)/11-kaatuminen.loki $(B)/anturi
	$(GDB) -x $< $(B)/anturi $(B)/core.anturi 2>&1 | $(OSOITTEET) > $@
# @loppu vedos

# Levykuvat ja arkistot ovat välituotteita, mutta ne säilytetään.
.SECONDARY:

# --- käsiajo ------------------------------------------------------------
aja: $(B)/$(E).cpio.gz $(IMAGE)
	$(QEMU) -t 600 -k $(IMAGE) -i $< -a "$(KOMENTO)"

siivoa:
	rm -rf $(B)
