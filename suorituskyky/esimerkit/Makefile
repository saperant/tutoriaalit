# Suorituskyvyn esimerkit: mittaukset ja deterministiset tarkistukset.
#
# Testaaja (make -C .. testaa) kääntää esimerkit sanitoijien kanssa ja
# vertaa toiminnallisten testien tulosteet odotettuihin. Tämä Makefile
# kääntää samat ohjelmat optimoinneilla ja
#
#   make tarkista   ajaa Valgrindin (Cachegrind, Callgrind) ja kääntäjän
#                   raportit; tulokset ovat deterministisiä ja niiden
#                   suhteet tarkistetaan
#   make mittaa     ajaa ajoitusmittaukset; luvut ovat suuntaa-antavia,
#                   eikä niitä verrata mihinkään
#   make            molemmat
#   make tulokset   kirjoittaa kirjassa näytetyt tulosteet hakemistoon
#                   tulokset/ (kirjoittajan koneen luvut)
#   make siivoa     poistaa käännöstuotteet

.NOTPARALLEL:
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

CC    := $(firstword $(shell command -v gcc-14 gcc 2>/dev/null))
LIPUT := -std=c23 -O2 -g -Wall -Wextra -Werror
OTSAKKEET := mittari.h satunnainen.h
KUSTANNUKSET := python3 tyokalut/kustannukset.py
LOKIT := $(wildcard 04-lokit/*.c 04-lokit/*.h) $(OTSAKKEET)
LTO := $(wildcard 09-lto/*.c 09-lto/*.h) $(OTSAKKEET)

# @alku cachegrind
# Simuloitu välimuisti: 32 KiB L1d ja tarkoituksella pieni 256 KiB
# viimeinen taso, jotta pienetkin syötteet ylittävät sen.
VALGRIND   := valgrind -q --log-file=bin/valgrind.log
CACHEGRIND := $(VALGRIND) --tool=cachegrind --cache-sim=yes \
              --D1=32768,8,64 --LL=262144,8,64
# @loppu cachegrind

OHJELMAT := 01-isot 02-kellot 02-toistot 02-poistettu 03-roofline \
            05-lapikaynti 05-askel 05-latenssi 06-hiukkaset \
            06-matriisitulo 06-asettelu 07-haarat 08-vektorointi \
            08-simd 10-areena 10-puskurointi 11-sumennus

.PHONY: kaikki tarkista mittaa tasot tulokset siivoa

kaikki: tarkista mittaa

bin:
	@mkdir -p bin

bin/%: %.c $(OTSAKKEET) | bin
	$(CC) $(LIPUT) $< -o $@ -lm

bin/lokit: $(LOKIT) | bin
	$(CC) $(LIPUT) $(filter %.c,$^) -o $@

# ---------------------------------------------------------------------
# Deterministiset tarkistukset

TARKISTUKSET := lapikaynti matriisitulo hiukkaset haarat gprof callgrind \
                puskuroitu sumennus vektorointi konekoodi lto pgo \
                jarjestelmakutsut

tarkista: $(addprefix tarkista-,$(TARKISTUKSET))
	@echo "OK: tarkistukset"

.PHONY: $(addprefix tarkista-,$(TARKISTUKSET))

# @alku valimuisti
tarkista-lapikaynti: bin/05-lapikaynti
	@echo "== Cachegrind: lapikaynti, n = 1024 =="
	@$(CACHEGRIND) --cachegrind-out-file=bin/lapikaynti.cg \
	    bin/05-lapikaynti --kerran 1024 > /dev/null
	@$(KUSTANNUKSET) cachegrind bin/lapikaynti.cg \
	    summa_riveittain summa_sarakkeittain \
	    --suhde summa_sarakkeittain summa_riveittain D1mr 4
# @loppu valimuisti

tarkista-matriisitulo: bin/06-matriisitulo
	@echo "== Cachegrind: matriisitulo, n = 256 =="
	@$(CACHEGRIND) --cachegrind-out-file=bin/matriisitulo.cg \
	    bin/06-matriisitulo --kerran 256 > /dev/null
	@$(KUSTANNUKSET) cachegrind bin/matriisitulo.cg \
	    tulo_ijk tulo_ikj tulo_lohkottu \
	    --suhde tulo_ijk tulo_ikj D1mr 4 \
	    --suhde tulo_ikj tulo_lohkottu DLmr 4

tarkista-hiukkaset: bin/06-hiukkaset
	@echo "== Cachegrind: hiukkaset, 100000 kpl =="
	@$(CACHEGRIND) --cachegrind-out-file=bin/hiukkaset.cg \
	    bin/06-hiukkaset --kerran 100000 > /dev/null
	@$(KUSTANNUKSET) cachegrind bin/hiukkaset.cg \
	    --tapahtumat Ir,Dr,D1mr siirra_aos siirra_soa \
	    --suhde siirra_aos siirra_soa D1mr 3

# @alku haarat
# Kääntäjä muuttaa haaran usein ehdolliseksi siirroksi (cmov) tai
# vektoroi silmukan. Nämä liput pitävät haaran, jotta ennustus näkyy.
HAARALIPUT := -fno-if-conversion -fno-if-conversion2 -fno-tree-vectorize

bin/07-haarat-haara: 07-haarat.c $(OTSAKKEET) | bin
	$(CC) $(LIPUT) $(HAARALIPUT) $< -o $@

tarkista-haarat: bin/07-haarat-haara
	@echo "== Cachegrind: haarautumisen ennustus, 1000000 tavua =="
	@for d in sekaisin lajiteltu; do \
	    $(VALGRIND) --tool=cachegrind --cache-sim=no --branch-sim=yes \
	        --cachegrind-out-file=bin/haarat-$$d.cg \
	        bin/07-haarat-haara --kerran 1000000 $$d > /dev/null; \
	done
	@$(KUSTANNUKSET) cachegrind bin/haarat-sekaisin.cg \
	    --tapahtumat Ir,Bc,Bcm sekaisin=summa_haarautuva \
	    lajiteltu=bin/haarat-lajiteltu.cg:summa_haarautuva \
	    --suhde sekaisin lajiteltu Bcm 10
# @loppu haarat

# @alku profiilit
bin/lokit-pg: $(LOKIT) | bin
	$(CC) $(LIPUT) -pg $(filter %.c,$^) -o $@

tarkista-gprof: bin/lokit-pg
	@echo "== gprof: lokit, hidas, 20000 rivia =="
	@cd bin && ./lokit-pg --aja hidas 20000 3000 > /dev/null
	@gprof -b -p bin/lokit-pg bin/gmon.out | sed -n '1,10p'

tarkista-callgrind: bin/lokit
	@echo "== Callgrind: lokit, hidas, 8000 rivia, kumulatiivinen =="
	@$(VALGRIND) --tool=callgrind --callgrind-out-file=bin/lokit.cg \
	    bin/lokit --aja hidas 8000 3000 > /dev/null
	@callgrind_annotate --inclusive=yes bin/lokit.cg \
	    | $(KUSTANNUKSET) callgrind --rivit 12
# @loppu profiilit

tarkista-puskuroitu: bin/lokit
	@echo "== Callgrind: lokit, puskuroitu, 8000 rivia, oma =="
	@$(VALGRIND) --tool=callgrind --callgrind-out-file=bin/lokit2.cg \
	    bin/lokit --aja puskuroitu 8000 3000 > /dev/null
	@callgrind_annotate bin/lokit2.cg | $(KUSTANNUKSET) callgrind --rivit 5

tarkista-sumennus: bin/11-sumennus
	@echo "== Cachegrind: sumennus, 256 x 256 =="
	@$(CACHEGRIND) --cachegrind-out-file=bin/sumennus.cg \
	    bin/11-sumennus --kerran 256 > /dev/null
	@$(KUSTANNUKSET) cachegrind bin/sumennus.cg --tapahtumat Ir,Dr,D1mr \
	    sumenna_v1 sumenna_v2 sumenna_v3 sumenna_v4 \
	    --suhde sumenna_v1 sumenna_v4 Ir 10

# @alku vektorointi
bin/vektorointi.o: 08-vektorointi.c $(OTSAKKEET) | bin
	@$(CC) $(LIPUT:-O2=-O3) -fopt-info-vec-optimized -c $< -o $@ \
	    2> bin/vektorointi.txt

tarkista-vektorointi: bin/vektorointi.o
	@echo "== GCC:n vektorointiraportti, -O3 =="
	@grep -E '08-vektorointi.c:(14|24|35|47):' bin/vektorointi.txt \
	    | sort -t: -k2,2n -s | uniq
	@grep -q 'versioned for vectorization because of possible aliasing' \
	    bin/vektorointi.txt
# @loppu vektorointi

tarkista-konekoodi: bin/vektorointi.o
	@echo "== summa_float konekoodina: skalaarikaskyja (addss) =="
	@objdump -d --no-show-raw-insn bin/vektorointi.o \
	    | awk '/<summa_float>:/, /ret/' > bin/summa_float.s
	@grep -E 'addss|addps' bin/summa_float.s | head -4 | cut -f2-
	@! grep -q addps bin/summa_float.s

# @alku lto
bin/lto-ei: $(LTO) | bin
	$(CC) $(LIPUT) $(filter %.c,$^) -o $@

bin/lto-kylla: $(LTO) | bin
	$(CC) $(LIPUT) -flto $(filter %.c,$^) -o $@

tarkista-lto: bin/lto-ei bin/lto-kylla
	@echo "== LTO: kutsuja funktioon etaisyys2 konekoodissa =="
	@for b in lto-ei lto-kylla; do \
	    printf '  %-10s %s\n' $$b \
	        "$$(objdump -d bin/$$b | grep -c 'call.*<etaisyys2>')"; \
	done
	@test "$$(objdump -d bin/lto-kylla | grep -c 'call.*<etaisyys2>')" = 0
	@test "$$(objdump -d bin/lto-ei | grep -c 'call.*<etaisyys2>')" != 0
# @loppu lto

# @alku pgo
# Profiiliohjattu optimointi kahdessa vaiheessa: instrumentoitu ohjelma
# kirjoittaa ajon aikana profiilin, ja toinen käännös käyttää sitä.
bin/lokit-pgo: $(LOKIT) | bin
	$(CC) $(LIPUT) -fprofile-generate -fprofile-dir=bin/pgo \
	    $(filter %.c,$^) -o $@
	./$@ --aja nopea 200000 3000 > /dev/null
	$(CC) $(LIPUT) -fprofile-use -fprofile-dir=bin/pgo \
	    -Werror=missing-profile $(filter %.c,$^) -o $@
# @loppu pgo

tarkista-pgo: bin/lokit bin/lokit-pgo
	@echo "== PGO: sama tulos kuin ilman profiilia =="
	@bin/lokit --aja nopea 50000 3000 > bin/pgo-ei.txt
	@bin/lokit-pgo --aja nopea 50000 3000 > bin/pgo-kylla.txt
	@diff bin/pgo-ei.txt bin/pgo-kylla.txt && echo "  samat"

# @alku strace
# strace -c laskee järjestelmäkutsut. Tapa 0 kirjoittaa rivin
# kerrallaan, tapa 1 stdio-puskurin kautta. Jäljitys vaatii
# ptrace-oikeuden; jos sitä ei ole, tarkistus ohitetaan.
WRITET = awk '$$NF == "write" { print $$4 }' bin/strace-$(1).txt

tarkista-jarjestelmakutsut: bin/10-puskurointi
	@echo "== strace -c: write-kutsut, 100000 rivia =="
	@if ! strace -c -o /dev/null true 2> /dev/null; then \
	    echo "  OHITETTU: strace ei saa jaljittaa tassa ymparistossa"; \
	else \
	    for tapa in 0 1; do \
	        strace -c -e trace=write -o bin/strace-$$tapa.txt \
	            bin/10-puskurointi --kerran $$tapa || exit 1; \
	    done; \
	    printf '  %-22s %7s write-kutsua\n' \
	        "write / rivi" "$$($(call WRITET,0))" \
	        "stdio, oletuspuskuri" "$$($(call WRITET,1))"; \
	    test "$$($(call WRITET,0))" -gt $$((100 * $$($(call WRITET,1)))); \
	fi
# @loppu strace

# ---------------------------------------------------------------------
# Ajoitusmittaukset (suuntaa-antavia)

# Matriisitulo vektoroituna ja koneen omilla käskyillä.
bin/06-matriisitulo-O3: 06-matriisitulo.c $(OTSAKKEET) | bin
	$(CC) $(LIPUT:-O2=-O3) -march=native $< -o $@

mittaa: $(addprefix bin/,$(OHJELMAT)) bin/07-haarat-haara bin/lokit \
        bin/lokit-pgo bin/lto-ei bin/lto-kylla bin/06-matriisitulo-O3 \
        bin/08-vektorointi-O3 tasot
	@for o in $(OHJELMAT); do \
	    echo "== $$o =="; bin/$$o --mittaa || exit 1; \
	done
	@echo "== 06-matriisitulo, -O3 -march=native ==" \
	    && bin/06-matriisitulo-O3 --mittaa
	@echo "== 07-haarat, haarat pakotettu ==" && bin/07-haarat-haara --mittaa
	@echo "== 08-vektorointi, -O3 ==" && bin/08-vektorointi-O3 --mittaa
	@echo "== 04-lokit ==" && bin/lokit --mittaa
	@echo "== 04-lokit, PGO ==" && bin/lokit-pgo --mittaa
	@echo "== 09-lto ==" && bin/lto-ei --mittaa && bin/lto-kylla --mittaa
	@echo "OK: mittaukset"

# @alku tasot
TASOT := -O0 -O1 -O2 -O3 -Os "-O3 -march=native"

tasot: | bin
	@echo "== Optimointitasot: sumennus, vaihe 4 =="
	@for t in $(TASOT); do \
	    $(CC) -std=c23 -g $$t 11-sumennus.c -o bin/tasot || exit 1; \
	    printf '  %-18s koodia %6s tavua  ' "$$t" \
	        "$$(size bin/tasot | awk 'NR == 2 { print $$1 }')"; \
	    bin/tasot --mittaa 4 | awk '/vaihe 4/ { print $$3, $$4 }'; \
	done
# @loppu tasot

bin/08-vektorointi-O3: 08-vektorointi.c $(OTSAKKEET) | bin
	$(CC) $(LIPUT:-O2=-O3) $< -o $@

# Kirjan tulosteet. Ajoitukset vaihtelevat koneittain ja ajoittain.

tulokset: $(addprefix bin/,$(OHJELMAT)) bin/07-haarat-haara bin/lokit \
          bin/lokit-pgo bin/lto-ei bin/lto-kylla bin/06-matriisitulo-O3 \
          bin/08-vektorointi-O3
	@mkdir -p tulokset
	@for o in $(OHJELMAT); do \
	    bin/$$o --mittaa > tulokset/$$o.txt || exit 1; \
	done
	@bin/06-matriisitulo-O3 --mittaa > tulokset/06-matriisitulo-O3.txt
	@bin/07-haarat-haara --mittaa > tulokset/07-haarat-haara.txt
	@bin/08-vektorointi-O3 --mittaa > tulokset/08-vektorointi-O3.txt
	@bin/lokit --mittaa > tulokset/04-lokit.txt
	@bin/lokit-pgo --mittaa > tulokset/04-lokit-pgo.txt
	@(bin/lto-ei --mittaa; bin/lto-kylla --mittaa) > tulokset/09-lto.txt
	@$(MAKE) -s tasot > tulokset/tasot.txt
	@for t in $(TARKISTUKSET); do \
	    $(MAKE) -s tarkista-$$t > tulokset/tarkista-$$t.txt || exit 1; \
	done

siivoa:
	rm -rf bin
