# Tarkistukset, joita yksittäisten ohjelmien testaaja ei tee:
#
#   tyypit   tarkistaa kaikki esimerkit kerralla tsconfig.json-tiedoston
#            asetuksin (samat kuin testaajalla)
#   testit   ajaa node:test-yksikkötestit (*.test.ts) Nodella, joka
#            poistaa tyypit ajossa
#
# Yksittäinen esimerkki ajetaan suoraan:  node 06-tilakone.ts

TESTIT := $(wildcard */*.test.ts)
# @types/node on asennettu globaalisti (kehityskontti, CI).
TYYPIT := $(shell npm root -g)/@types

.PHONY: kaikki tyypit testit siivoa

kaikki: tyypit testit

tyypit:
	tsc -p . --typeRoots ./node_modules/@types,$(TYYPIT)

testit:
	node --test --test-reporter=dot $(TESTIT)

siivoa:
	@true
