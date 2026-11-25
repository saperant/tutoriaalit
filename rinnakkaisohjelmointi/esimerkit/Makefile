# ThreadSanitizerin raporttien tarkistus. Hakemiston tsan/ ohjelmissa on
# tarkoituksellinen rinnakkaisuusvirhe: ajon on päätyttävä
# ThreadSanitizerin raporttiin, ja raportissa on oltava tiedoston
# <nimi>.raportti rivit ("..." on jokerimerkki). GCC symboloi pinot itse;
# Clangin raportista tarkistetaan otsikko, koska llvm-symbolizer ei ole
# aina asennettuna. Muut esimerkit testaa yhteinen testaaja.
#
# Hakemiston openmp/ ohjelma käännetään GCC:llä valitsimella -fopenmp
# (libgomp tulee GCC:n mukana), ja sen tulostetta verrataan tiedostoon
# <nimi>.odotettu.
#
# Hakemiston mittaus/ ohjelmat mittaavat aikoja ja havaintojen määriä,
# jotka riippuvat koneesta. Testi vain kääntää ne (ne sisällyttävät
# esimerkkien koodin, joten ne eivät saa vanhentua); `make tulokset`
# ajaa ne optimoituina hiljaisella koneella ja kirjoittaa tulokset
# hakemistoon tulokset/, josta teksti ja kuvat ne lukevat.
GCC   := $(firstword $(shell command -v g++-14 g++ 2>/dev/null))
CLANG := $(firstword $(shell command -v clang++-20 clang++ 2>/dev/null))
LIPUT := -std=c++23 -Wall -Wextra -Wpedantic -Werror -g -fsanitize=thread
OHJELMAT := $(basename $(notdir $(wildcard tsan/*.cc)))
export TSAN_OPTIONS := halt_on_error=1

MITTAUKSET := litmus nopeutus vaara-jakaminen
MITTALIPUT := -std=c++23 -O2 -Wall -Wextra -Wpedantic -Werror -pthread

.PHONY: kaikki rivit openmp mittaus tulokset siivoa $(OHJELMAT)
kaikki: rivit $(OHJELMAT) openmp mittaus

rivit:
	@python3 -c 'import sys; v = [f"{t}:{n}: rivi on liian pitkä" \
	    for t in sys.argv[1:] for n, r in enumerate(open(t, \
	    encoding="utf-8"), 1) if len(r.rstrip("\n")) > 78]; \
	    print(*v, sep="\n") if v else None; sys.exit(bool(v))' \
	    tsan/*.cc tsan/*.raportti tsan/*.sh openmp/*.cc mittaus/*.cc

openmp:
	@mkdir -p bin
	@if ! echo 'int main(){}' | $(GCC) -x c++ -fopenmp - \
	    -o bin/openmp-testi 2>/dev/null; then \
	    echo "OHITETTU: kääntäjä ilman OpenMP:tä"; \
	else \
	    $(GCC) -std=c++23 -Wall -Wextra -Wpedantic -Werror -g -fopenmp \
	        -fsanitize=address,undefined openmp/tyonjako.cc \
	        -o bin/openmp-tyonjako && \
	    bin/openmp-tyonjako | diff openmp/tyonjako.odotettu - && \
	    echo "OK: openmp/tyonjako"; \
	fi

$(OHJELMAT): %:
	@mkdir -p bin
	@for k in $(GCC):kaikki $(CLANG):otsikko; do \
	    cxx=$${k%%:*}; tila=$${k##*:}; n=$$(basename $$cxx); \
	    [ -n "$$cxx" ] || continue; \
	    if ! echo 'int main(){}' | $$cxx -x c++ -fsanitize=thread - \
	        -o bin/$@-testi-$$n 2>/dev/null || ! bin/$@-testi-$$n; then \
	        echo "OHITETTU: $$n ilman ThreadSanitizeria"; continue; \
	    fi; \
	    $$cxx $(LIPUT) tsan/$@.cc -o bin/$@-$$n || exit 1; \
	    if bin/$@-$$n > /dev/null 2> bin/$@-$$n.raportti; then \
	        echo "VIRHE: $@ ($$n) ei tuottanut raporttia"; exit 1; \
	    fi; \
	    tsan/tarkista.sh tsan/$@.raportti bin/$@-$$n.raportti $$tila \
	        || { echo "VIRHE: $@ ($$n)"; exit 1; }; \
	done
	@echo "OK: $@ (ThreadSanitizer-raportti)"

# @alku mittaus
mittaus:
	@mkdir -p bin
	@for m in $(MITTAUKSET); do \
	    $(GCC) $(MITTALIPUT) mittaus/$$m.cc -o bin/mittaus-$$m || exit 1; \
	done
	@echo "OK: mittausohjelmat kääntyvät"

tulokset: mittaus
	@mkdir -p tulokset
	bin/mittaus-litmus > tulokset/04-litmus.txt
	bin/mittaus-nopeutus > tulokset/10-nopeutus.txt
	bin/mittaus-vaara-jakaminen > tulokset/10-vaara-jakaminen.txt
# @loppu mittaus

siivoa:
	rm -rf bin
