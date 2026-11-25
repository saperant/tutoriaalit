# Web-sovellusten tietoturvan esimerkit: npm-projekti (Node.js,
# TypeScript, node:test ja Playwright). paketti.mk ajaa tämän osana
# "make testaa"-kohdetta.
#
#   make           asentaa riippuvuudet ja ajaa kaikki tarkistukset
#   make naytos    hyökkäysten tulokset tauluina (verrataan tallennettuun)
#   make kokeile   käynnistää luvun 3 palstan omaan selaimeen
#   make siivoa    poistaa testiraportit (riippuvuudet jäävät)

NODE := node --disable-warning=ExperimentalWarning

.PHONY: kaikki tyypit testit naytos e2e kokeile paivita-naytokset siivoa

kaikki: tyypit testit naytos e2e

# Riippuvuudet lukitustiedoston mukaan; npm ci vain, kun lukitus muuttuu.
node_modules/.package-lock.json: package-lock.json
	npm ci --no-audit --no-fund --loglevel=error

tyypit: node_modules/.package-lock.json
	npx tsc --noEmit -p .

testit: node_modules/.package-lock.json
	$(NODE) --test --test-reporter=dot "src/**/*.test.ts"

# @alku naytos
# Näytösajot: sama hyökkäys haavoittuvaa ja korjattua versiota vastaan,
# tulos tauluna. Tuloste verrataan tallennettuun (naytos/*.odotettu),
# joten kirjan tulostelohkot ovat aina oikean ajon tuloksia.
naytos: node_modules/.package-lock.json
	@for n in $$($(NODE) src/naytos.ts --lista); do \
	  $(NODE) src/naytos.ts $$n | diff -u naytos/$$n.odotettu - || exit 1; \
	done; echo "OK: näytösajot"

# Selaintestit kirjoittavat omat taulunsa hakemistoon
# test-results/naytos, ja ne verrataan samoin.
e2e: node_modules/.package-lock.json
	npx playwright test --reporter=dot
	@for t in test-results/naytos/*.txt; do \
	  diff -u naytos/$$(basename $$t .txt).odotettu $$t || exit 1; \
	done; echo "OK: selaintestien taulut"
# @loppu naytos

# Luvun 3 palsta omaan selaimeen (kuuntelee vain osoitetta 127.0.0.1):
#   make kokeile                         ei puolustuksia
#   make kokeile PUOLUSTUS="koodaus csp" molemmat puolustukset
kokeile: node_modules/.package-lock.json
	$(NODE) src/kokeile.ts $(PUOLUSTUS)

# Tallentaa nykyiset näytöstulosteet odotetuiksi (aja e2e ensin).
paivita-naytokset: node_modules/.package-lock.json
	@mkdir -p naytos
	@for n in $$($(NODE) src/naytos.ts --lista); do \
	  $(NODE) src/naytos.ts $$n > naytos/$$n.odotettu; done
	@for t in test-results/naytos/*.txt; do \
	  cp $$t naytos/$$(basename $$t .txt).odotettu; done

siivoa:
	rm -rf test-results playwright-report
