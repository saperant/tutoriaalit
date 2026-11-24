# Ajoituskaaviot simulaatiosta.
#
# Kirjan ajoituskaaviot ovat tiedostoja kaaviot/*.json. Tämä Makefile
# tuottaa ne uudelleen simuloimalla esimerkit ja vertaa tulosta
# tallennettuun, joten kaavio ei voi erkaantua koodista.
#
#   make           tarkistaa kaaviot (ajetaan osana make testaa)
#   make paivita   kirjoittaa kaaviot/*.json uudelleen
#   make siivoa    poistaa käännöstuotteet
#
# Simuloitavan kaavion kuvaus on tiedostossa kaaviot/<nimi>.kaavio: se on
# SystemVerilog-kääre, joka instansioi esimerkin testipenkin, tuo
# näytettävät signaalit omiksi johdoikseen ja kirjoittaa VCD-tiedoston.
# Otsakerivit kertovat lähteet ja kaaviot.py:n valitsimet:
#
#   // lahde: 09-laskurit.sv
#   // vcd: --kello clk --signaalit sarja,q0 --jaksot 9

KAAVIOT := $(abspath ../../yhteiset/kaaviot.py)
RAK     := build
SIMULOIDUT := $(patsubst kaaviot/%.kaavio,%,$(wildcard kaaviot/*.kaavio))
TARKISTUKSET := $(SIMULOIDUT:%=$(RAK)/%.ok)

.PHONY: kaikki paivita siivoa
kaikki: $(TARKISTUKSET)

# Kaavio simuloidaan Verilatorilla omassa hakemistossaan.
$(RAK)/%.json: kaaviot/%.kaavio $(wildcard *.sv */*.sv) $(KAAVIOT)
	@rm -rf $(RAK)/$* && mkdir -p $(RAK)/$*
	@cp $< $(RAK)/$*/kaavio.sv
	@lahteet=$$(sed -n 's#^// lahde: ##p' $<); \
	verilator --binary --trace --top-module kaavio -Wno-fatal \
	    -Mdir $(RAK)/$*/obj -o sim $$lahteet $(RAK)/$*/kaavio.sv \
	    > $(RAK)/$*/verilator.log 2>&1 \
	    || { cat $(RAK)/$*/verilator.log; exit 1; }
	@cd $(RAK)/$* && timeout 120 ./obj/sim > sim.log \
	    || { echo "kaavion $* simulointi epäonnistui"; exit 1; }
	@python3 $(KAAVIOT) vcd $(RAK)/$*/kaavio.vcd \
	    $$(sed -n 's#^// vcd: ##p' $<) > $@

$(RAK)/%.ok: $(RAK)/%.json kaaviot/%.json
	@diff -u kaaviot/$*.json $< \
	    || { echo "kaavio $* ei vastaa simulaatiota: make paivita"; exit 1; }
	@touch $@

paivita: $(SIMULOIDUT:%=$(RAK)/%.json)
	@for k in $(SIMULOIDUT); do \
	    cp $(RAK)/$$k.json kaaviot/$$k.json; done

siivoa:
	rm -rf $(RAK)
