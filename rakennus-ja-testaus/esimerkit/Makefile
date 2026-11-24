# Käännösjärjestelmät, testaus ja CI: esimerkit.
#
#   make              tarkistaa skriptit ja ajaa kaikki esimerkit
#   make 03-make-syvemmin   ajaa yhden esimerkin
#   make paivita      kirjoittaa odotetut tulosteet uudelleen (vain kun
#                     muutos on tarkistettu käsin)
#
# Jokainen esimerkki on hakemisto, jossa on aja.sh. Ajo tehdään
# tilapäishakemistossa (aja-esimerkki.sh), joten esimerkit voi ajaa
# rinnakkain (-j) eikä tänne jää käännöstuotteita.

ESIMERKIT := $(sort $(patsubst %/aja.sh,%,$(wildcard */aja.sh)))

.PHONY: kaikki shellcheck paivita siivoa $(ESIMERKIT)

kaikki: shellcheck $(ESIMERKIT)

shellcheck:
	@shellcheck -x aja-esimerkki.sh */aja.sh
	@echo "OK: ShellCheck"

$(ESIMERKIT):
	@./aja-esimerkki.sh $@

paivita:
	@for e in $(ESIMERKIT); do PAIVITA=1 ./aja-esimerkki.sh $$e; done

siivoa:
	@true
