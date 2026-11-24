# Laitteiston verifioinnin esimerkit.
#
#   make           ajaa kaikki esimerkit ja vertaa tulosteet
#                  hakemiston odotetut/ tiedostoihin
#   make siivoa    poistaa käännöstuotteet
#   PAIVITA=1 make kirjoittaa odotetut tulosteet uudelleen
#
# Kohteiden nimissä vian nimi (tyhja, samanaikainen, taysi, kiintea,
# kaksi) tarkoittaa, että DUT käännetään makrolla BUGI_<VIKA>. Silloin
# odotetaan yleensä, että testi löytää vian ja epäonnistuu (--virhe).

RAKENNUS  := rakennus
VERTAA    := python3 tyokalut/vertaa.py
VERILATOR := verilator --assert -Wall -Wno-DECLFILENAME \
             --top-module testipenkki
FIFO      := rtl/fifo.sv
COCOTB    := python3 pythonpenkit/aja.py
FORMAALI  := python3 tyokalut/formaali.py
FIFOVIAT  := tyhja samanaikainen taysi

# Makron nimi kohteen nimen viimeisestä osasta: penkki-taysi -> BUGI_TAYSI
bugi = -DBUGI_$(shell echo $(lastword $(subst -, ,$(1))) | tr a-z A-Z)

SV_KOHTEET := ohjattu ohjattu-taysi ohjattu-samanaikainen \
              penkki $(addprefix penkki-,$(FIFOVIAT)) siemenet \
              sva $(addprefix sva-,$(FIFOVIAT)) sva-ei-tuettu \
              kattavuus
COCOTB_KOHTEET := cocotb-fifo $(addprefix cocotb-fifo-,$(FIFOVIAT)) \
                  cocotb-arbiteri cocotb-arbiteri-kiintea \
                  cocotb-arbiteri-kaksi
FORMAALIT := formaali-bmc $(addprefix formaali-,$(FIFOVIAT)) \
             formaali-induktio formaali-invariantti formaali-cover \
             formaali-arbiteri formaali-arbiteri-kiintea \
             formaali-arbiteri-kaksi
MUUT := suunnitelma regressio laatu kaavio-ohjattu

KOHTEET := $(SV_KOHTEET) $(COCOTB_KOHTEET) $(FORMAALIT) $(MUUT)

.PHONY: kaikki siivoa formaali-kaavio $(KOHTEET)
kaikki: $(KOHTEET)

# sv NIMI VALITSIMET LÄHTEET: kääntää Verilatorilla hakemistoon
# rakennus/NIMI. Kääntäjän tuloste näytetään vain virheen sattuessa.
define sv
	@mkdir -p $(RAKENNUS)/$(1)
	@$(VERILATOR) $(2) -Mdir $(RAKENNUS)/$(1) -o sim $(3) \
	    > $(RAKENNUS)/$(1).loki 2>&1 || (cat $(RAKENNUS)/$(1).loki; false)
endef

# --- Luvut 1-4: ohjattu testi ja kerroksellinen testipenkki ----------
ohjattu:
	$(call sv,$@,--binary,$(FIFO) 01-ohjattu/testipenkki.sv)
	@$(VERTAA) odotetut/$@.odotettu -- $(RAKENNUS)/$@/sim

ohjattu-taysi:
	$(call sv,$@,--binary $(call bugi,$@),$(FIFO) 01-ohjattu/testipenkki.sv)
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(RAKENNUS)/$@/sim

# Ohjattu testi ei kirjoita ja lue yhtä aikaa: vika jää huomaamatta.
ohjattu-samanaikainen:
	$(call sv,$@,--binary $(call bugi,$@),$(FIFO) 01-ohjattu/testipenkki.sv)
	@$(VERTAA) odotetut/$@.odotettu -- $(RAKENNUS)/$@/sim

penkki:
	$(call sv,$@,--binary,$(FIFO) 03-penkki/testipenkki.sv)
	@$(VERTAA) odotetut/$@.odotettu -- $(RAKENNUS)/$@/sim +siemen=1

$(addprefix penkki-,$(FIFOVIAT)):
	$(call sv,$@,--binary $(call bugi,$@),$(FIFO) 03-penkki/testipenkki.sv)
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(RAKENNUS)/$@/sim +siemen=1

# Sama siemen tuottaa saman ajon: siemen 2 ajetaan kahdesti.
siemenet:
	$(call sv,$@,--binary,$(FIFO) 03-penkki/testipenkki.sv)
	@$(VERTAA) odotetut/siemen-2.odotettu -- $(RAKENNUS)/$@/sim +siemen=2
	@$(VERTAA) odotetut/siemen-2.odotettu -- $(RAKENNUS)/$@/sim +siemen=2
	@$(VERTAA) odotetut/siemen-3.odotettu -- $(RAKENNUS)/$@/sim +siemen=3

# Kirjan ajoituskaavio tuotetaan simulaation aaltomuodosta ja verrataan
# versionhallinnassa olevaan tiedostoon kaaviot/NIMI.json; PAIVITA=1
# kirjoittaa sen uudelleen. kaavio NIMI VCD (VCD poistetaan lopuksi)
# JSON muotoillaan riveittäin, jotta rivit pysyvät lyhyinä.
KAAVIOT := python3 ../../yhteiset/kaaviot.py vcd
MUOTOILE := python3 -m json.tool --indent 1 --no-ensure-ascii
define kaavio
	@$(MUOTOILE) $(RAKENNUS)/$(1).json > $(RAKENNUS)/$(1).muotoiltu
	@mv $(RAKENNUS)/$(1).muotoiltu $(RAKENNUS)/$(1).json
	@if [ "$(PAIVITA)" = 1 ]; then cp $(RAKENNUS)/$(1).json kaaviot/$(1).json; fi
	@diff -u kaaviot/$(1).json $(RAKENNUS)/$(1).json && echo "OK: kaavio $(1)"
	@rm -f $(2)
endef

kaavio-ohjattu:
	$(call sv,$@,--binary --trace -DJALJITYS,$(FIFO) 01-ohjattu/testipenkki.sv)
	@$(RAKENNUS)/$@/sim > /dev/null
	@$(KAAVIOT) $(RAKENNUS)/$@.vcd --kello clk --jaksot 9 \
	    --signaalit rst,push,din,pop,dout,maara,tyhja,taysi \
	    > $(RAKENNUS)/ohjattu.json
	$(call kaavio,ohjattu,$(RAKENNUS)/$@.vcd)

# --- Luku 5: koodikattavuus -----------------------------------------
# Verilatorin --binary ei kirjoita kattavuutta, joten käytetään omaa
# pääohjelmaa. Make-ohjelma tarvitsee sen absoluuttisen polun.
KAT := --cc --exe --build --timing --coverage
PAA := $(CURDIR)/05-kattavuus/paa.cpp
kattavuus:
	$(call sv,$@-ohjattu,$(KAT),$(FIFO) 01-ohjattu/testipenkki.sv $(PAA))
	$(call sv,$@-penkki,$(KAT),$(FIFO) 03-penkki/testipenkki.sv $(PAA))
	@$(RAKENNUS)/$@-ohjattu/sim \
	    +kattavuus=$(RAKENNUS)/$@-ohjattu/kattavuus.dat > /dev/null
	@$(RAKENNUS)/$@-penkki/sim +siemen=1 \
	    +kattavuus=$(RAKENNUS)/$@-penkki/kattavuus.dat > /dev/null
	@$(VERTAA) odotetut/kattavuus-ohjattu.odotettu -- \
	    python3 tyokalut/koodikattavuus.py --tiedosto $(FIFO) \
	    $(RAKENNUS)/$@-ohjattu/kattavuus.dat
	@$(VERTAA) odotetut/kattavuus-yhdistetty.odotettu -- \
	    python3 tyokalut/koodikattavuus.py --tiedosto $(FIFO) \
	    $(RAKENNUS)/$@-ohjattu/kattavuus.dat \
	    $(RAKENNUS)/$@-penkki/kattavuus.dat

# --- Luku 6: SVA ----------------------------------------------------
SVA := $(FIFO) 06-sva/fifo_sva.sv 06-sva/testipenkki.sv
sva:
	$(call sv,$@,--binary,$(SVA))
	@$(VERTAA) odotetut/$@.odotettu -- $(RAKENNUS)/$@/sim +siemen=1

$(addprefix sva-,$(FIFOVIAT)):
	$(call sv,$@,--binary $(call bugi,$@),$(SVA))
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(RAKENNUS)/$@/sim +siemen=1

sva-ei-tuettu:
	@$(VERTAA) odotetut/$@.odotettu --virhe -- \
	    verilator --lint-only -Wall 06-sva/ei_tuettu.sv

# --- Luvut 7 ja 9: cocotb -------------------------------------------
cocotb-fifo:
	@$(VERTAA) odotetut/$@.odotettu -- \
	    $(COCOTB) --top fifo --moduuli test_fifo --lahde $(FIFO)

$(addprefix cocotb-fifo-,$(FIFOVIAT)): cocotb-fifo-%:
	@$(VERTAA) odotetut/$@.odotettu --virhe -- \
	    $(COCOTB) --top fifo --moduuli test_fifo --lahde $(FIFO) \
	    --vika BUGI_$(shell echo $* | tr a-z A-Z)

cocotb-arbiteri:
	@$(VERTAA) odotetut/$@.odotettu -- $(COCOTB) --top arbiteri \
	    --moduuli test_arbiteri --lahde rtl/arbiteri.sv

cocotb-arbiteri-kiintea cocotb-arbiteri-kaksi: cocotb-arbiteri-%:
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(COCOTB) --top arbiteri \
	    --moduuli test_arbiteri --lahde rtl/arbiteri.sv \
	    --vika BUGI_$(shell echo $* | tr a-z A-Z)

# --- Luku 8: formaali verifiointi -----------------------------------
FIFO_F := $(FORMAALI) --top fifo --lahde $(FIFO)
JALKI  := --signaalit rst,push,pop,maara,tyhja,taysi
ARB_F  := $(FORMAALI) --top arbiteri --lahde rtl/arbiteri.sv
formaali-bmc:
	@$(VERTAA) odotetut/$@.odotettu -- $(FIFO_F) --syvyys 10

$(addprefix formaali-,$(FIFOVIAT)): formaali-%:
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(FIFO_F) --syvyys 10 \
	    -D BUGI_$(shell echo $* | tr a-z A-Z) $(JALKI)

# Vastaesimerkin jälki ajoituskaaviona (luku 8).
formaali-samanaikainen: formaali-kaavio
JALKI_VCD := $(RAKENNUS)/formaali/fifo-bmc-bugi_samanaikainen/jalki.vcd
formaali-kaavio:
	@$(FIFO_F) --syvyys 10 -D BUGI_SAMANAIKAINEN > /dev/null || true
	@$(KAAVIOT) $(JALKI_VCD) --jaksot 4 \
	    --kello clk --signaalit rst,push,pop,maara,tyhja,taysi \
	    > $(RAKENNUS)/vastaesimerkki.json
	$(call kaavio,vastaesimerkki,$(JALKI_VCD))

formaali-induktio:
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(FIFO_F) --tila prove \
	    --syvyys 8 --signaalit push,pop,kirj,luku,maara,tyhja

formaali-invariantti:
	@$(VERTAA) odotetut/$@.odotettu -- $(FIFO_F) --tila prove \
	    --syvyys 8 -D INVARIANTTI

formaali-cover:
	@$(VERTAA) odotetut/$@.odotettu -- $(FIFO_F) --tila cover \
	    --syvyys 10 $(JALKI)

formaali-arbiteri:
	@$(VERTAA) odotetut/$@-bmc.odotettu -- $(ARB_F) --syvyys 12
	@$(VERTAA) odotetut/$@-prove.odotettu -- $(ARB_F) --tila prove \
	    --syvyys 6
	@$(VERTAA) odotetut/$@-cover.odotettu -- $(ARB_F) --tila cover \
	    --syvyys 10

formaali-arbiteri-kiintea formaali-arbiteri-kaksi: formaali-arbiteri-%:
	@$(VERTAA) odotetut/$@.odotettu --virhe -- $(ARB_F) --syvyys 12 \
	    -D BUGI_$(shell echo $* | tr a-z A-Z) \
	    --signaalit rst,pyynto:b,myonto:b,reilu[1].odotus

# --- Luvut 2 ja 10: suunnitelma, regressio ja koodin laatu -----------
suunnitelma:
	@$(VERTAA) odotetut/$@.odotettu -- \
	    python3 tyokalut/suunnitelma.py suunnitelma/fifo.toml

regressio:
	@$(VERTAA) odotetut/$@.odotettu -- python3 tyokalut/regressio.py

PYTHON := tyokalut pythonpenkit
laatu:
	@ruff check -q --no-cache $(PYTHON)
	@ruff format -q --no-cache --check $(PYTHON)
	@mypy --no-error-summary --cache-dir=/dev/null tyokalut
	@cd pythonpenkit && mypy --no-error-summary --cache-dir=/dev/null .
	@echo "OK: laatu"

siivoa:
	rm -rf $(RAKENNUS) pythonpenkit/__pycache__ tyokalut/__pycache__
