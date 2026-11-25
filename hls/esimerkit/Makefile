# minihls ja sen esimerkit.
#
#   make           tarkistaa minihls:n (ruff, mypy --strict, ShellCheck)
#                  ja ajaa kaikki esimerkit (rinnakkain valitsimella -j)
#   make 07-matriisi   vain yksi esimerkki
#   make siivoa    poistaa hakemiston rakennus/
#
# Esimerkin vuo on kuvattu tiedostossa testaa.sh.

ESIMERKIT := $(sort $(wildcard [0-9][0-9]-*))

.PHONY: kaikki tarkistukset siivoa $(ESIMERKIT)

kaikki: $(ESIMERKIT) kaaviot
	@echo "OK: $(words $(ESIMERKIT)) esimerkkiä"

# Kirjan kaaviot tuotetaan minihls:llä ja simulaatiosta ja verrataan
# hakemiston kaaviot/ tiedostoihin. PAIVITA=1 kirjoittaa ne uudelleen.
#   kaaviot/diffeq-askel.dot   ajoitettu tietovuograafi (minihls --dot)
#   kaaviot/mac-ap-ctrl.json   01-mac:n kättely Verilatorin VCD:stä
#   kaaviot/luma-lohko1.dot    02-etupaa:n tietovuograafi ajoitettuna
#   kaaviot/mac-putki.json     sama 06-liukuhihnan RTL:llä (II = 1)
#   kaaviot/fir-virta.json     09-fir:n AXI-Stream-kättely vastapaineella
# Simulaation kääre ja kaaviot.py:n valitsimet ovat tiedostossa
# kaaviot/<nimi>.kaavio (otsakerivit lahde: ja vcd:).
KAAVIOTYOKALU := $(abspath ../../yhteiset/kaaviot.py)
KR := rakennus/kaaviot
SIMULOIDUT := mac-ap-ctrl mac-putki fir-virta
.PHONY: kaaviot
kaaviot: tarkistukset
	@mkdir -p $(KR)
	@python3 -m minihls 03-ajoitus/diffeq.cpp --top diffeq --dot askel \
	    > $(KR)/diffeq-askel.dot
	@python3 -m minihls 02-etupaa/luma.cpp --top luma --dot lohko1 \
	    > $(KR)/luma-lohko1.dot
	@python3 -m minihls 06-liukuhihna/mac_putki.cpp --top mac \
	    --ulos $(KR)/putki > /dev/null
	@for k in $(SIMULOIDUT); do \
	    mkdir -p $(KR)/$$k && cp kaaviot/$$k.kaavio $(KR)/$$k/kaavio.sv && \
	    verilator --binary --trace --top-module kaavio -Wno-fatal \
	        -Mdir $(KR)/$$k/obj -o sim \
	        $$(sed -n 's#^// lahde: ##p' kaaviot/$$k.kaavio) \
	        $(KR)/$$k/kaavio.sv > $(KR)/$$k/verilator.log 2>&1 \
	        || { cat $(KR)/$$k/verilator.log; exit 1; }; \
	    (cd $(KR)/$$k && timeout 60 ./obj/sim > /dev/null) || exit 1; \
	    python3 $(KAAVIOTYOKALU) vcd $(KR)/$$k/kaavio.vcd \
	        $$(sed -n 's#^// vcd: ##p' kaaviot/$$k.kaavio) \
	        > $(KR)/$$k.json || exit 1; \
	done
	@for k in diffeq-askel.dot luma-lohko1.dot $(SIMULOIDUT:%=%.json); do \
	    if [ "$(PAIVITA)" = 1 ]; then cp $(KR)/$$k kaaviot/$$k; fi; \
	    diff -u kaaviot/$$k $(KR)/$$k \
	        || { echo "kaavio $$k ei vastaa (PAIVITA=1)"; exit 1; }; \
	done
	@echo "OK: kaaviot"

tarkistukset:
	ruff check --no-cache -q minihls tyokalut
	mypy --strict --no-error-summary --cache-dir=rakennus/mypy \
	    minihls tyokalut
	shellcheck testaa.sh

$(ESIMERKIT): tarkistukset
	@./testaa.sh $@

siivoa:
	rm -rf rakennus
