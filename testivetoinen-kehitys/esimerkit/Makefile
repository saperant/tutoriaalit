# Testivetoinen kehitys ja testisuunnittelu: esimerkit.
#
#   make                  tarkistaa ja ajaa kaikki esimerkit
#   make 04-rajat         yksi esimerkki: mypy --strict, ajo ja vertailu
#                         tiedostoon 04-rajat/odotettu
#   make paivita          kirjoittaa odotetut tulosteet uudelleen
#
# Esimerkkihakemisto on tavallinen pytest-projekti, joten sen testit voi
# ajaa myös suoraan:  cd 04-rajat && python3 -m pytest
#
# Osa esimerkeistä sisältää tarkoituksella epäonnistuvia testejä: ne
# näyttävät, minkä vian testi löytää. Siksi tulosta verrataan
# tallennettuun eikä katsota pytestin paluuarvoa (ks. aja.py).

export PYTHONDONTWRITEBYTECODE := 1

ESIMERKIT := $(sort $(patsubst %/odotettu,%,\
    $(wildcard */odotettu */*/odotettu)))
# Vaiheessa 1 testattavaa moduulia ei vielä ole, joten mypy ohitetaan.
EI_TYYPPEJA := 02-tdd/1-punainen
valitsin = $(if $(filter $(1),$(EI_TYYPPEJA)),--ei-tyyppeja)

.PHONY: kaikki tarkista paivita siivoa $(ESIMERKIT)

kaikki: tarkista $(ESIMERKIT)

tarkista:
	ruff check --no-cache --quiet .
	mypy --strict --no-error-summary --cache-dir=/dev/null \
	    aja.py tulostin.py

$(ESIMERKIT):
	@python3 aja.py $(call valitsin,$@) $@

paivita:
	@$(foreach e,$(ESIMERKIT),\
	    python3 aja.py --kirjoita $(call valitsin,$(e)) $(e) &&) true

# Ajo ei jätä jälkiä: välimuistit ovat väliaikaishakemistossa (aja.py).
siivoa:
	@true
