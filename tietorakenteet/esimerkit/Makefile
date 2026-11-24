# Tietorakenteiden esimerkit.
#
# Testaaja (make -C .. testaa) kääntää ja ajaa varsinaiset esimerkit
# sanitoijien kanssa ilman optimointeja. Tämä Makefile ajaa lisäksi
# ajoitusmittauksen optimoidulla käännöksellä, koska sanitoijat ja -O0
# vääristäisivät välimuistin vaikutuksen.
#
#   make           mittaus ja tuloksen vertailu odotettuun
#   make siivoa    poistaa käännöstuotteet

CC := $(firstword $(shell command -v gcc-14 gcc clang-20 clang cc 2>/dev/null))

.PHONY: kaikki mittaa siivoa

kaikki: mittaa

bin/aika: mittaus/src/aika.c satunnainen.h
	@mkdir -p bin
	$(CC) -std=c23 -O2 -Wall -Wextra -Werror $< -o $@

mittaa: bin/aika
	@./bin/aika > bin/aika.tuloste
	@diff mittaus/aika.odotettu bin/aika.tuloste
	@echo "OK: ajoitusmittaus"

siivoa:
	rm -rf bin
