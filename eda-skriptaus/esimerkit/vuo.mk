# Sama vuo Makella. Kohteet ovat tiedostoja, ja Make päättelee
# vanhentuneisuuden muutosajoista. Käyttö (ks. 02-make.py):
#   make -f vuo.mk JUURI=. AJO=ajo LEVEYS=8

JUURI  ?= .
AJO    ?= ajo
LEVEYS ?= 8
TCLSH  ?= tclsh8.6
RTL    := $(JUURI)/rtl/laskuri.sv
TCL    := $(JUURI)/tcl

.PHONY: kaikki
kaikki: $(AJO)/sta.txt

# @alku saannot
$(AJO)/lint.ok: $(RTL)
	@mkdir -p $(AJO)
	@echo "  lint"
	@verilator --lint-only -Wall -GLEVEYS=$(LEVEYS) $< >$(AJO)/lint.log 2>&1
	@touch $@

$(AJO)/laskuri.blif: $(AJO)/lint.ok $(RTL) $(TCL)/synteesi.tcl
	@echo "  synteesi"
	@LEVEYDET=$(LEVEYS) RTL=$(RTL) TULOS=$(AJO)/syn \
	    yosys -q -c $(TCL)/synteesi.tcl >$(AJO)/synteesi.log 2>&1
	@cp $(AJO)/syn/laskuri_$(LEVEYS).blif $@

$(AJO)/sta.txt: $(AJO)/laskuri.blif $(TCL)/opetus_sta.tcl $(TCL)/sta_kulku.tcl
	@echo "  sta"
	@$(TCLSH) $(TCL)/opetus_sta.tcl -source $(TCL)/sta_kulku.tcl \
	    -- $< 10 $@ >$(AJO)/sta.log
# @loppu saannot
