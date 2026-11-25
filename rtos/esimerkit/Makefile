# Reaaliaikakäyttöjärjestelmät: Kide-ydin ja esimerkit.
#
#   make              kääntää esimerkit Cortex-M3:lle ja ajaa ne QEMU:ssa
#                     (mps2-an385), kääntää osan myös isäntäkoneelle
#                     sanitoijin ja vertaa molempien tulosteen ja
#                     paluuarvon tiedostoon testit/<esimerkki>.odotettu
#   make aja E=01-tehtavat   ajaa yhden esimerkin QEMU:ssa
#   make siivoa       poistaa build/-hakemiston

# @alku liput
CC      := arm-none-eabi-gcc
CFLAGS   = -mcpu=cortex-m3 -mthumb -Os -g -std=c11 \
           -Wall -Wextra -Werror -ffreestanding \
           -ffunction-sections -fdata-sections -Iyhteinen -Ikide
LDFLAGS := -Tyhteinen/laite.ld -nostartfiles \
           --specs=nano.specs --specs=nosys.specs -Wl,--gc-sections
# -icount: virtuaaliaika etenee käskyjen mukaan, ei seinäkellon.
# Ajo on joka kerta käsky käskyltä sama, eikä koneen kuorma vaikuta.
QEMU    := qemu-system-arm -M mps2-an385 -nographic -monitor none \
           -serial stdio -semihosting-config enable=on,target=native \
           -icount shift=3,align=off,sleep=off
# @loppu liput
AIKARAJA := timeout 60

# @alku isanta
ISANTA_CC     := cc
ISANTA_CFLAGS := -std=c11 -D_GNU_SOURCE -DKIDE_ISANTA -g -O1 \
                 -Wall -Wextra -Werror -Iyhteinen -Ikide \
                 -fsanitize=address,undefined -fno-sanitize-recover=all
YDIN          := kide/lista.c kide/tehtava.c kide/jono.c \
                 kide/tapahtumat.c kide/muisti.c yhteinen/aikajana.c \
                 isanta/portti_isanta.c isanta/konsoli_isanta.c
# @loppu isanta
KIDE     := $(wildcard kide/*.c) $(wildcard kide/*.h)
YHTEINEN := $(wildcard yhteinen/*.c) $(wildcard yhteinen/*.h) \
            yhteinen/laite.ld
ISANTA_L := $(wildcard isanta/*.c)

ESIMERKIT := $(patsubst %/main.c,%,$(wildcard [0-9][0-9]-*/main.c))
VARIANTIT := 04-vuorottelu-ei 13-inversio-mutex 14-rms-ylikuorma
# Nämä esimerkit eivät käytä laitteistoa, joten ne ajetaan myös
# isäntäportilla.
ISANTA    := 01-tehtavat 02-jakso 03-etuoikeutus 04-vuorottelu 08-jono \
             10-semafori 11-tapahtumat 12-ilmoitus 13-inversio \
             14-rms 17-ajastimet \
             $(VARIANTIT)

# Kirjan ajoituskaaviot, jotka tuotetaan testatuista tulosteista.
KAAVIOT   := 13-inversio 13-inversio-mutex 14-rms 14-rms-ylikuorma

TESTIT := $(ESIMERKIT:%=build/%.tulos) $(VARIANTIT:%=build/%.tulos) \
          $(ISANTA:%=build/isanta/%.tulos) $(KAAVIOT:%=build/%.kaavio)

.PHONY: kaikki aja siivoa
.SECONDARY:
kaikki: $(TESTIT)

build build/isanta:
	mkdir -p $@

# @alku rakennus
build/%.elf: %/*.c $(KIDE) $(YHTEINEN) | build
	$(CC) $(CFLAGS) $(wildcard $*/*.c) $(filter %.c,$(KIDE) $(YHTEINEN)) \
	    $(LDFLAGS) -Wl,-Map=build/$*.map -o $@

build/isanta/%: %/*.c $(KIDE) $(ISANTA_L) | build/isanta
	$(ISANTA_CC) $(ISANTA_CFLAGS) $(wildcard $*/*.c) $(YDIN) -o $@

# Muunnelma: sama lähdekoodi, eri käännösvalitsimet.
define muunnelma
build/$(1).elf: $(2)/*.c $$(KIDE) $$(YHTEINEN) | build
	$$(CC) $$(CFLAGS) $(3) $$(wildcard $(2)/*.c) \
	    $$(filter %.c,$$(KIDE) $$(YHTEINEN)) $$(LDFLAGS) -o $$@
build/isanta/$(1): $(2)/*.c $$(KIDE) $$(ISANTA_L) | build/isanta
	$$(ISANTA_CC) $$(ISANTA_CFLAGS) $(3) $$(wildcard $(2)/*.c) \
	    $$(YDIN) -o $$@
endef
$(eval $(call muunnelma,04-vuorottelu-ei,04-vuorottelu,\
    -DconfigUSE_TIME_SLICING=0))
$(eval $(call muunnelma,13-inversio-mutex,13-inversio,-DMUTEX))
$(eval $(call muunnelma,14-rms-ylikuorma,14-rms,-DYLIKUORMA))
# @loppu rakennus

# @alku ajo
syote = $(firstword $(wildcard $(1)/syote.txt) /dev/null)

build/%.tulos: build/%.elf testit/%.odotettu
	{ $(AIKARAJA) $(QEMU) -kernel $< < $(call syote,$*); \
	  echo "paluuarvo $$?"; } > $@.tmp 2>&1
	diff -u testit/$*.odotettu $@.tmp
	mv $@.tmp $@

# Isäntäkoneella sama odotettu tuloste kuin QEMU:ssa. Sanitoijien
# ilmoitukset menevät virhetulosteeseen, joka näytetään vain, jos
# vertailu epäonnistuu.
build/isanta/%.tulos: build/isanta/% testit/%.odotettu
	{ $(AIKARAJA) ./$< < /dev/null 2> $@.virheet; \
	  echo "paluuarvo $$?"; } > $@.tmp
	diff -u testit/$*.odotettu $@.tmp || { cat $@.virheet; false; }
	mv $@.tmp $@
# @loppu ajo

# @alku kaaviot
# Ajoituskaavio tuotetaan odotetusta tulosteesta ja verrataan kirjassa
# näytettyyn tiedostoon kaaviot/<nimi>.json. Jos tuloste muuttuu,
# kaavio on tuotettava uudelleen: python3 kaaviot/tee.py LAJI TULOSTE
laji = $(if $(findstring inversio,$(1)),inversio,rms)

build/%.kaavio: testit/%.odotettu kaaviot/%.json kaaviot/tee.py | build
	python3 kaaviot/tee.py $(call laji,$*) $< > $@.tmp
	diff -u kaaviot/$*.json $@.tmp
	mv $@.tmp $@
# @loppu kaaviot

aja: build/$(E).elf
	$(QEMU) -kernel $<

siivoa:
	rm -rf build
