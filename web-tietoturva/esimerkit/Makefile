# Web-sovellusten tietoturvan esimerkit: npm-projekti (Node.js,
# TypeScript, node:test ja Playwright). paketti.mk ajaa tämän osana
# "make testaa"-kohdetta.
#
#   make           asentaa riippuvuudet ja ajaa kaikki tarkistukset
#   make siivoa    poistaa testiraportit (riippuvuudet jäävät)

NODE := node --disable-warning=ExperimentalWarning

.PHONY: kaikki tyypit testit e2e siivoa

kaikki: tyypit testit e2e

# Riippuvuudet lukitustiedoston mukaan; npm ci vain, kun lukitus muuttuu.
node_modules/.package-lock.json: package-lock.json
	npm ci --no-audit --no-fund --loglevel=error

tyypit: node_modules/.package-lock.json
	npx tsc --noEmit -p .

testit: node_modules/.package-lock.json
	$(NODE) --test --test-reporter=dot "src/**/*.test.ts"

e2e: node_modules/.package-lock.json
	npx playwright test --reporter=dot

siivoa:
	rm -rf test-results playwright-report
