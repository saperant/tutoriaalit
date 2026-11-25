# Web-sovellusten esimerkit: npm-projekti (Vite, React, Vitest,
# Playwright). paketti.mk ajaa tämän osana "make testaa"-kohdetta.
#
#   make           asentaa riippuvuudet ja ajaa kaikki tarkistukset
#   make siivoa    poistaa käännöstuotteet (riippuvuudet jäävät)
#   make kuvat     ottaa tutoriaalin kuvakaappaukset (../kuvat)
#
# Kehitys:  node palvelin/api.ts  ja toisessa päätteessä  npm run dev

DEMOT := src/03-tila/signaali-demo

.PHONY: kaikki tyypit testit kaannos e2e demot kuvat siivoa

kaikki: tyypit testit e2e demot

# Riippuvuudet lukitustiedoston mukaan; npm ci vain, kun lukitus muuttuu.
node_modules/.package-lock.json: package-lock.json
	npm ci --no-audit --no-fund --loglevel=error

tyypit: node_modules/.package-lock.json
	npx tsc --noEmit -p .

testit: node_modules/.package-lock.json
	npx vitest run --reporter=dot

kaannos: node_modules/.package-lock.json
	npx vite build --logLevel warn

e2e: kaannos
	npx playwright test --reporter=dot

demot: node_modules/.package-lock.json
	@for d in $(DEMOT); do \
	    node $$d.ts | diff -u $$d.odotettu - || exit 1; \
	done

# Kuvitus ei kuulu testeihin: kuvat ovat versionhallinnassa.
kuvat: kaannos
	npx playwright test -c playwright.kuvat.config.ts --reporter=dot

siivoa:
	rm -rf dist test-results playwright-report
