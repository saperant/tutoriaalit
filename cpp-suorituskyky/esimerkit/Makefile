# C++:n suorituskyvyn esimerkit: mittaukset ja deterministiset tarkistukset.
#
# Testaaja (make -C .. testaa) kääntää esimerkit sanitoijien kanssa ja
# vertaa toiminnallisten testien tulosteet odotettuihin. Tämä Makefile
# kääntää samat ohjelmat optimoinneilla ja
#
#   make tarkista   laskee Cachegrindilla käskyt ja välimuistihudit
#                   operaatiota kohden ja tutkii konekoodia; tulokset ovat
#                   deterministisiä, ja tekstin väitteet tarkistetaan
#   make mittaa     ajaa ajoitusmittaukset; luvut ovat suuntaa-antavia,
#                   eikä niitä verrata mihinkään
#   make            molemmat
#   make tulokset   kirjoittaa kirjassa näytetyt tulosteet hakemistoon
#                   tulokset/ (kirjoittajan koneen luvut)
#   make siivoa     poistaa käännöstuotteet

.NOTPARALLEL:
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

CXX   := $(firstword $(shell command -v g++-14 g++ 2>/dev/null))
LIPUT := -std=c++23 -O2 -g -Wall -Wextra -Werror
OTSAKKEET := mittari.hpp laskuri.hpp satunnainen.hpp seuranta.hpp
LTO := $(wildcard 09-lto/*.cpp 09-lto/*.hpp) $(OTSAKKEET)

# @alku kaskyt
# Käskyt (Ir) tai välimuistihudit (D1mr) operaatiota kohden: ohjelma
# ajetaan Cachegrindissa toistoilla 0 ja K, ja erotus jaetaan (ks.
# tyokalut/kaskyt.py). Tulos ei riipu koneen kuormasta.
KASKYT := python3 tyokalut/kaskyt.py
# @loppu kaskyt

# Funktion konekoodi: objdump ja funktion nimen alku.
konekoodi = objdump -d -C --no-show-raw-insn $(1) \
            | awk '/^[0-9a-f]+ <$(2)\(/,/^$$/'

OHJELMAT := 01-kopiot 02-poistettu 03-kuviot 04-funktiot 05-jasennys \
            06-pmr 08-soa 08-sailiot 10-muotoilu 11-sanat

.PHONY: kaikki tarkista mittaa tulokset siivoa

kaikki: tarkista mittaa

bin:
	@mkdir -p bin

bin/%: %.cpp $(OTSAKKEET) | bin
	$(CXX) $(LIPUT) $< -o $@

# ---------------------------------------------------------------------
# Deterministiset tarkistukset

TARKISTUKSET := poistettu kuviot devirtualisointi funktiot poikkeukset \
                osoittimet soa sailiot lto constexpr otsakkeet muotoilu sanat

tarkista: $(addprefix tarkista-,$(TARKISTUKSET))
	@echo "OK: tarkistukset"

.PHONY: $(addprefix tarkista-,$(TARKISTUKSET))

# @alku poistettu
tarkista-poistettu: bin/02-poistettu
	@echo "== Kaskyja kierrosta kohden: keskiarvo 1000 alkiosta =="
	@$(KASKYT) --toistot 100 bin/02-poistettu \
	    hylatty pidetty vakio piilotettu \
	    --suhde pidetty hylatty 100 --suhde piilotettu vakio 2
# @loppu poistettu

tarkista-kuviot: bin/03-kuviot
	@echo "== Kaskyja kuviota kohden, 1000 kuviota =="
	@$(KASKYT) --toistot 20 --per 1000 bin/03-kuviot \
	    virtuaali variant avoin final crtp dynamic_cast \
	    --suhde virtuaali final 1.5 --suhde avoin final 1.2 \
	    --suhde dynamic_cast virtuaali 2

# @alku devirtualisointi
tarkista-devirtualisointi: bin/03-kuviot
	@echo "== summa_avoin: vertailu, suora polku ja epasuora kutsu =="
	@$(call konekoodi,bin/03-kuviot,summa_avoin) > bin/avoin.s
	@grep -E 'Ympyra::pinta_ala|call +\*' bin/avoin.s | cut -f2-
	@echo "== summa_final: kertolaskut silmukassa, ei kutsuja =="
	@$(call konekoodi,bin/03-kuviot,summa_final) > bin/final.s
	@grep -E 'mulsd|addsd' bin/final.s | cut -f2-
	@grep -qE 'call +\*' bin/avoin.s
	@! grep -q call bin/final.s
# @loppu devirtualisointi

# @alku osoittimet
tarkista-osoittimet: bin/06-osoittimet
	@echo "== Kaskyja kutsua kohden =="
	@$(KASKYT) --toistot 1000 bin/06-osoittimet arvona viitteena oliosta \
	    --suhde arvona viitteena 2
# @loppu osoittimet

tarkista-funktiot: bin/04-funktiot
	@echo "== Kaskyja alkiota kohden, 1000 alkiota =="
	@$(KASKYT) --toistot 20 --per 1000 bin/04-funktiot \
	    malli osoitin function --suhde function malli 2

# @alku poikkeukset
tarkista-poikkeukset: bin/05-jasennys
	@echo "== Kaskyja jasennysta kohden, 1000 rivia =="
	@$(KASKYT) --toistot 5 --per 1000 bin/05-jasennys \
	    poikkeus-ok expected-ok poikkeus-virhe expected-virhe \
	    --suhde poikkeus-virhe expected-virhe 20
# @loppu poikkeukset

# @alku soa
tarkista-soa: bin/08-soa
	@echo "== L1-datahutia ja kaskyja hiukkasta kohden, 10000 =="
	@$(KASKYT) --tapahtuma D1mr --toistot 5 --per 10000 bin/08-soa \
	    aos soa --suhde aos soa 3
	@$(KASKYT) --toistot 5 --per 10000 bin/08-soa aos soa
# @loppu soa

tarkista-sailiot: bin/08-sailiot
	@echo "== Hakua kohden, 20000 avainta =="
	@$(KASKYT) --toistot 5 --per 1000 bin/08-sailiot \
	    map litea unordered_map
	@$(KASKYT) --tapahtuma D1mr --toistot 5 --per 1000 bin/08-sailiot \
	    map litea unordered_map --suhde map litea 2
	@$(KASKYT) --tapahtuma DLmr --toistot 5 --per 1000 bin/08-sailiot \
	    map litea unordered_map

# @alku lto
bin/lto-ei: $(LTO) | bin
	$(CXX) $(LIPUT) $(filter %.cpp,$^) -o $@

bin/lto-kylla: $(LTO) | bin
	$(CXX) $(LIPUT) -flto=auto $(filter %.cpp,$^) -o $@

tarkista-lto: bin/lto-ei bin/lto-kylla
	@echo "== Kutsuja hinta_ensin_erillinen-funktioon konekoodissa =="
	@for b in lto-ei lto-kylla; do \
	    printf '  %-10s %s\n' $$b "$$(objdump -d -C bin/$$b \
	        | grep -c 'call.*<hinta_ensin_erillinen')"; \
	done
	@echo "== Kaskyja tuotetta kohden lajittelussa, 1000 tuotetta =="
	@for b in lto-ei lto-kylla; do \
	    echo "  $$b:"; \
	    $(KASKYT) --toistot 5 --per 1000 bin/$$b erillinen inline \
	        || exit 1; \
	done
	@test "$$(objdump -d -C bin/lto-kylla \
	    | grep -c 'call.*<hinta_ensin_erillinen')" = 0
# @loppu lto

# @alku constexpr
tarkista-constexpr: bin/09-constexpr
	@echo "== Symbolit: taulukko on, sen laskeva funktio ei =="
	@nm -C bin/09-constexpr | grep -E 'crc_taulukko|tee_taulukko' \
	    | cut -d' ' -f2-
	@! nm -C bin/09-constexpr | grep -q tee_taulukko
# @loppu constexpr

# @alku otsakkeet
OTSAKELISTA := cstdio vector string algorithm format iostream ranges print

tarkista-otsakkeet:
	@echo "== Esikasitellyn koodin rivit otsaketta kohden =="
	@for o in $(OTSAKELISTA); do \
	    printf '  %-12s %6s rivia\n' "<$$o>" \
	        "$$(echo "#include <$$o>" \
	            | $(CXX) -std=c++23 -E -P -x c++ - | wc -l)"; \
	done
	@test "$$(echo '#include <print>' | $(CXX) -std=c++23 -E -P -x c++ - \
	    | wc -l)" -gt 10000
# @loppu otsakkeet

# @alku muotoilu
tarkista-muotoilu: bin/10-muotoilu
	@echo "== Kaskyja muunnosta kohden, 1000 lukua =="
	@$(KASKYT) --toistot 5 --per 1000 bin/10-muotoilu snprintf to_chars \
	    format_to_n format to_string ostringstream \
	    --suhde snprintf to_chars 3 --suhde ostringstream to_chars 5
# @loppu muotoilu

tarkista-sanat: bin/11-sanat
	@echo "== Kaskyja sanaa kohden, 20000 sanaa =="
	@$(KASKYT) --toistot 3 --per 20000 bin/11-sanat v1 v2 v3 v4 \
	    --suhde v1 v4 2.5 --suhde v2 v3 1.1

# ---------------------------------------------------------------------
# Ajoitusmittaukset (suuntaa-antavia)

mittaa: $(addprefix bin/,$(OHJELMAT)) bin/lto-ei bin/lto-kylla
	@for o in $(OHJELMAT); do \
	    echo "== $$o =="; bin/$$o --mittaa || exit 1; \
	done
	@echo "== 09-lto ==" && bin/lto-ei --mittaa
	@echo "== 09-lto, -flto ==" && bin/lto-kylla --mittaa
	@echo "OK: mittaukset"

# Kirjan tulosteet. Ajoitukset vaihtelevat koneittain ja ajoittain.
tulokset: $(addprefix bin/,$(OHJELMAT)) bin/lto-ei bin/lto-kylla
	@mkdir -p tulokset
	@for o in $(OHJELMAT); do \
	    bin/$$o --mittaa > tulokset/$$o.txt || exit 1; \
	done
	@bin/lto-ei --mittaa > tulokset/09-lto.txt
	@bin/lto-kylla --mittaa > tulokset/09-lto-kylla.txt
	@for t in $(TARKISTUKSET); do \
	    $(MAKE) -s tarkista-$$t > tulokset/tarkista-$$t.txt || exit 1; \
	done

siivoa:
	rm -rf bin
