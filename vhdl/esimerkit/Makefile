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

.PHONY: kaikki paivita siivoa cocotb
kaikki: $(TARKISTUKSET) $(RAK)/synteesi.ok cocotb

# --- Luku 7: muistien päättely --------------------------------------
#
# ghdl --synth ilmoittaa jokaisesta tunnistamastaan muistista. Rivit
# verrataan tiedostoon 07-muisti/synteesi.odotettu: jos kuvio rikkoutuu,
# ilmoitus katoaa ja tarkistus epäonnistuu.
MUISTIT := ram nelio_rom fifo

$(RAK)/synteesi.ok: 07-muisti/synteesi.odotettu $(wildcard 07-muisti/*.vhd)
	@rm -rf $(RAK)/synteesi && mkdir -p $(RAK)/synteesi
	@ghdl -a --std=08 --workdir=$(RAK)/synteesi 07-muisti/ram.vhd \
	    07-muisti/rom.vhd 07-muisti/fifo.vhd
	@for e in $(MUISTIT); do \
	    ghdl --synth --std=08 --workdir=$(RAK)/synteesi $$e 2>&1 \
	        > /dev/null \
	    | sed -n "s/^.*note: found \([A-Z]*\) \"[^\"]*\"/$$e: \1/p"; \
	done > $(RAK)/synteesi.tuloste
	@diff -u 07-muisti/synteesi.odotettu $(RAK)/synteesi.tuloste
	@touch $@

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
	rm -rf $(RAK) cocotb-testit/__pycache__

# --- Luku 10: cocotb-testit ----------------------------------------
#
# Jokainen ajo kääntää entiteetin GHDL:llä ja ajaa Python-testit
# (cocotb-testit/aja.py). Tuloste verrataan tiedostoon
# cocotb-testit/odotettu/<ajo>.odotettu. Mutaatioajoissa lähteeseen
# istutetaan vika, ja testien on huomattava se (paluuarvo 1).

COCOTB := python3 cocotb-testit/aja.py
KVAD   := --top kvadratuuri --moduuli test_kvadratuuri \
          --lahde 05-kvadratuuri.vhd
UART   := --top sarjavastaanotin --moduuli test_uart_rx \
          --lahde 06-uart-rx/sarjavastaanotin.vhd \
          --parametri KELLOJA_BITTIIN=16

# cocotb_ajo NIMI ODOTETTU_PALUUARVO VALITSIMET
define cocotb_ajo
$(RAK)/cocotb-$(1).ok: cocotb-testit/odotettu/$(1).odotettu \
    $(wildcard cocotb-testit/*.py *.vhd */*.vhd)
	@mkdir -p $(RAK)
	@$(COCOTB) $(3) > $(RAK)/cocotb-$(1).tuloste; tila=$$$$?; \
	diff -u cocotb-testit/odotettu/$(1).odotettu \
	    $(RAK)/cocotb-$(1).tuloste || exit 1; \
	[ $$$$tila -eq $(2) ] || \
	    { echo "cocotb $(1): paluuarvo $$$$tila"; exit 1; }
	@touch $$@
COCOTB_AJOT += $(RAK)/cocotb-$(1).ok
endef

$(eval $(call cocotb_ajo,kvadratuuri,0,$(KVAD)))
$(eval $(call cocotb_ajo,kvadratuuri-vika,1,$(KVAD) \
    --mutaatio '"1101" | "0100"=>"1101"'))
$(eval $(call cocotb_ajo,uart-rx,0,$(UART)))
$(eval $(call cocotb_ajo,uart-rx-vika,1,$(UART) \
    --mutaatio 'rx & siirto(7 downto 1)=>siirto(6 downto 0) & rx'))

cocotb: $(COCOTB_AJOT)
	@cd cocotb-testit && ruff check -q --no-cache . \
	    && mypy --no-error-summary --cache-dir=/dev/null .
