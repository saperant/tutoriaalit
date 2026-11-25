# Mikrokontrollerit: esimerkit Cortex-M3:lle (QEMU mps2-an385).
#
#   make              kääntää esimerkit, ajaa ne QEMU:ssa ja vertaa
#                     tulosteen ja paluuarvon tiedostoon
#                     testit/<esimerkki>.odotettu
#   make aja E=01-hei ajaa yhden esimerkin päätteessä
#   make gdb E=01-hei käynnistää esimerkin ja jää odottamaan gdb:tä
#   make siivoa       poistaa build/-hakemiston
#
# gdb-istunto (10-gdb) ajetaan vain, jos gdb-multiarch on asennettu.

# @alku liput
CC      := arm-none-eabi-gcc
OPT     := -Os
CFLAGS   = -mcpu=cortex-m3 -mthumb $(OPT) -g -std=c11 \
           -Wall -Wextra -Werror -ffreestanding \
           -ffunction-sections -fdata-sections -Iyhteinen
LDFLAGS := -Tyhteinen/laite.ld -nostartfiles \
           --specs=nano.specs --specs=nosys.specs -Wl,--gc-sections
QEMU    := qemu-system-arm -M mps2-an385 -nographic -monitor none \
           -serial stdio -semihosting-config enable=on,target=native
# @loppu liput
AIKARAJA := timeout 30

YHTEINEN  := $(wildcard yhteinen/*.c) $(wildcard yhteinen/*.h) \
             yhteinen/laite.ld
ESIMERKIT := $(patsubst %/main.c,%,$(wildcard [0-9][0-9]-*/main.c)) \
             03-kaynnistys-ilman
TESTIT    := $(ESIMERKIT:%=build/%.tulos) build/11-isanta.tulos
GDB       := $(shell command -v gdb-multiarch 2>/dev/null)
ifneq ($(GDB),)
TESTIT    += build/10-gdb-istunto.tulos
endif

.PHONY: kaikki aja gdb siivoa
kaikki: $(TESTIT)
ifeq ($(GDB),)
	@echo "gdb-multiarch puuttuu: gdb-istuntoa 10-gdb ei testattu"
endif

build:
	mkdir -p $@

# @alku rakennus
build/%.elf: %/*.c $(YHTEINEN) | build
	$(CC) $(CFLAGS) $(filter %.c,$^) $(LDFLAGS) \
	    -Wl,-Map=build/$*.map -o $@

# Debugattava esimerkki: optimoinnit, jotka eivät haittaa gdb:tä.
build/10-gdb.elf: OPT := -Og

# Sama käynnistysesimerkki ilman .data-kopiointia ja .bss-nollausta.
build/03-kaynnistys-ilman.elf: 03-kaynnistys/main.c $(YHTEINEN) | build
	$(CC) $(CFLAGS) -DILMAN_ALUSTUSTA $(filter %.c,$^) $(LDFLAGS) -o $@
# @loppu rakennus

# Vahtikoiran aikaraja kuluu QEMU:n virtuaaliajassa. -icount sitoo ajan
# suoritettuihin käskyihin, jolloin kuormitettu isäntäkone ei laukaise
# vahtia väärään aikaan.
build/06-vahtikoira.tulos: QEMU += -icount shift=3,align=off,sleep=off

# @alku ajo
# Ajo: syöte tiedostosta <esimerkki>/syote.txt, jos sellainen on.
syote = $(firstword $(wildcard $(1)/syote.txt) /dev/null)

build/%.tulos: build/%.elf testit/%.odotettu
	{ $(AIKARAJA) $(QEMU) -kernel $< < $(call syote,$*); \
	  echo "paluuarvo $$?"; } > $@.tmp 2>&1
	diff -u testit/$*.odotettu $@.tmp
	mv $@.tmp $@
# @loppu ajo

# Tilakoneen logiikka testataan myös isäntäkoneella.
build/11-isanta: 11-tilakone/isanta/testi.c 11-tilakone/tila.c \
                 11-tilakone/tila.h | build
	cc -std=c11 -Wall -Wextra -Werror -I11-tilakone \
	    $(filter %.c,$^) -o $@
build/11-isanta.tulos: build/11-isanta testit/11-isanta.odotettu
	{ ./$<; echo "paluuarvo $$?"; } > $@.tmp 2>&1
	diff -u testit/11-isanta.odotettu $@.tmp
	mv $@.tmp $@

# @alku gdb-testi
# gdb käynnistää QEMU:n itse ja puhuu sille putken kautta (-gdb stdio).
# Osoitteet ja polut riippuvat kääntäjästä, joten ne suodatetaan.
build/10-gdb-istunto.tulos: build/10-gdb.elf 10-gdb/istunto.gdb \
                            testit/10-gdb-istunto.odotettu
	$(AIKARAJA) $(GDB) -q -batch -nx -x 10-gdb/istunto.gdb $< \
	    2>&1 | sed -E -f 10-gdb/suodata.sed > $@.tmp
	diff -u testit/10-gdb-istunto.odotettu $@.tmp
	mv $@.tmp $@
# @loppu gdb-testi

aja: build/$(E).elf
	$(QEMU) -kernel $<

gdb: build/$(E).elf
	@echo "Toisessa päätteessä: gdb-multiarch $< -ex 'target remote :1234'"
	$(QEMU) -kernel $< -S -s

siivoa:
	rm -rf build
