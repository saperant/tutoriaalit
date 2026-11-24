# Järjestelmäkutsujen jäljitys straceliä. Esimerkki käännetään
# staattisesti, jotta dynaamisen linkittäjän kutsut eivät näy
# jäljessä. Jos stracea ei ole tai ptrace on estetty (esim. kontissa
# ilman oikeuksia), jäljitys ohitetaan.
EHDOKKAAT := gcc-14 gcc clang-20 clang cc
CC := $(firstword $(shell command -v $(EHDOKKAAT) 2>/dev/null))
KUTSUT := openat,read,write,close

.PHONY: kaikki jaljita siivoa
kaikki: jaljita

bin/viesti: 02-viesti.c tarkista.h
	@mkdir -p bin
	$(CC) -std=c23 -O1 -static -Wall -Wextra -Werror $< -o $@

jaljita: bin/viesti
	@if ! command -v strace >/dev/null; then \
	    echo "OHITETTU: strace puuttuu"; \
	elif ! strace -qq -o /dev/null true 2>/dev/null; then \
	    echo "OHITETTU: ptrace ei ole sallittu"; \
	else \
	    cd bin && strace -qq -o viesti.strace -e trace=$(KUTSUT) \
	        ./viesti >/dev/null && \
	    diff ../jaljitys/02-viesti.odotettu viesti.strace && \
	    echo "OK: strace-jäljitys"; \
	fi

siivoa:
	rm -rf bin
