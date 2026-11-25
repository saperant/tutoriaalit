# EDA-työkaluketjujen automatisointi: esimerkit.
#
#   make              tarkistaa Pythonin (ruff, mypy --strict), ajaa
#                     yksikkötestit ja esimerkit ja vertaa tulosteita
#                     tiedostoihin *.odotettu
#   make 07-regressio ajaa yhden esimerkin
#   make paivita      kirjoittaa odotetut tulosteet uudelleen (vain kun
#                     muutos on tarkistettu käsin)
#
# Esimerkit ajavat työkalut tilapäishakemistoissa, joten ne voi ajaa
# rinnakkain (-j). Ulomman Maken MAKEFLAGS poistetaan työkalujen omista
# Make-kutsuista (vuo/ajo.py ja 02-make.py).

PYTHON    ?= python3
ESIMERKIT := $(basename $(wildcard [0-9][0-9]-*.py))
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: kaikki tarkista testit kaavio paivita siivoa $(ESIMERKIT)

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

# Kirjan ajoituskaavio (luku 5) tuotetaan saman testipenkin VCD:stä
# repositorion yhteisellä työkalulla ja verrataan tallennettuun.
# PAIVITA=1 kirjoittaa sen uudelleen. Zip-paketissa työkalua ei ole,
# jolloin tarkistus ohitetaan.
KAAVIOTYOKALU := ../../yhteiset/kaaviot.py
KAAVIOHAK     := .kaaviot
kaavio:
	@if [ ! -f $(KAAVIOTYOKALU) ]; then echo "OHITETTU: kaavio"; exit 0; fi; \
	mkdir -p $(KAAVIOHAK) && \
	iverilog -g2012 -s laskuri_tb -o $(KAAVIOHAK)/sim.vvp rtl/laskuri.sv \
	    tb/laskuri_tb.sv && \
	vvp -n $(KAAVIOHAK)/sim.vvp +vcd=$(KAAVIOHAK)/laskuri.vcd > /dev/null && \
	$(PYTHON) $(KAAVIOTYOKALU) vcd $(KAAVIOHAK)/laskuri.vcd --kello clk \
	    --signaalit rst_n,sallittu,arvo,yli --kanta d --alku 1 \
	    --jaksot 14 > $(KAAVIOHAK)/laskuri.json && \
	{ [ "$(PAIVITA)" != 1 ] || cp $(KAAVIOHAK)/laskuri.json kaaviot/; } && \
	diff -u kaaviot/laskuri.json $(KAAVIOHAK)/laskuri.json && \
	echo "OK: kaavio"

paivita:
	@for e in $(ESIMERKIT); do $(PYTHON) $$e.py > $$e.odotettu || exit 1; done

siivoa:
	@rm -rf __pycache__ vuo/__pycache__ testit/__pycache__ .mypy_cache \
	    .ruff_cache \
	    .kaaviot
