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

.PHONY: kaikki paivita siivoa cocotb
kaikki: $(TARKISTUKSET) cocotb

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
	rm -rf $(RAK) cocotb-testit/__pycache__

# --- Luku 13: cocotb-testit ----------------------------------------
#
# Jokainen ajo kääntää moduulin Icarus Verilogilla ja ajaa Python-testit
# (cocotb-testit/aja.py). Tuloste verrataan tiedostoon
# cocotb-testit/odotettu/<ajo>.odotettu. Mutaatioajoissa lähteeseen
# istutetaan vika, ja testien on huomattava se (paluuarvo 1).

COCOTB  := python3 cocotb-testit/aja.py
FIFO    := --top fifo --moduuli test_fifo --lahde 08-fifo/fifo.sv
UART    := --top uart_tx --moduuli test_uart_tx \
           --lahde 06-uart-tx/uart_tx.sv \
           --parametri KELLO_HZ=1000000 --parametri BAUD=100000

# cocotb_ajo NIMI ODOTETTU_PALUUARVO VALITSIMET
define cocotb_ajo
$(RAK)/cocotb-$(1).ok: cocotb-testit/odotettu/$(1).odotettu \
    $(wildcard cocotb-testit/*.py *.sv */*.sv)
	@mkdir -p $(RAK)
	@$(COCOTB) $(3) > $(RAK)/cocotb-$(1).tuloste; tila=$$$$?; \
	diff -u cocotb-testit/odotettu/$(1).odotettu \
	    $(RAK)/cocotb-$(1).tuloste || exit 1; \
	[ $$$$tila -eq $(2) ] || \
	    { echo "cocotb $(1): paluuarvo $$$$tila"; exit 1; }
	@touch $$@
COCOTB_AJOT += $(RAK)/cocotb-$(1).ok
endef

$(eval $(call cocotb_ajo,laskuri,0,--top laskuri --moduuli test_laskuri \
    --lahde 01-laskuri.sv))
$(eval $(call cocotb_ajo,laskuri-6,0,--top laskuri --moduuli test_laskuri \
    --lahde 01-laskuri.sv --parametri LEVEYS=6))
$(eval $(call cocotb_ajo,fifo-4,0,$(FIFO) --parametri SYVYYS=4))
$(eval $(call cocotb_ajo,fifo-16,0,$(FIFO) --parametri SYVYYS=16))
$(eval $(call cocotb_ajo,fifo-vika,1,$(FIFO) --parametri SYVYYS=4 \
    --mutaatio 'if (kirjoita && !taynna) k_os=>if (kirjoita) k_os'))
$(eval $(call cocotb_ajo,uart,0,$(UART)))
$(eval $(call cocotb_ajo,uart-vika,1,$(UART) \
    --mutaatio "if (bitti_q == 3'd7)=>if (bitti_q == 3'd6)"))

cocotb: $(COCOTB_AJOT)
	@cd cocotb-testit && ruff check -q --no-cache . \
	    && mypy --no-error-summary --cache-dir=/dev/null .
