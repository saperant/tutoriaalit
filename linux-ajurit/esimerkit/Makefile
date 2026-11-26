# Linux-laiteajurit: esimerkit ARM64:lle QEMU:n virt-koneessa.
#
#   make             kääntää ytimen (kerran), moduulit ja testiohjelmat,
#                    käynnistää jokaisen testin QEMU:ssa ja vertaa
#                    tulosteen tiedostoon testit/<testi>.odotettu
#   make aja T=02-jono   käynnistää testin päätteessä
#   make siivoa      poistaa build/-hakemiston; ydin säilyy välimuistissa
#   make ydin-siivoa poistaa myös ytimen lähteet ja käännöksen
#
# Ympäristö (ymparisto/) on kopio Sulautettu Linux -tutoriaalin
# ympäristöstä; ydin saa lisäksi fragmentin ymparisto/ajurit.config.

include ymparisto/ydin.mk
.DEFAULT_GOAL := kaikki

B        := build
QEMU     := ymparisto/aja-qemu.sh
AIKA     := 1767225600
CC_ARM   := $(RISTI)gcc
CFLAGS   := -O2 -std=gnu11 -Wall -Wextra -Werror -static
# Ydin ei kirjoita konsoliin: lokirivit näytetään vain /dev/kmsg:n
# kautta suodatettuina. Ilman console_no_auto_verbose-valitsinta
# kaatumis- ja lockdep-ilmoitukset ohittaisivat lokitason.
KOMENTO  := console=ttyAMA0 loglevel=0 panic=-1 \
            printk.console_no_auto_verbose=1
TULOS     = { $(1); echo "paluuarvo $$?"; } 2>&1 | tr -d '\r'

TESTIT := 01-modinfo 01-suljettu 01-parametrit 02-jono 02-kartta 03-herate \
          03-vahti 04-dma 05-i2c 06-spi 07-resurssit 07-ajonaikainen \
          07-lepotila 08-dyndbg 08-ftrace 08-oops 08-lukot
TULOKSET := $(TESTIT:%=$(B)/%.tulos) $(B)/tyylit.ok $(B)/kaaviot.ok

.PHONY: kaikki aja siivoa
kaikki: $(TULOKSET)

$(B):
	mkdir -p $@

$(B)/%.tulos: $(B)/%.uusi testit/%.odotettu
	diff -u testit/$*.odotettu $<
	cp $< $@

SKRIPTIT := $(wildcard */*.sh)
$(B)/tyylit.ok: $(SKRIPTIT) | $(B)
	shellcheck $(SKRIPTIT)
	touch $@

# Virranhallinnan aikajana tuotetaan testin tulosteesta ja verrataan
# tallennettuun kaavioon, jota tekstissä näytetään.
# @alku kaavio
$(B)/kaaviot.ok: kaaviot/tee.py testit/07-ajonaikainen.odotettu \
                 kaaviot/virta.json | $(B)
	python3 kaaviot/tee.py testit/07-ajonaikainen.odotettu | \
	    diff -u kaaviot/virta.json -
	touch $@
# @loppu kaavio

# --- käyttäjätilan ohjelmat: staattisia ARM64-ohjelmia ------------------
# @alku ohjelmat
$(B)/bin/%: | $(B)
	mkdir -p $(@D)
	$(CC_ARM) $(CFLAGS) -I02-merkkilaite $(filter %.c,$^) -o $@

$(B)/bin/ajo: kayttaja/ajo.c
$(B)/bin/heksa: kayttaja/heksa.c
$(B)/bin/kirjoita: kayttaja/kirjoita.c
$(B)/bin/jonotesti: 02-merkkilaite/jonotesti.c 02-merkkilaite/jono.h
$(B)/bin/karttatesti: 02-merkkilaite/karttatesti.c
$(B)/bin/heratetesti: 03-platform/heratetesti.c
$(B)/bin/i2c-aseta: 05-i2c/i2c-aseta.c
$(B)/bin/tila: 07-resurssit/tila.c
# @loppu ohjelmat

# --- moduulit: ytimen ulkopuoliset moduulit Kbuildilla ------------------
# Lähteet kopioidaan build-hakemistoon, jotta käännöstuotteet eivät
# sotke lähdehakemistoa. Kaikki moduulit käännetään samaa ydintä vasten.
# @alku moduulit
define MODUULIT
$(B)/$(1)/valmis: $(wildcard $(1)/*.c $(1)/*.h) $(1)/Kbuild $(YDIN)/valmis
	rm -rf $(B)/$(1) && mkdir -p $(B)/$(1)
	cp $(1)/*.c $(1)/Kbuild $(B)/$(1)/
	cp $(wildcard $(1)/*.h) $(B)/$(1)/ 2>/dev/null || true
	+$(YMAKE) -s M=$(abspath $(B)/$(1)) modules
	touch $$@
endef
# @loppu moduulit
HAKEMISTOT := 01-moduulit 02-merkkilaite 03-platform 04-dma 05-i2c \
              06-spi 07-resurssit 08-vianetsinta
$(foreach h,$(HAKEMISTOT),$(eval $(call MODUULIT,$(h))))

# --- initramfs ja ajo ---------------------------------------------------
# Jokainen testi on oma järjestelmänsä: /init on vaiheajuri (ajo.c),
# /vaiheet sen komennot, /lib/modules moduulit ja /bin testiohjelmat.
# @alku testi
# $(call TESTI,nimi,vaiheet,moduulit,ohjelmat,qemu-valintojen muuttuja)
# Valinnat annetaan muuttujan nimenä, koska niissä voi olla pilkkuja.
define TESTI
$(B)/$(1).lista: $(2) $(3) $(4:%=$(B)/bin/%) $(B)/bin/ajo | $(B)
	{ printf '%s\n' 'dir /dev 0755 0 0' 'nod /dev/console 0600 0 0 c 5 1' \
	    'dir /proc 0555 0 0' 'dir /sys 0555 0 0' 'dir /lib 0755 0 0' \
	    'dir /lib/modules 0755 0 0' 'dir /bin 0755 0 0' \
	    'file /init $(B)/bin/ajo 0755 0 0' 'file /vaiheet $(2) 0644 0 0'; \
	  for m in $(3); do echo "file /lib/modules/$$$${m##*/} $$$$m 0644 0 0"; \
	  done; \
	  for o in $(4); do echo "file /bin/$$$$o $(B)/bin/$$$$o 0755 0 0"; \
	  done; } > $$@
$(B)/$(1).cpio.gz: $(B)/$(1).lista $(GEN_CPIO)
	$(GEN_CPIO) -t $(AIKA) $$< | gzip -n -9 > $$@
$(B)/$(1).raaka: $(B)/$(1).cpio.gz $(IMAGE) $(QEMU)
	$$(call TULOS,$(QEMU) -k $(IMAGE) -i $$< -a "$(KOMENTO)" \
	    $$($(strip $(5)))) > $$@
endef
# @loppu testi

# Oletuksena tuloste on sellaisenaan; normalisoivat testit määrittelevät
# oman .uusi-sääntönsä.
TAITA := awk -f ymparisto/taita.awk
$(B)/%.uusi: $(B)/%.raaka
	$(TAITA) $< > $@

# --- 01: moduulit -------------------------------------------------------
M01 := $(B)/01-moduulit
$(M01)/tilasto.ko $(M01)/mittaus.ko: $(M01)/valmis
	test -f $@

# @alku modinfo
$(B)/01-modinfo.uusi: $(M01)/valmis
	for m in tilasto mittaus; do \
	  modinfo $(M01)/$$m.ko | grep -E \
	    '^(name|license|description|depends|vermagic|parm):' | \
	    sed 's/ *$$//'; \
	  echo; \
	done > $@
# @loppu modinfo

# modpost hylkää suljetun moduulin, joka käyttää GPL-symbolia. Symbolien
# tiedot tulevat tilasto.ko:n käännöksen Module.symvers-tiedostosta.
# @alku suljettu
$(B)/01-suljettu.uusi: 01-moduulit/suljettu/suljettu.c \
                      01-moduulit/suljettu/Kbuild $(M01)/valmis
	rm -rf $(B)/suljettu && mkdir -p $(B)/suljettu
	cp $(filter 01-moduulit/suljettu/%,$^) 01-moduulit/tilasto.h \
	    $(B)/suljettu/
	sed -i 's|"../tilasto.h"|"tilasto.h"|' $(B)/suljettu/suljettu.c
	$(call TULOS,$(YMAKE) -s M=$(abspath $(B)/suljettu) \
	    KBUILD_EXTRA_SYMBOLS=$(abspath $(M01))/Module.symvers modules) \
	    | grep -E '^(ERROR|paluuarvo)' | sed 's|/[^ ]*/||' | $(TAITA) > $@
# @loppu suljettu

$(eval $(call TESTI,01-parametrit,01-moduulit/parametrit.vaiheet,\
    $(M01)/tilasto.ko $(M01)/mittaus.ko,,))

# --- 02: merkkilaite ----------------------------------------------------
$(B)/02-merkkilaite/jono.ko $(B)/02-merkkilaite/kartta.ko: \
    $(B)/02-merkkilaite/valmis
	test -f $@
$(eval $(call TESTI,02-jono,02-merkkilaite/jono.vaiheet,\
    $(B)/02-merkkilaite/jono.ko,jonotesti,))
$(eval $(call TESTI,02-kartta,02-merkkilaite/kartta.vaiheet,\
    $(B)/02-merkkilaite/kartta.ko,karttatesti,))

# --- 03: platform-ajuri, laitepuu ja keskeytykset ----------------------
# @alku dtb
$(B)/virt.dtb: $(QEMU) | $(B)
	$(QEMU) -- -machine dumpdtb=$@ 2> $@.loki || { cat $@.loki; exit 1; }
$(B)/virt.dts: $(B)/virt.dtb
	dtc -q -I dtb -O dts -o $@ $<
$(B)/%.dtb: $(B)/virt.dts 03-platform/%.dtsi
	cat $^ | dtc -q -I dts -O dtb -o $@ -
# @loppu dtb

$(B)/03-platform/herate.ko: $(B)/03-platform/valmis
	test -f $@
$(eval $(call TESTI,03-herate,03-platform/herate.vaiheet,\
    $(B)/03-platform/herate.ko,heratetesti,HERATE))
HERATE := -d $(B)/herate.dtb
$(B)/03-herate.raaka: $(B)/herate.dtb
# Rekisterivedoksessa laskurin ja vertailuarvon arvot riippuvat ajasta.
$(B)/03-herate.uusi: $(B)/03-herate.raaka
	sed -E 's/^(  RTC(DR|MR) +)0x[0-9a-f]+/\1.../' $< > $@

$(eval $(call TESTI,03-vahti,03-platform/vahti.vaiheet,\
    $(B)/03-platform/herate.ko,heratetesti,VAARA))
VAARA := -d $(B)/herate-vaara.dtb
$(B)/03-vahti.raaka: $(B)/herate-vaara.dtb
$(B)/herate-vaara.dtb: $(B)/virt.dts 03-platform/herate.dtsi \
                       03-platform/vaara.dtsi
	cat $^ | dtc -q -I dts -O dtb -o $@ -

# --- 04: DMA ------------------------------------------------------------
# @alku fwcfg
FWCFG := -- -fw_cfg name=opt/tutoriaalit/viesti,file=04-dma/viesti.txt
# @loppu fwcfg
$(B)/04-dma/fwcfg.ko: $(B)/04-dma/valmis
	test -f $@
$(eval $(call TESTI,04-dma,04-dma/dma.vaiheet,$(B)/04-dma/fwcfg.ko,,\
    FWCFG))
$(B)/04-dma.raaka: 04-dma/viesti.txt

# --- 05: I2C ------------------------------------------------------------
I2C_STUB := $(YDIN)/drivers/i2c/i2c-stub.ko
$(I2C_STUB) $(B)/05-i2c/lampo.ko: $(B)/05-i2c/valmis
	test -f $@
$(eval $(call TESTI,05-i2c,05-i2c/i2c.vaiheet,\
    $(I2C_STUB) $(B)/05-i2c/lampo.ko,i2c-aseta,))

# --- 06: SPI ------------------------------------------------------------
$(B)/06-spi/vspi.ko $(B)/06-spi/muisti.ko: $(B)/06-spi/valmis
	test -f $@
$(eval $(call TESTI,06-spi,06-spi/spi.vaiheet,\
    $(B)/06-spi/vspi.ko $(B)/06-spi/muisti.ko,heksa,))

# --- 07: kellot, säätimet, GPIO ja virranhallinta -----------------------
# GPIO-simulaattori ja kiinteä säädin ovat ytimessä; kello ja anturin
# kaksi ajuria ovat tutoriaalin moduuleja. Laitepuuhun lisätään linjat,
# säädin, kello ja anturi.
R07 := $(B)/07-resurssit
$(R07)/kello.ko $(R07)/paine.ko $(R07)/paine_pm.ko: $(R07)/valmis
	test -f $@
$(B)/paine.dtb: $(B)/virt.dts 07-resurssit/paine.dtsi
	cat $^ | dtc -q -I dts -O dtb -o $@ -
PAINE := -d $(B)/paine.dtb

$(eval $(call TESTI,07-resurssit,07-resurssit/resurssit.vaiheet,\
    $(R07)/kello.ko $(R07)/paine.ko,,PAINE))
$(eval $(call TESTI,07-ajonaikainen,07-resurssit/ajonaikainen.vaiheet,\
    $(R07)/kello.ko $(R07)/paine_pm.ko,tila,PAINE))
$(eval $(call TESTI,07-lepotila,07-resurssit/lepotila.vaiheet,\
    $(R07)/kello.ko $(R07)/paine_pm.ko,tila,PAINE))
$(B)/07-resurssit.raaka $(B)/07-ajonaikainen.raaka \
    $(B)/07-lepotila.raaka: $(B)/paine.dtb
# devices_deferred erottaa laitteen ja syyn sarkaimella.
$(B)/07-resurssit.uusi: $(B)/07-resurssit.raaka
	expand -t 16 $< | $(TAITA) > $@

# --- 08: vianetsintä ----------------------------------------------------
VIKA := $(B)/08-vianetsinta/vika.ko
$(VIKA): $(B)/08-vianetsinta/valmis
	test -f $@
$(eval $(call TESTI,08-dyndbg,08-vianetsinta/dyndbg.vaiheet,$(VIKA),,))
$(eval $(call TESTI,08-ftrace,08-vianetsinta/ftrace.vaiheet,$(VIKA),,))
$(eval $(call TESTI,08-oops,08-vianetsinta/oops.vaiheet,$(VIKA),\
    kirjoita,))
$(eval $(call TESTI,08-lukot,08-vianetsinta/lukot.vaiheet,$(VIKA),,))

# Jäljityksen riveiltä poistetaan prosessinumero, aika ja liput.
# @alku jalki
$(B)/08-ftrace.uusi: $(B)/08-ftrace.raaka
	sed -E 's/^ +[^ ]+-[0-9]+ +\[[0-9]+\] [^ ]+ +[0-9.]+: /  /' $< | \
	    grep -v '^  #' > $@
# @loppu jalki

# Kaatumisilmoituksen osoite muunnetaan lähdekoodin riviksi isännällä.
# @alku faddr2line
$(B)/08-oops.uusi: $(B)/08-oops.raaka $(VIKA)
	sed -E 's/\+0x[0-9a-f]+\/0x[0-9a-f]+/+.../; s/PID: [0-9]+/PID: .../' \
	    $< | $(TAITA) > $@
	echo "faddr2line:" >> $@
	kohta=$$(sed -n 's/.*pc : \([a-z_]*+0x[0-9a-f]*\/0x[0-9a-f]*\).*/\1/p' \
	    $< | head -1); \
	CROSS_COMPILE=$(RISTI) $(LAHDE)/scripts/faddr2line $(VIKA) "$$kohta" \
	    | sed -n 's|.* at .*/\([^/]*:[0-9]*\).*|  \1|p' >> $@
# @loppu faddr2line

$(B)/08-lukot.uusi: $(B)/08-lukot.raaka
	$(TAITA) $< > $@

.SECONDARY:

# --- käsiajo ------------------------------------------------------------
aja: $(B)/$(T).cpio.gz $(IMAGE)
	$(QEMU) -t 600 -k $(IMAGE) -i $< -a "console=ttyAMA0 panic=-1"

siivoa:
	rm -rf $(B)
