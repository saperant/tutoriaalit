# LT-100-lämpötilaloggerin laiteohjelmisto (valmistajan puoli).
#
#   make B=hakemisto   rakentaa käynnistyslataimen, sovelluksen
#                      muunnelmat, flash-kuvat ja päivityspaketin
#
# Analyysiesimerkit käyttävät vain tuotteita (flash-kuvat, paketti),
# eivät lähdekoodia: lähteet ovat tarinan mukaan kadonneet. ELF-
# tiedostoilla tarkistetaan päättelyjen oikeellisuus.

B ?= ../build/laite

# @alku liput
CC      := arm-none-eabi-gcc
OBJCOPY := arm-none-eabi-objcopy
CFLAGS  := -mcpu=cortex-m3 -mthumb -Os -g -std=c11 \
           -Wall -Wextra -Werror -ffreestanding \
           -ffunction-sections -fdata-sections \
           -ffile-prefix-map=$(CURDIR)=.
LDFLAGS := -nostartfiles --specs=nano.specs --specs=nosys.specs \
           -Wl,--gc-sections
# @loppu liput

YHTEISET := tarkiste.c konsoli.c semihost.c
BOOT     := boot.c $(YHTEISET)
SOVELLUS := kaynnistys.c sovellus.c komennot.c asetukset.c xtea.c \
            suodatin.c loki.c kehys.c tehtavat.c $(YHTEISET)
OTSAKKEET := $(wildcard *.h)

TUOTTEET := $(addprefix $(B)/, boot.elf boot-korjattu.elf \
    sovellus.elf sovellus-240.elf sovellus-korjattu.elf \
    sovellus-rikki.elf flash.bin flash-240.bin flash-rikki.bin \
    flash-korjattu.bin lt100-2.4.1.lt1)

.PHONY: kaikki
kaikki: $(TUOTTEET)

$(B):
	mkdir -p $@

# @alku elf
$(B)/boot.elf: $(BOOT) $(OTSAKKEET) boot.ld | $(B)
	$(CC) $(CFLAGS) $(BOOT) -Tboot.ld $(LDFLAGS) -o $@
$(B)/boot-korjattu.elf: $(BOOT) $(OTSAKKEET) boot.ld | $(B)
	$(CC) $(CFLAGS) -DKORJATTU $(BOOT) -Tboot.ld $(LDFLAGS) -o $@

SOVELLUS_CFLAGS := $(CFLAGS) -fstack-protector-strong
$(B)/sovellus.elf: $(SOVELLUS) $(OTSAKKEET) sovellus.ld | $(B)
	$(CC) $(SOVELLUS_CFLAGS) $(SOVELLUS) -Tsovellus.ld $(LDFLAGS) -o $@
# @loppu elf
$(B)/sovellus-240.elf: $(SOVELLUS) $(OTSAKKEET) sovellus.ld | $(B)
	$(CC) $(SOVELLUS_CFLAGS) -DVERSIO_240 $(SOVELLUS) -Tsovellus.ld \
	    $(LDFLAGS) -o $@
$(B)/sovellus-korjattu.elf: $(SOVELLUS) $(OTSAKKEET) sovellus.ld | $(B)
	$(CC) $(SOVELLUS_CFLAGS) -DKORJATTU $(SOVELLUS) -Tsovellus.ld \
	    $(LDFLAGS) -o $@
$(B)/sovellus-rikki.elf: $(SOVELLUS) $(OTSAKKEET) sovellus-rikki.ld | $(B)
	$(CC) $(SOVELLUS_CFLAGS) $(SOVELLUS) -Tsovellus-rikki.ld \
	    $(LDFLAGS) -o $@

$(B)/%.bin: $(B)/%.elf
	$(OBJCOPY) -O binary $< $@

# Tehtaan asetuslohkot: tavallinen ja korjattu (debug lukittu, ei
# huoltosalasanaa).
$(B)/asetukset.bin: asetukset.py | $(B)
	python3 asetukset.py $@
$(B)/asetukset-korjattu.bin: asetukset.py | $(B)
	python3 asetukset.py --korjattu $@

# @alku flash
# Flash-kuva: käynnistyslatain, sovelluksen otsake, sovellus ja
# asetuslohko yhdessä tiedostossa (256 kt).
$(B)/flash.bin: flash.py $(B)/boot.bin $(B)/sovellus.bin \
                $(B)/asetukset.bin
	python3 flash.py $@ $(B)/boot.bin $(B)/sovellus.bin \
	    $(B)/asetukset.bin 2.4.1
# @loppu flash
$(B)/flash-240.bin: flash.py $(B)/boot.bin $(B)/sovellus-240.bin \
                    $(B)/asetukset.bin
	python3 flash.py $@ $(B)/boot.bin $(B)/sovellus-240.bin \
	    $(B)/asetukset.bin 2.4.0
$(B)/flash-rikki.bin: flash.py $(B)/boot.bin $(B)/sovellus-rikki.bin \
                      $(B)/asetukset.bin
	python3 flash.py $@ $(B)/boot.bin $(B)/sovellus-rikki.bin \
	    $(B)/asetukset.bin 2.4.1
$(B)/flash-korjattu.bin: flash.py $(B)/boot-korjattu.bin \
        $(B)/sovellus-korjattu.bin $(B)/asetukset-korjattu.bin
	python3 flash.py $@ $(B)/boot-korjattu.bin \
	    $(B)/sovellus-korjattu.bin $(B)/asetukset-korjattu.bin 2.4.2

$(B)/lt100-2.4.1.lt1: pakkaa.py ohje.txt $(B)/sovellus.bin \
                      $(B)/asetukset.bin
	python3 pakkaa.py $@ 2.4.1 $(B)/sovellus.bin $(B)/asetukset.bin \
	    ohje.txt
