# Maxima- ja Octave-esimerkit, joita yhteinen testaaja ei aja:
#
#   make           ajaa maxima/*.mac- ja octave/*.m-skriptit ja vertaa
#                  tulosteet tiedostoihin *.odotettu
#   make paivita   kirjoittaa odotetut tulosteet uudelleen
#   make siivoa    poistaa välimuistit
#
# Yksittäinen skripti ajetaan esimerkiksi näin:
#   cd maxima && maxima --very-quiet -b 06-laplace.mac
#   cd octave && octave --no-gui --quiet --norc 01-kahvi.m

SHELL  := /bin/bash
.SHELLFLAGS := -o pipefail -c

MAXIMA := $(sort $(wildcard maxima/*.mac))
OCTAVE := $(sort $(wildcard octave/*.m))

.PHONY: kaikki paivita siivoa $(MAXIMA) $(OCTAVE)

kaikki: $(MAXIMA) $(OCTAVE)

# @alku ajo
# Maxima: batchload ajaa skriptin tulostamatta komentoja; vain
# print-kutsujen tuloste jää. Rivien lopun välilyönnit, tyhjät rivit ja
# ohjelman kaiku poistetaan.
maxima_ajo = (cd maxima && maxima --very-quiet \
	--batch-string='batchload("$(notdir $(1))")$$' 2>/dev/null \
	| sed -e 's/ *$$//' -e '/^$$/d' -e '/^batchload(/d')

# Octave: --norc ohittaa käyttäjän asetukset, ja virhetuloste (ilmoitus
# puuttuvasta näytöstä) jätetään pois. Virhe skriptissä näkyy
# paluuarvona.
octave_ajo = (cd octave && octave --no-gui --quiet --norc \
	$(notdir $(1)) 2>/dev/null)
# @loppu ajo

$(MAXIMA):
	@diff -u $(@:.mac=.odotettu) <($(call maxima_ajo,$@))

$(OCTAVE):
	@diff -u $(@:.m=.odotettu) <($(call octave_ajo,$@))

paivita:
	@$(foreach f,$(MAXIMA),$(call maxima_ajo,$(f)) > $(f:.mac=.odotettu);)
	@$(foreach f,$(OCTAVE),$(call octave_ajo,$(f)) > $(f:.m=.odotettu);)

siivoa:
	find . -name __pycache__ -prune -exec rm -r {} +
