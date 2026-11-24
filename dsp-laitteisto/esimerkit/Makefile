# DSP-algoritmien laitteistototeutuksen esimerkit.
#
#   make           ajaa kaikki esimerkit ja vertaa tulosteet hakemistojen
#                  odotetut/ ja raportit/ tiedostoihin
#   make cocotb-fir-suora   yksi kohde
#   make siivoa    poistaa käännöstuotteet
#   PAIVITA=1 make kirjoittaa odotetut tulosteet uudelleen
#
# Kohteet, joiden nimessä on vian nimi (katkaisu, kierto), kääntävät
# RTL:n makrolla BUGI_<VIKA>; niiden testin on löydettävä vika.

export PYTHONPATH := $(CURDIR)
RAKENNUS := rakennus
VERTAA   := python3 tyokalut/vertaa.py
COCOTB   := python3 penkit/aja.py
KAV      := rtl/kavenna.sv

# --- Malli, generoidut tiedostot ja koodin laatu --------------------
ANALYYSIT := suunnittelu bittikasvu sanaleveys cordic_tarkkuus \
             nco_piikit cic
MUUT := generoidut laatu lint pytest

# --- cocotb (Icarus Verilog) ------------------------------------------
FIRIT := fir-suora fir-transponoitu fir-symmetrinen fir-jaettu
COCOTB_KOHTEET := $(addprefix cocotb-,$(FIRIT)) cocotb-polyfaasi \
                  cocotb-sos cocotb-cic cocotb-cordic-iter \
                  cocotb-cordic-lh cocotb-nco
VIAT := cocotb-fir-suora-katkaisu cocotb-sos-kierto

# --- Verilator ------------------------------------------------------
VERILATOR_KOHTEET := verilator-fir verilator-fir-katkaisu

# --- Synteesi (Yosys, nextpnr, iCE40 UP5K) ---------------------------
SYNTEESIT := $(addprefix synteesi-,$(FIRIT) fir-suora-lut \
               fir-transponoitu-lut fir-symmetrinen-lut fir-jaettu-lut \
               polyfaasi biquad biquad-lut cic cordic-iter cordic-lh nco)

# --- Kirjan ajoituskaaviot simulaatiosta ------------------------------
KAAVIOT := $(patsubst kaaviot/%.kaavio,kaavio-%,$(wildcard kaaviot/*.kaavio))

KOHTEET := $(MUUT) $(ANALYYSIT) $(COCOTB_KOHTEET) $(VIAT) \
           $(VERILATOR_KOHTEET) $(SYNTEESIT) $(KAAVIOT)

.PHONY: kaikki siivoa $(KOHTEET)
kaikki: $(KOHTEET)

generoidut:
	@python3 -m malli.generoi --tarkista

PYTHON := malli analyysit penkit testit tyokalut verilator
laatu:
	@ruff check -q --no-cache $(PYTHON)
	@ruff format -q --no-cache --check $(PYTHON)
	@mypy --no-error-summary --cache-dir=/dev/null $(PYTHON)
	@shellcheck tyokalut/vuo.sh
	@echo "OK: laatu"

pytest:
	@python3 -m pytest -q -p no:cacheprovider testit > /dev/null \
	    || python3 -m pytest -q -p no:cacheprovider testit
	@echo "OK: mallin testit"

# @alku lint
# Jokainen ylimmän tason moduuli Verilatorin tiukimmilla varoituksilla.
LINT := verilator --lint-only -Wall -Irtl
lint:
	@for m in fir_suora fir_transponoitu fir_symmetrinen fir_jaettu \
	          polyfaasi biquad cic; do \
	    $(LINT) --top-module $$m rtl/$$m.sv $(KAV) || exit 1; done
	@$(LINT) --top-module sos rtl/sos.sv rtl/biquad.sv $(KAV)
	@for m in cordic_iter cordic_lh nco; do \
	    $(LINT) --top-module $$m rtl/$$m.sv || exit 1; done
	@echo "OK: lint"
# @loppu lint

$(ANALYYSIT):
	@$(VERTAA) odotetut/$@.odotettu -- python3 analyysit/$@.py

# @alku cocotb
# Neljä FIR-rakennetta, sama testisarja ja sama malli.
$(addprefix cocotb-,$(FIRIT)): cocotb-fir-%:
	@$(VERTAA) odotetut/$@.odotettu -- $(COCOTB) --moduuli test_suodin \
	    --top fir_$(subst -,_,$*) --lahde rtl/fir_$(subst -,_,$*).sv \
	    --lahde $(KAV) --asetus SUODIN=fir

cocotb-fir-suora-katkaisu:
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(COCOTB) \
	    --moduuli test_suodin --top fir_suora --lahde rtl/fir_suora.sv \
	    --lahde $(KAV) --asetus SUODIN=fir --vika BUGI_KATKAISU
# @loppu cocotb

cocotb-polyfaasi:
	@$(VERTAA) odotetut/$@.odotettu -- $(COCOTB) --moduuli test_suodin \
	    --top polyfaasi --lahde rtl/polyfaasi.sv --lahde $(KAV) \
	    --asetus SUODIN=polyfaasi

SOS := --lahde rtl/sos.sv --lahde rtl/biquad.sv --lahde $(KAV)
cocotb-sos:
	@$(VERTAA) odotetut/$@.odotettu -- $(COCOTB) --moduuli test_suodin \
	    --top sos $(SOS) --asetus SUODIN=sos

cocotb-sos-kierto:
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(COCOTB) \
	    --moduuli test_suodin --top sos $(SOS) --asetus SUODIN=sos \
	    --vika BUGI_KIERTO

cocotb-cic:
	@$(VERTAA) odotetut/$@.odotettu -- $(COCOTB) --moduuli test_suodin \
	    --top cic --lahde rtl/cic.sv --asetus SUODIN=cic

cocotb-cordic-iter cocotb-cordic-lh: cocotb-cordic-%:
	@$(VERTAA) odotetut/$@.odotettu -- $(COCOTB) --moduuli test_cordic \
	    --top cordic_$* --lahde rtl/cordic_$*.sv

cocotb-nco:
	@$(VERTAA) odotetut/$@.odotettu -- $(COCOTB) --moduuli test_nco \
	    --top nco --lahde rtl/nco.sv

# @alku verilator
# Verilator kääntää RTL:n C++:ksi; oma pääohjelma ajaa 100 000 näytettä.
VL := $(RAKENNUS)/verilator
define verilator_fir
	@mkdir -p $(VL)/$(1)
	@verilator --cc --exe --build -j 2 -O3 -Wall -Irtl $(2) \
	    --top-module fir_suora rtl/fir_suora.sv $(KAV) \
	    $(CURDIR)/verilator/paa.cpp -Mdir $(VL)/$(1) -o sim \
	    > $(VL)/$(1).loki 2>&1 || (cat $(VL)/$(1).loki; false)
	@python3 verilator/vektorit.py $(VL)/$(1) 100000
endef

verilator-fir:
	$(call verilator_fir,$@,)
	@$(VERTAA) odotetut/$@.odotettu -- $(VL)/$@/sim \
	    $(VL)/$@/syote.txt $(VL)/$@/odotettu.txt

verilator-fir-katkaisu:
	$(call verilator_fir,$@,-DBUGI_KATKAISU)
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(VL)/$@/sim \
	    $(VL)/$@/syote.txt $(VL)/$@/odotettu.txt
# @loppu verilator

# @alku synteesi
# synteesi NIMI YLIN LÄHTEET YOSYS-VALINNAT RAPORTIN-RAJAT [PARAMETRIT]
# Vuon loki menee rakennushakemistoon; tiivistelmä verrataan tiedostoon
# raportit/NIMI.odotettu.
define synteesi
	@mkdir -p $(RAKENNUS)
	@bash tyokalut/vuo.sh $(1) $(2) "$(3)" "$(4)" "--freq 12" $(6) \
	    > $(RAKENNUS)/$(1).vuo.loki 2>&1 \
	    || (cat $(RAKENNUS)/$(1).vuo.loki; false)
	@python3 tyokalut/raportti.py $(1) $(RAKENNUS)/$(1).stat.json \
	    $(RAKENNUS)/$(1).pnr.json $(5) > $(RAKENNUS)/$(1).tulos
	@diff -u raportit/$(1).odotettu $(RAKENNUS)/$(1).tulos \
	    && echo "OK: $(1)"
endef

# DSP-lohkoilla: resurssit. nextpnr ei mallinna SB_MAC16-lohkon
# viiveitä, joten Fmax luetaan LUT-toteutuksesta (-lut).
synteesi-fir-suora:
	$(call synteesi,fir-suora,fir_suora,rtl/fir_suora.sv $(KAV),-dsp,\
	    --solut-alle 600)
synteesi-fir-suora-lut:
	$(call synteesi,fir-suora-lut,fir_suora,rtl/fir_suora.sv $(KAV),,\
	    --solut-yli 1200 --fmax-yli 18 --fmax-alle 30)
# @loppu synteesi
synteesi-fir-transponoitu:
	$(call synteesi,fir-transponoitu,fir_transponoitu,\
	    rtl/fir_transponoitu.sv $(KAV),-dsp,--solut-alle 400)
synteesi-fir-transponoitu-lut:
	$(call synteesi,fir-transponoitu-lut,fir_transponoitu,\
	    rtl/fir_transponoitu.sv $(KAV),,--solut-alle 1000 --fmax-yli 30)
synteesi-fir-symmetrinen:
	$(call synteesi,fir-symmetrinen,fir_symmetrinen,\
	    rtl/fir_symmetrinen.sv $(KAV),-dsp,--solut-alle 450)
synteesi-fir-symmetrinen-lut:
	$(call synteesi,fir-symmetrinen-lut,fir_symmetrinen,\
	    rtl/fir_symmetrinen.sv $(KAV),,--solut-alle 1200 --fmax-yli 22)
synteesi-fir-jaettu:
	$(call synteesi,fir-jaettu,fir_jaettu,rtl/fir_jaettu.sv $(KAV),-dsp,\
	    --solut-alle 350)
synteesi-fir-jaettu-lut:
	$(call synteesi,fir-jaettu-lut,fir_jaettu,rtl/fir_jaettu.sv $(KAV),,\
	    --solut-alle 1000 --fmax-yli 12 --fmax-alle 22)
synteesi-polyfaasi:
	$(call synteesi,polyfaasi,polyfaasi,rtl/polyfaasi.sv $(KAV),-dsp,\
	    --solut-alle 600)
synteesi-biquad:
	$(call synteesi,biquad,biquad,rtl/biquad.sv $(KAV),-dsp,\
	    --solut-alle 450)
synteesi-biquad-lut:
	$(call synteesi,biquad-lut,biquad,rtl/biquad.sv $(KAV),,\
	    --fmax-yli 10 --fmax-alle 18)
synteesi-cic:
	$(call synteesi,cic,cic,rtl/cic.sv,,--solut-alle 350 --fmax-yli 35)

KAARE := synteesi/kaare.sv rtl/cordic_iter.sv rtl/cordic_lh.sv rtl/nco.sv
synteesi-cordic-iter:
	$(call synteesi,cordic-iter,kaare,$(KAARE),,\
	    --solut-alle 800 --fmax-yli 25,TOTEUTUS=0)
synteesi-cordic-lh:
	$(call synteesi,cordic-lh,kaare,$(KAARE),,\
	    --solut-yli 2500 --fmax-yli 40,TOTEUTUS=1)
synteesi-nco:
	$(call synteesi,nco,kaare,$(KAARE),,--solut-alle 200 --fmax-yli 55,\
	    TOTEUTUS=2)

# Kirjan ajoituskaaviot (kaaviot/*.json) simuloidaan Verilatorilla
# tiedoston kaaviot/<nimi>.kaavio kääreestä ja verrataan tallennettuun.
# Otsakerivit kertovat lähteet ja yhteiset/kaaviot.py:n valitsimet.
# PAIVITA=1 kirjoittaa kaavion uudelleen.
KAAVIOTYOKALU := $(abspath ../../yhteiset/kaaviot.py)
$(KAAVIOT): kaavio-%:
	@mkdir -p $(RAKENNUS)/kaavio-$*
	@cp kaaviot/$*.kaavio $(RAKENNUS)/kaavio-$*/kaavio.sv
	@verilator --binary --trace --top-module kaavio -Wno-fatal -Irtl \
	    -Mdir $(RAKENNUS)/kaavio-$*/obj -o sim \
	    $$(sed -n 's#^// lahde: ##p' kaaviot/$*.kaavio) \
	    $(RAKENNUS)/kaavio-$*/kaavio.sv > $(RAKENNUS)/kaavio-$*/loki 2>&1 \
	    || { cat $(RAKENNUS)/kaavio-$*/loki; exit 1; }
	@cd $(RAKENNUS)/kaavio-$* && timeout 60 ./obj/sim > /dev/null \
	    || { echo "kaavion $* simulointi epäonnistui"; exit 1; }
	@python3 $(KAAVIOTYOKALU) vcd $(RAKENNUS)/kaavio-$*/kaavio.vcd \
	    $$(sed -n 's#^// vcd: ##p' kaaviot/$*.kaavio) \
	    > $(RAKENNUS)/kaavio-$*/kaavio.json
	@if [ "$(PAIVITA)" = 1 ]; then \
	    cp $(RAKENNUS)/kaavio-$*/kaavio.json kaaviot/$*.json; fi
	@diff -u kaaviot/$*.json $(RAKENNUS)/kaavio-$*/kaavio.json \
	    || { echo "kaavio $* ei vastaa simulaatiota (PAIVITA=1)"; exit 1; }
	@echo "OK: kaavio $*"

siivoa:
	rm -rf $(RAKENNUS)
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
