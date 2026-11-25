# Laitteiston kuvausstandardit: esimerkit.
#
#   make              tarkistaa Pythonin (ruff, mypy --strict), ajaa
#                     yksikkötestit ja esimerkit ja vertaa tulosteita
#                     tiedostoihin *.odotettu
#   make 05-regblock  ajaa yhden esimerkin
#   make tuota        tuottaa hakemiston tuotettu/ kuvauksista
#   make paivita      kirjoittaa odotetut tulosteet uudelleen (vain kun
#                     muutos on tarkistettu käsin)
#
# Esimerkit ajavat työkalut väliaikaisissa hakemistoissa, joten ne voi
# ajaa rinnakkain (-j). Verilatorin sisäinen Make ei peri ulomman Maken
# MAKEFLAGS-muuttujaa (kuvaus/ajo.py).

PYTHON    ?= python3
ESIMERKIT := $(basename $(wildcard [0-9][0-9]-*.py))
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: kaikki tarkista testit kaavio tuota paivita siivoa $(ESIMERKIT)

kaikki: tarkista testit kaavio $(ESIMERKIT)

tarkista:
	@ruff check --no-cache .
	@mypy --no-incremental --cache-dir=/dev/null .

testit:
	@$(PYTHON) -m pytest -q

$(ESIMERKIT):
	@tulos=$$($(PYTHON) $@.py) || { echo "VIRHE: $@ kaatui"; exit 1; }; \
	printf '%s\n' "$$tulos" | diff -u $@.odotettu - \
	    || { echo "VIRHE: $@ poikkeaa odotetusta"; exit 1; }; \
	echo "OK: $@"

# Kirjan ajoituskaaviot (luku 4) tuotetaan tapahtumat-lohkon
# testipenkin VCD:stä repositorion yhteisellä työkalulla ja verrataan
# tallennettuihin. PAIVITA=1 kirjoittaa ne uudelleen. Zip-paketissa
# työkalua ei ole, jolloin tarkistus ohitetaan.
KAAVIOTYOKALU := ../../yhteiset/kaaviot.py
K    := .kaaviot
VCD  := $(PYTHON) $(KAAVIOTYOKALU) vcd $(K)/tapahtumat.vcd --kello clk \
        --naytteistys ennen
PULSSI_S := psel=PSEL,penable=PENABLE,pwrite=PWRITE,paddr=PADDR
PULSSI_S := $(PULSSI_S),pwdata=PWDATA,pready=PREADY,j_kaynnista=KAYNNISTA
KESK_S := j_hwset=VIRHE.hwset,j_virhe=KESKEYTYS.VIRHE,psel=PSEL
KESK_S := $(KESK_S),penable=PENABLE,pwrite=PWRITE,paddr=PADDR
KESK_S := $(KESK_S),j_salli=SALLI.VIRHE,j_intr=intr
kaavio:
	@if [ ! -f $(KAAVIOTYOKALU) ]; then echo "OHITETTU: kaavio"; exit 0; fi; \
	mkdir -p $(K) && \
	MAKEFLAGS= verilator --binary --timing -Wall -Itb --trace -DJALJITYS \
	    --top-module tapahtumat_tb -Mdir $(K)/obj -o sim tb/tuotettu.vlt \
	    tuotettu/tapahtumat_pkg.sv tuotettu/tapahtumat.sv \
	    tb/tapahtumat_tb.sv > $(K)/kaannos.log 2>&1 && \
	$(K)/obj/sim +vcd=$(K)/tapahtumat.vcd > /dev/null && \
	$(VCD) --alku 3 --jaksot 6 --signaalit $(PULSSI_S) \
	    > $(K)/kertapulssi.json && \
	$(VCD) --alku 70030 --jaksot 15 --signaalit $(KESK_S) \
	    > $(K)/keskeytys.json && \
	rm -f $(K)/tapahtumat.vcd && \
	for k in kertapulssi keskeytys; do \
	    if [ "$(PAIVITA)" = 1 ]; then cp $(K)/$$k.json kaaviot/; fi; \
	    diff -u kaaviot/$$k.json $(K)/$$k.json || exit 1; \
	done && echo "OK: kaavio"

tuota:
	@$(PYTHON) 11-tahdissa.py --kirjoita

paivita:
	@for e in $(ESIMERKIT); do $(PYTHON) $$e.py > $$e.odotettu || exit 1; done

siivoa:
	@rm -rf __pycache__ kuvaus/__pycache__ testit/__pycache__ \
	    .mypy_cache .ruff_cache .pytest_cache .kaaviot
