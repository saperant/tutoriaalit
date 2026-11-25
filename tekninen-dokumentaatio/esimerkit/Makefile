# Tekninen dokumentaatio: esimerkit.
#
#   make             kaikki tarkistukset ja dokumentaation rakennukset
#   make tarkista    ruff ja mypy
#   make pytest      yksikkötestit ja docstringien esimerkit
#   make c           C-kirjaston testi sanitoijien kanssa
#   make doxygen     C-kirjaston viite, varoitukset virheinä
#   make sphinx      Python-kirjaston dokumentaatio ja sen esimerkit
#   make mkdocs      käsikirja, rikkinäiset linkit virheinä
#   make openapi     rajapintakuvaus toteutusta vasten
#   make dokumentit  linkit, proosa, muutosloki ja upotetut tulosteet
#   make adr         päätöslokin rakenne ja hakemisto
#   make kaaviot     koodista tuotetut kaaviot ovat ajan tasalla
#   make naytteet    tarkistimet löytävät näytteiden viat
#   make paivita     kirjoittaa odotetut tulosteet ja kaaviot uudelleen
#   make siivoa      poistaa rakennushakemiston

SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c
export PYTHONPATH := $(CURDIR):$(CURDIR)/tyokalut
export PYTHONDONTWRITEBYTECODE := 1
B := build
CC := gcc-14
# Vertaa komennon tulostetta tiedostoon; PAIVITA=1 kirjoittaa tiedoston.
vertaa = $(if $(PAIVITA),cat > $(1),diff -u $(1) -)
# Työkalujen pitkät ilmoitukset taitetaan, jotta ne mahtuvat sivulle.
TAITA := fold -s -w 76 | sed -e 's/ *$$//'

.PHONY: kaikki tarkista pytest c doxygen sphinx mkdocs openapi \
        dokumentit adr kaaviot naytteet paivita siivoa

kaikki: tarkista pytest c doxygen sphinx mkdocs openapi dokumentit adr \
        kaaviot naytteet

tarkista:
	@ruff check --no-cache --quiet .
	@mypy --no-error-summary --cache-dir=/dev/null \
	    saa testit tyokalut openapi kaaviot naytteet
	@echo "OK: ruff ja mypy"

pytest:
	@python3 -m pytest > $(B).pytest.loki 2>&1 \
	    || { cat $(B).pytest.loki; rm -f $(B).pytest.loki; exit 1; }
	@rm -f $(B).pytest.loki
	@echo "OK: yksikkötestit ja docstringien esimerkit"

c:
	@mkdir -p $(B)/c
	@$(CC) -std=c23 -Wall -Wextra -Werror -g \
	    -fsanitize=address,undefined c/puskuri.c c/testi.c -o $(B)/c/testi
	@$(B)/c/testi | $(call vertaa,c/testi.odotettu)
	@echo "OK: rengaspuskurin testi"

# @alku doxygen
# Viite rakennetaan varoitukset virheinä, ja dokumentoitujen kohteiden
# luetteloa verrataan tallennettuun. Puutteellisen otsakkeen on
# kaaduttava täsmälleen odotettuihin varoituksiin.
doxygen:
	@mkdir -p $(B)
	@cd c && doxygen Doxyfile
	@python3 tyokalut/kohteet.py doxygen $(B)/doxygen/xml/index.xml \
	    | $(call vertaa,c/kohteet.odotettu)
	@cd c && ! { cat Doxyfile; echo "INPUT = puutteellinen.h"; \
	      echo "OUTPUT_DIRECTORY = ../$(B)/doxygen-puutteellinen"; } \
	    | doxygen - > ../$(B)/doxygen-puutteellinen.loki 2>&1
	@sed -e 's#^.*/puutteellinen.h#puutteellinen.h#' \
	    $(B)/doxygen-puutteellinen.loki | awk '!nahty[$$0]++' | $(TAITA) \
	    | $(call vertaa,c/puutteellinen.odotettu)
	@echo "OK: Doxygen"
# @loppu doxygen

# @alku sphinx
# -W tekee varoituksista virheitä, --keep-going näyttää ne kaikki.
# --no-color: tuloste on sama päätteessä ja CI:ssä.
SPHINX := sphinx-build -W --keep-going -q --no-color

sphinx:
	@$(SPHINX) -b html sphinx $(B)/sphinx/html
	@$(SPHINX) -b doctest sphinx $(B)/sphinx/doctest > /dev/null
	@python3 tyokalut/kohteet.py sphinx $(B)/sphinx/html/objects.inv \
	    | $(call vertaa,sphinx/kohteet.odotettu)
	@rm -rf $(B)/sphinx-rikki && mkdir -p $(B)/sphinx-rikki
	@cp -r sphinx $(B)/sphinx-rikki/lahde
	@printf '\nVanha nimi: :func:`saa.tilasto.keskiarvo`.\n' \
	    >> $(B)/sphinx-rikki/lahde/selitys.rst
	@! $(SPHINX) -b html $(B)/sphinx-rikki/lahde $(B)/sphinx-rikki/html \
	    > $(B)/sphinx-rikki/loki 2>&1
	@sed -e 's#^.*/##' $(B)/sphinx-rikki/loki | $(TAITA) \
	    | $(call vertaa,sphinx/rikki.odotettu)
	@echo "OK: Sphinx"
# @loppu sphinx

# @alku mkdocs
# Huomaa: valitsin -q piilottaisi varoitukset myös --strict-tilalta,
# jolloin rikkinäinen linkki menisi läpi. Tuloste ohjataan lokiin.
mkdocs:
	@mkdir -p $(B)
	@mkdocs build --strict -f mkdocs/mkdocs.yml \
	    -d $(CURDIR)/$(B)/mkdocs > $(B)/mkdocs.loki 2>&1 \
	    || { cat $(B)/mkdocs.loki; exit 1; }
	@test -f $(B)/mkdocs/opas/index.html
	@rm -rf $(B)/mkdocs-rikki && mkdir -p $(B)/mkdocs-rikki
	@cp -r mkdocs $(B)/mkdocs-rikki/lahde
	@printf '\nKatso [asetukset](asetukset.md) ja %s.\n' \
	    '[asennus](ohjeet.md#asennus)' \
	    >> $(B)/mkdocs-rikki/lahde/docs/index.md
	@! mkdocs build --strict -f $(B)/mkdocs-rikki/lahde/mkdocs.yml \
	    -d $(CURDIR)/$(B)/mkdocs-rikki/sivusto \
	    > $(B)/mkdocs-rikki/loki 2>&1
	@grep WARNING $(B)/mkdocs-rikki/loki | sed -e 's/  */ /g' | $(TAITA) \
	    | $(call vertaa,mkdocs/rikki.odotettu)
	@echo "OK: MkDocs"
# @loppu mkdocs

# @alku openapi
# Vanhentunut kuvaus tehdään muuttamalla skeeman kentän nimeä: sen on
# jäätävä kiinni.
openapi:
	@mkdir -p $(B)
	@python3 openapi/tarkista.py openapi/saa.yaml \
	    | $(call vertaa,openapi/tarkista.odotettu)
	@sed '/^components:/,$$ s/lampotila_c/lampotila/' openapi/saa.yaml \
	    > $(B)/vanhentunut.yaml
	@! python3 openapi/tarkista.py $(B)/vanhentunut.yaml \
	    > $(B)/vanhentunut.loki
	@cat $(B)/vanhentunut.loki | $(TAITA) \
	    | $(call vertaa,openapi/vanhentunut.odotettu)
	@echo "OK: OpenAPI"
# @loppu openapi

DOKUMENTIT := dokumentit/README.md dokumentit/CONTRIBUTING.md \
    dokumentit/kayttoohjeet/levy-taynna.md $(wildcard mkdocs/docs/*.md)

dokumentit:
	@python3 tyokalut/linkit.py dokumentit mkdocs/docs > /dev/null
	@python3 tyokalut/proosa.py $(DOKUMENTIT) > /dev/null
	@python3 tyokalut/muutosloki.py dokumentit/CHANGELOG.md \
	    pyproject.toml > /dev/null
	@python3 tyokalut/upotukset.py mkdocs/docs/*.md
	@echo "OK: linkit, proosa, muutosloki ja upotetut tulosteet"

adr:
	@python3 tyokalut/adr.py adr | $(call vertaa,adr/hakemisto.odotettu)
	@echo "OK: päätösloki"

# @alku kaaviot
# Koodista tuotettu kaavio on versionhallinnassa. Jos import-lauseet
# muuttuvat, vertailu epäonnistuu, kunnes kaavio päivitetään.
kaaviot:
	@python3 kaaviot/riippuvuudet.py saa dot \
	    | $(call vertaa,kaaviot/riippuvuudet.dot)
	@python3 kaaviot/riippuvuudet.py saa mermaid \
	    | $(call vertaa,kaaviot/riippuvuudet.mmd)
	@python3 kaaviot/riippuvuudet.py saa plantuml \
	    | $(call vertaa,kaaviot/riippuvuudet.puml)
	@for k in kaaviot/*.dot; do dot -Tsvg $$k > /dev/null || exit 1; done
	@echo "OK: kaaviot"
# @loppu kaaviot

naytteet:
	@! python3 tyokalut/linkit.py naytteet/sekava-ohje.md \
	    > $(B).linkit.loki
	@cat $(B).linkit.loki | $(TAITA) \
	    | $(call vertaa,naytteet/sekava-ohje.linkit.odotettu)
	@! python3 tyokalut/proosa.py naytteet/sekava-ohje.md \
	    > $(B).proosa.loki
	@cat $(B).proosa.loki | $(TAITA) \
	    | $(call vertaa,naytteet/sekava-ohje.proosa.odotettu)
	@! python3 tyokalut/kattavuus.py naytteet/ajautunut.py \
	    > $(B).kattavuus.loki
	@cat $(B).kattavuus.loki | $(TAITA) \
	    | $(call vertaa,naytteet/ajautunut.odotettu)
	@python3 tyokalut/kattavuus.py saa | $(call vertaa,saa.kattavuus.odotettu)
	@rm -f $(B).linkit.loki $(B).proosa.loki $(B).kattavuus.loki
	@echo "OK: näytteiden viat löytyvät"

paivita:
	$(MAKE) -s PAIVITA=1 c doxygen sphinx mkdocs openapi adr kaaviot \
	    naytteet

siivoa:
	rm -rf $(B) $(B).*.loki .ruff_cache .mypy_cache .pytest_cache
	find . -name __pycache__ -prune -exec rm -rf {} +
