# 3D-peliohjelmoinnin esimerkit, joita yhteinen testaaja ei aja.
#
#   make             tarkistaa, että glTF-resurssit vastaavat generaattoria
#   make resurssit   tuottaa resurssit uudelleen hakemistoon resurssit/
#   make siivoa      poistaa väliaikaiset tiedostot
#
# C++-esimerkit käännetään kuten tutoriaalin testeissä, esimerkiksi
#   g++ -std=c++23 -Wall -Wextra -fsanitize=address,undefined 09-hahmo.cpp

SHELL := /bin/bash
GEN   := resurssit/tee_resurssit.py
TMP   := build/resurssit

.PHONY: kaikki tarkista-resurssit resurssit siivoa

kaikki: tarkista-resurssit

# @alku tarkistus
# Generaattori ajetaan väliaikaiseen hakemistoon, ja tulosta verrataan
# versionhallinnassa oleviin tiedostoihin tavu tavulta.
tarkista-resurssit:
	@if command -v ruff >/dev/null; then ruff check --no-cache -q $(GEN); fi
	@mkdir -p $(TMP) && python3 $(GEN) $(TMP)
	@for f in hahmo.gltf hahmo.bin taso.gltf taso.bin; do \
	    cmp $(TMP)/$$f resurssit/$$f || exit 1; \
	done
	@echo "OK: glTF-resurssit vastaavat generaattoria"
# @loppu tarkistus

resurssit:
	python3 $(GEN) resurssit

siivoa:
	rm -rf build
