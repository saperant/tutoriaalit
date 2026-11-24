# minihls ja sen esimerkit.
#
#   make           tarkistaa minihls:n (ruff, mypy --strict, ShellCheck)
#                  ja ajaa kaikki esimerkit (rinnakkain valitsimella -j)
#   make 07-matriisi   vain yksi esimerkki
#   make siivoa    poistaa hakemiston rakennus/
#
# Esimerkin vuo on kuvattu tiedostossa testaa.sh.

ESIMERKIT := $(sort $(wildcard [0-9][0-9]-*))

.PHONY: kaikki tarkistukset siivoa $(ESIMERKIT)

kaikki: $(ESIMERKIT)
	@echo "OK: $(words $(ESIMERKIT)) esimerkkiä"

tarkistukset:
	ruff check --no-cache -q minihls tyokalut
	mypy --strict --no-error-summary --cache-dir=rakennus/mypy \
	    minihls tyokalut
	shellcheck testaa.sh

$(ESIMERKIT): tarkistukset
	@./testaa.sh $@

siivoa:
	rm -rf rakennus
