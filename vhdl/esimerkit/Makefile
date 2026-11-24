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
# VHDL-kääre, joka instansioi esimerkin testipenkin ja tuo näytettävät
# signaalit omiksi signaaleikseen ulkoisilla nimillä (VHDL-2008).
# GHDL kirjoittaa VCD-tiedoston. Otsakerivit kertovat lähteet ja
# kaaviot.py:n valitsimet:
#
#   -- lahde: 07-pwm.vhd
#   -- vcd: --kello kaavio.clk --signaalit kaavio.k0=k0 --jaksot 17

KAAVIOT := $(abspath ../../yhteiset/kaaviot.py)
RAK     := build
SIMULOIDUT := $(patsubst kaaviot/%.kaavio,%,$(wildcard kaaviot/*.kaavio))
TARKISTUKSET := $(SIMULOIDUT:%=$(RAK)/%.ok)

.PHONY: kaikki paivita siivoa
kaikki: $(TARKISTUKSET)

# Kaavio simuloidaan GHDL:llä omassa hakemistossaan.
$(RAK)/%.json: kaaviot/%.kaavio $(wildcard *.vhd */*.vhd) $(KAAVIOT)
	@rm -rf $(RAK)/$* && mkdir -p $(RAK)/$*
	@cp $< $(RAK)/$*/kaavio.vhd
	@lahteet=$$(sed -n 's#^-- lahde: ##p' $<); \
	{ ghdl -i --std=08 --workdir=$(RAK)/$* $$lahteet $(RAK)/$*/kaavio.vhd \
	  && ghdl -m --std=08 --workdir=$(RAK)/$* kaavio; } \
	    > $(RAK)/$*/ghdl.log 2>&1 \
	    || { cat $(RAK)/$*/ghdl.log; exit 1; }
	@timeout 120 ghdl -r --std=08 --workdir=$(RAK)/$* kaavio \
	    --vcd=$(RAK)/$*/kaavio.vcd > $(RAK)/$*/sim.log 2>&1 \
	    || { cat $(RAK)/$*/sim.log; exit 1; }
	@python3 $(KAAVIOT) vcd $(RAK)/$*/kaavio.vcd \
	    $$(sed -n 's#^-- vcd: ##p' $<) > $@

$(RAK)/%.ok: $(RAK)/%.json kaaviot/%.json
	@diff -u kaaviot/$*.json $< \
	    || { echo "kaavio $* ei vastaa simulaatiota: make paivita"; exit 1; }
	@touch $@

paivita: $(SIMULOIDUT:%=$(RAK)/%.json)
	@for k in $(SIMULOIDUT); do \
	    cp $(RAK)/$$k.json kaaviot/$$k.json; done

siivoa:
	rm -rf $(RAK)
