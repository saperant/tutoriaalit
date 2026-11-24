# Kääntäjätekniikka. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := kaantajatekniikka
KIELI   := projekti
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kirjan kaaviot tuotetaan kääntäjän testatuista välitulosteista.
testaa: tarkista-kaaviot
.PHONY: tarkista-kaaviot
tarkista-kaaviot:
	@python3 kaaviot/tee.py --tarkista
