# JavaScript-esimerkkien lisätarkistukset. Yksittäiset ohjelmat ajetaan
# suoraan, esim.  node 03-syote.js < 03-syote.syote
#
#   make          tyyppitarkistus koko hakemistolle (tsconfig.json) ja
#                 node:test-testit hakemistoesimerkeistä
#   make siivoa   ei luotavia tiedostoja; olemassa yhtenäisyyden vuoksi
#
# Tyyppimäärittelyt @types/node haetaan paikallisesta node_modules-
# hakemistosta (npm install) tai globaalista asennuksesta.

TYYPIT := $(firstword $(wildcard node_modules/@types) \
                      $(shell npm root -g 2>/dev/null)/@types)

.PHONY: kaikki tyypit testit siivoa

kaikki: tyypit testit

tyypit:
	tsc -p . --typeRoots $(TYYPIT)

testit:
	node --test --test-reporter=dot "09-varasto/*.test.js" \
	    "11-testit/*.test.js"

siivoa:
	@true
