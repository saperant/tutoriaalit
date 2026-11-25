# Web-sovelluskehysten esimerkit: sama sovellus viidellä tavalla yhdessä
# npm-projektissa. paketti.mk ajaa tämän osana "make testaa"-kohdetta.
#
#   make           asentaa riippuvuudet ja ajaa kaikki tarkistukset
#   make tulokset  päivittää tekstissä näytetyt mittaukset ja tulosteet
#   make kuvat     ottaa tekstin kuvituskuvan (../kuvat/sovellus.png)
#   make siivoa    poistaa käännöstuotteet (riippuvuudet jäävät)
#
# Kehityspalvelin yhdelle toteutukselle, esim.:
#   npx vite --config vue/vite.config.ts      (Angular: npx ng serve)

TOTEUTUKSET := paljas react vue angular svelte
PERIAATTEET := vdom signaalit muutostentunnistus kaantaja sailo palvelin
SIVUT       := $(TOTEUTUKSET:%=dist/%/index.html)
export NG_CLI_ANALYTICS := false

.PHONY: kaikki tyypit yksikko periaatteet riippuvuudet kaannos e2e \
        mitat tulokset kuvat siivoa

kaikki: tyypit yksikko periaatteet riippuvuudet e2e mitat

# Riippuvuudet lukitustiedoston mukaan; npm ci vain, kun lukitus muuttuu.
node_modules/.package-lock.json: package-lock.json
	npm ci --no-audit --no-fund --loglevel=error

# @alku tyypit
# Jokaisella kehyksellä on oma tyyppitarkistimensa: mallipohjat ovat
# TypeScriptin näkökulmasta vierasta kieltä. Angularin mallipohjat
# tarkistaa sen oma kääntäjä käännöksen yhteydessä.
tyypit: node_modules/.package-lock.json
	npx tsc --noEmit -p .
	npx tsc --noEmit -p paljas
	npx tsc --noEmit -p react
	npx vue-tsc --noEmit -p vue
	npx svelte-check --workspace svelte --tsconfig ./tsconfig.json \
	    --fail-on-warnings --output machine > /dev/null \
	  || npx svelte-check --workspace svelte --tsconfig ./tsconfig.json
# @loppu tyypit

yksikko: node_modules/.package-lock.json
	node --test --test-reporter=dot yhteinen/logiikka.test.ts

periaatteet: node_modules/.package-lock.json
	@for p in $(PERIAATTEET); do \
	    node periaatteet/$$p.ts | diff -u periaatteet/$$p.odotettu - \
	      || exit 1; \
	done

riippuvuudet:
	@node tyokalut/riippuvuudet.ts \
	  | diff -u tyokalut/riippuvuudet.odotettu -

# Käännökset: kolme Vitellä ja liitännäisellä, Angular omalla
# komentorivityökalullaan (joka käyttää sisäisesti samoja työkaluja).
dist/angular/index.html: node_modules/.package-lock.json angular.json \
    $(shell find angular yhteinen -type f)
	@mkdir -p dist
	@npx ng build --progress=false > dist/angular.log 2>&1 \
	  || { cat dist/angular.log; exit 1; }

dist/%/index.html: node_modules/.package-lock.json \
    $(shell find paljas react vue svelte yhteinen -type f)
	npx vite build --config $*/vite.config.ts --logLevel warn

kaannos: $(SIVUT)

e2e: kaannos
	npx playwright test --reporter=dot

mitat: kaannos
	@node tyokalut/mitat.ts --tarkista

tulokset: kaannos
	node tyokalut/mitat.ts > tulokset/mitat.txt
	node tyokalut/riippuvuudet.ts > tyokalut/riippuvuudet.odotettu
	for p in $(PERIAATTEET); do \
	    node periaatteet/$$p.ts > periaatteet/$$p.odotettu; \
	done

kuvat: kaannos
	@mkdir -p ../kuvat
	node tyokalut/kuva.ts

siivoa:
	rm -rf dist test-results playwright-report .angular
