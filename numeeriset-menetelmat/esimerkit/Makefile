# GNU Octave -esimerkit, joita yhteinen testaaja ei aja:
#
#   make           ajaa octave/*.m-skriptit ja vertaa tulosteet
#                  tiedostoihin octave/*.odotettu
#   make siivoa    poistaa välimuistit
#
# Yksittäinen skripti ajetaan esimerkiksi näin:
#   cd octave && octave --no-gui --quiet --norc 03-juuret.m

OCTAVE := $(sort $(wildcard octave/*.m))

.PHONY: kaikki siivoa $(OCTAVE)

kaikki: $(OCTAVE)

# @alku octave
# --norc ohittaa käyttäjän asetukset, ja --no-window-system estää
# grafiikkaikkunat. Varoitukset (virhetuloste) eivät kuulu vertailuun.
$(OCTAVE):
	@cd octave && octave --no-gui --no-window-system --quiet --norc \
	    $(notdir $@) 2>/dev/null \
	  | diff -u $(notdir $(@:.m=.odotettu)) -
# @loppu octave

siivoa:
	find . -name __pycache__ -o -name .mypy_cache | xargs rm -rf
