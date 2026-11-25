# Kehitysympäristöt ja Dev Containers: esimerkit.
#
#   make             kaikki tarkistukset
#   make tarkista    ruff ja mypy
#   make yksikko     tarkistimen ja kesto-projektin testit
#   make devkontti   devcontainer.json-tiedostojen tarkistus
#   make kokoelma    tutoriaalikokoelman kehityskonttien säännöt
#   make kontti      rakentaa kesto-projektin kehityskontin Dockerilla
#                    ja ajaa projektin testit siinä; ohitetaan, jos
#                    Docker ei ole käytettävissä
#   make siivoa      poistaa välimuistit ja rakennetun kuvan

SHELL := /bin/bash
export PYTHONPATH := $(CURDIR)
export PYTHONDONTWRITEBYTECODE := 1

TIEDOSTOT := $(sort $(wildcard muunnelmat/*.json)) \
             projekti/.devcontainer/devcontainer.json

.PHONY: kaikki tarkista yksikko devkontti kokoelma kontti siivoa

kaikki: tarkista yksikko devkontti kokoelma kontti

tarkista:
	@ruff check --no-cache --quiet .
	@mypy --no-error-summary --cache-dir=/dev/null devkontti.py \
	    kokoelma.py aja_kontissa.py testit projekti
	@echo "OK: tarkistukset"

yksikko:
	@python3 -m pytest -q -p no:cacheprovider testit > /dev/null \
	    && echo "OK: tarkistimen testit"
	@$(MAKE) -s -C projekti testaa > /dev/null \
	    && echo "OK: kesto-projektin testit"

# Virhe-esimerkkien vuoksi tarkistin palauttaa virhekoodin; vain
# tulostetta verrataan.
devkontti:
	@diff -u devkontti.odotettu <(python3 devkontti.py $(TIEDOSTOT)) \
	    && echo "OK: devkontti"

# Zip-paketissa ei ole koko repositoriota, jolloin tarkistus ohitetaan.
kokoelma:
	@tuloste=$$(python3 kokoelma.py) || { echo "$$tuloste"; exit 1; }; \
	case "$$tuloste" in OHITETTU*) echo "$$tuloste" ;; \
	*) diff -u kokoelma.odotettu <(echo "$$tuloste") \
	    && diff -u tyokalut.odotettu \
	        <(python3 kokoelma.py tyokalut kehitysymparistot) \
	    && echo "OK: kokoelma" ;; esac

# pytestin pisterivi ja kesto jätetään pois, jotta tuloste on aina sama.
kontti:
	@tuloste=$$(timeout 900 python3 aja_kontissa.py projekti make testaa \
	    | grep -v '%\]$$' | sed -E 's/ in [0-9.]+s$$//'); \
	case "$$tuloste" in OHITETTU*) echo "$$tuloste" ;; \
	*) diff -u kontti.odotettu <(echo "$$tuloste") \
	    && echo "OK: kontti" ;; esac

siivoa:
	@rm -rf .ruff_cache .mypy_cache .pytest_cache
	@find . -name __pycache__ -prune -exec rm -rf {} +
	-@docker rmi -f devkontti-projekti > /dev/null 2>&1
