# Koe oikeaa systemd:tä vasten (07-elava/aja.bash). Muut esimerkit ajaa
# yhteinen testaaja; tämä koe tarvitsee koneen, jossa systemd on
# prosessi 1, ja ohittaa itsensä muualla (esimerkiksi kehityskontissa).
SHELL := /bin/bash

.PHONY: kaikki elava siivoa
kaikki: elava

elava:
	@if command -v shellcheck > /dev/null; then \
	    shellcheck 07-elava/aja.bash; fi
	@tulos=$$(bash 07-elava/aja.bash) || { echo "$$tulos"; exit 1; }; \
	case "$$tulos" in \
	OHITETTU*) echo "$$tulos" ;; \
	*) diff -u 07-elava/odotettu.txt <(echo "$$tulos") \
	    && echo "OK: yksiköt ja palvelu oikean systemd:n alla" ;; \
	esac

siivoa:
	@true
