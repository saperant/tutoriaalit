# Esimerkkien apukohteet. Tutoriaalin testaaja (make -C .. testaa)
# kääntää ja ajaa kaikki esimerkit sanitoijien kanssa ilman optimointeja.
# Tämä Makefile ajaa lisäksi kokeet, joissa optimointi ratkaisee:
#
#   make           molemmat alla olevat
#   make nopea     -ffast-math: 07-nopea.c tavallisena ja nopeana
#   make mittaa    välimuistikokeet 10 ja 11 optimoituina (-O2)
#   make siivoa    poistaa käännetyt ohjelmat

CC := $(shell command -v gcc-14 >/dev/null 2>&1 && echo gcc-14 || echo gcc)

.PHONY: kaikki nopea mittaa siivoa

kaikki: nopea mittaa

# @alku nopea
nopea: bin/nopea-tavallinen bin/nopea-ffast-math
	./bin/nopea-tavallinen | diff -u 07-nopea.odotettu -
	./bin/nopea-ffast-math | diff -u 07-nopea-ffast-math.odotettu -

bin/nopea-tavallinen: 07-nopea.c
	@mkdir -p bin
	$(CC) -std=c23 -O2 $< -o $@ -lm

bin/nopea-ffast-math: 07-nopea.c
	@mkdir -p bin
	$(CC) -std=c23 -O2 -ffast-math $< -o $@ -lm
# @loppu nopea

mittaa: bin/10-jarjestys bin/11-matriisitulo
	./bin/10-jarjestys mittaa | diff -u 10-jarjestys-mittaus.odotettu -
	./bin/11-matriisitulo mittaa | diff -u 11-matriisitulo-mittaus.odotettu -

bin/%: %.c
	@mkdir -p bin
	$(CC) -std=c23 -O2 $< -o $@ -lm

siivoa:
	rm -rf bin
