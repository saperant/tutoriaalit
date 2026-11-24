# Maxima-esimerkit, joita yhteinen testaaja ei aja:
#
#   make           ajaa maxima/*.mac-skriptit ja vertaa tulosteet
#                  tiedostoihin maxima/*.odotettu
#   make siivoa    poistaa välimuistit
#
# Yksittäinen skripti ajetaan esimerkiksi näin:
#   cd maxima && maxima --very-quiet -b 02-perusteet.mac

MAXIMA := $(sort $(wildcard maxima/*.mac))

.PHONY: kaikki siivoa $(MAXIMA)

kaikki: $(MAXIMA)

# @alku maxima
# batchload ajaa skriptin tulostamatta komentoja; vain print-kutsujen
# tuloste jää. Ohjelman kaiku ja rivien lopun välilyönnit poistetaan.
$(MAXIMA):
	@cd maxima && maxima --very-quiet \
	    --batch-string='batchload("$(notdir $@)")$$' 2>/dev/null \
	  | sed -e '/^$$/d' -e '/^batchload(/d' -e 's/ *$$//' \
	  | diff -u $(notdir $(@:.mac=.odotettu)) -
# @loppu maxima

siivoa:
	find . -name __pycache__ -o -name .mypy_cache | xargs rm -rf
