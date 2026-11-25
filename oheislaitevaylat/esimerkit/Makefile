# Oheislaiteväylät: esimerkit.
#
#   make              kääntää Cortex-M-ohjelmat ja ajaa ne QEMU:ssa,
#                     kääntää ja ajaa ajurien isäntätestit, tarkistaa
#                     Python-mallit (ruff, mypy --strict, pytest) ja
#                     ajaa ne; jokainen tuloste verrataan tiedostoon
#                     testit/<nimi>.odotettu
#   make aja E=05-i2c ajaa yhden ohjelman päätteessä
#   make siivoa       poistaa build/-hakemiston ja välimuistit
#
# Ajot eivät riipu ajoituksesta, joten ne voi ajaa rinnakkain (-j).

# @alku liput
CC      := arm-none-eabi-gcc
CFLAGS   = -mthumb -Os -g -std=c11 -Wall -Wextra -Werror \
           -ffreestanding -ffunction-sections -fdata-sections \
           -Iyhteinen -Iajurit
LDFLAGS := -Lyhteinen -nostartfiles --specs=nano.specs \
           --specs=nosys.specs -Wl,--gc-sections
# @loppu liput
AN385   := -mcpu=cortex-m3 -Tan385.ld
AN505   := -mcpu=cortex-m33 -DAN505 -Tan505.ld

# @alku laitteet
# Laboratorion laitteet: QEMU kytkee ne mps2-an385:n viimeksi
# luotuihin I2C- ja SPI-väyliin (I2C_ANTURIT ja SPI_ADC, ks. mps2.h).
LAITTEET := -device tmp105,bus=i2c,address=0x48 \
            -device at24c-eeprom,bus=i2c,address=0x50,rom-size=256 \
            -device max1111,bus=ssi,input0=0,input1=127,input2=200,input3=255
QEMU     := qemu-system-arm -nographic -monitor none -serial stdio \
            -semihosting-config enable=on,target=native
# UART1 lukee syötteensä tiedostosta ja kirjoittaa toiseen.
uart1 = -chardev file,id=uart1,path=build/$(1).uart1,input-path=$(2) \
        -serial chardev:uart1
# @loppu laitteet
AIKARAJA := timeout 30
PYTHON   ?= python3
export PYTHONDONTWRITEBYTECODE := 1

YHTEINEN := $(wildcard yhteinen/*.c) $(wildcard yhteinen/*.h) \
            $(wildcard yhteinen/*.ld) $(wildcard ajurit/*.h)

# Ohjelmat ja niiden käyttämät ajurit.
AN385_OHJELMAT := 01-tunnistus 02-lahetys 02-lahetys-virhe 03-kehykset \
                  04-spi-adc 05-i2c 06-eeprom
ajurit_04-spi-adc := ajurit/pl022.c
ajurit_05-i2c     := ajurit/i2c_sbcon.c ajurit/i2c.c
ajurit_06-eeprom  := ajurit/i2c_sbcon.c ajurit/i2c.c ajurit/at24.c

ISANTA  := at24-testi at24-testi-sivuvirhe pl022-testi
TULOKSET := $(AN385_OHJELMAT:%=build/%.tulos) build/07-dma.tulos \
            $(ISANTA:%=build/%.tulos) build/03-kehykset-isanta.tulos

.PHONY: kaikki python aja siivoa
kaikki: $(TULOKSET) python

build:
	mkdir -p $@

# @alku rakennus
.SECONDEXPANSION:
build/%.elf: $$(wildcard %/*.c %/*.h) $$(ajurit_$$*) $(YHTEINEN) | build
	$(CC) $(CFLAGS) $(AN385) $(filter %.c,$^) $(LDFLAGS) -o $@
build/02-lahetys-virhe.elf: 02-lahetys/main.c $(YHTEINEN) | build
	$(CC) $(CFLAGS) $(AN385) -DILMAN_KAYNNISTYSTA $(filter %.c,$^) \
	    $(LDFLAGS) -o $@
build/07-dma.elf: 07-dma/main.c 07-dma/pl081.h $(YHTEINEN) | build
	$(CC) $(CFLAGS) $(AN505) $(filter %.c,$^) $(LDFLAGS) -o $@
# @loppu rakennus

# @alku ajo
# Ajo: tuloste ja paluuarvo verrataan odotettuun.
build/%.tulos: build/%.elf testit/%.odotettu
	{ $(AIKARAJA) $(QEMU) -M mps2-an385 $(LAITTEET) \
	    $(call uart1,$*,/dev/null) -kernel $<; \
	  echo "paluuarvo $$?"; } > $@.tmp 2>&1
	diff -u testit/$*.odotettu $@.tmp
	mv $@.tmp $@
# @loppu ajo

# Testattu QEMU 8.2.2:lla: sen mps2-an505-mallissa PL081:n keskeytys ei
# näy NVIC:ssä, joten esimerkki pollaa valmistumisbittiä (ks. luku 7).
build/07-dma.tulos: build/07-dma.elf testit/07-dma.odotettu
	{ $(AIKARAJA) $(QEMU) -M mps2-an505 -kernel $<; \
	  echo "paluuarvo $$?"; } > $@.tmp 2>&1
	diff -u testit/07-dma.odotettu $@.tmp
	mv $@.tmp $@

# @alku kehykset
# Kehysprotokolla: Python-malli tuottaa isännän tavut, laite vastaa,
# ja malli purkaa vastaukset.
build/03-kehykset.syote: python/kehykset.py python/mallit/kehys.py | build
	$(PYTHON) python/kehykset.py tuota $@
build/03-kehykset.tulos: build/03-kehykset.elf build/03-kehykset.syote \
                         testit/03-kehykset.odotettu
	{ $(AIKARAJA) $(QEMU) -M mps2-an385 \
	    $(call uart1,03-kehykset,build/03-kehykset.syote) -kernel $<; \
	  echo "paluuarvo $$?"; } > $@.tmp 2>&1
	diff -u testit/03-kehykset.odotettu $@.tmp
	mv $@.tmp $@
build/03-kehykset-isanta.tulos: build/03-kehykset.tulos \
                                testit/03-kehykset-isanta.odotettu
	$(PYTHON) python/kehykset.py pura build/03-kehykset.uart1 > $@.tmp
	diff -u testit/03-kehykset-isanta.odotettu $@.tmp
	mv $@.tmp $@
# @loppu kehykset

# @alku isanta
# Ajurien testit isäntäkoneella sanitoijien kanssa.
ISANTA_CC := cc -std=c11 -Wall -Wextra -Werror -g \
             -fsanitize=address,undefined -fno-sanitize-recover=all \
             -Iajurit -Iyhteinen
build/at24-testi: isanta/at24_testi.c ajurit/at24.c ajurit/i2c.c \
                  ajurit/at24.h ajurit/i2c.h | build
	$(ISANTA_CC) $(filter %.c,$^) -o $@
build/at24-testi-sivuvirhe: isanta/at24_testi.c ajurit/at24.c \
                            ajurit/i2c.c ajurit/at24.h | build
	$(ISANTA_CC) -DSIVUVIRHE $(filter %.c,$^) -o $@
build/pl022-testi: isanta/pl022_testi.c ajurit/pl022.c ajurit/pl022.h \
                   yhteinen/mps2.h | build
	$(ISANTA_CC) $(filter %.c,$^) -o $@
$(ISANTA:%=build/%.tulos): build/%.tulos: build/% testit/%.odotettu
	{ ./$<; echo "paluuarvo $$?"; } > $@.tmp 2>&1
	diff -u testit/$*.odotettu $@.tmp
	mv $@.tmp $@
# @loppu isanta

# Python-mallit: tarkistukset, yksikkötestit ja esimerkit.
python:
	$(MAKE) -C python -s

aja: build/$(E).elf
	$(QEMU) -M mps2-an385 $(LAITTEET) $(call uart1,$(E),/dev/null) \
	    -kernel $<

siivoa:
	rm -rf build
	$(MAKE) -C python -s siivoa
