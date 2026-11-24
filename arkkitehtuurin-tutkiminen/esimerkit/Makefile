# Arkkitehtuurin mallinnus: esimerkit.
#
#   make              tarkistaa Pythonin (ruff, mypy --strict) ja
#                     ShellCheckin, ajaa yksikkötestit ja kaikki esimerkit
#                     ja vertaa tulosteita odotettuihin
#   make 05-muisti    yksi esimerkki
#   make siivoa       poistaa build/-hakemiston
#
# C++- ja SystemC-esimerkit ovat hakemistoja NN-nimi/ (ks. testaa.sh),
# Python-esimerkit tiedostoja NN-nimi.py, joiden tulostetta verrataan
# tiedostoon NN-nimi.odotettu. Osa Python-esimerkeistä analysoi
# C++-esimerkin tuottamia tiedostoja hakemistossa build/.

PYTHON := python3
CPP    := $(patsubst %/,%,$(sort $(wildcard [0-9][0-9]-*/)))
PY     := $(basename $(sort $(wildcard [0-9][0-9]-*.py)))
export PYTHONDONTWRITEBYTECODE := 1
MAKEFLAGS += --no-builtin-rules
.DEFAULT_GOAL := kaikki

# @alku riippuvuudet
# Python-esimerkin argumentit: C++-esimerkkien tuottamat tiedostot.
JALJET := build/02-kuormat
args_02-uudelleenkaytto := $(JALJET)
args_02-hutikayra       := $(JALJET)
args_02-tyojoukko       := $(JALJET)
args_03-roofline        := $(JALJET)
args_03-cpi-pino        := $(JALJET)
args_08-energia         := $(JALJET)
args_05-vertailu        := build/05-muisti.saatu
args_06-intervalli      := build/06-ydin.saatu build/06-ydin/kaskyt.txt
args_06-simpoint        := build/06-ydin/intervallit.txt
args_07-jako            := build/07-prototyyppi.saatu
args_10-validointi      := build/06-ydin.saatu build/06-ydin/kaskyt.txt

02-uudelleenkaytto 02-hutikayra 02-tyojoukko 03-roofline 03-cpi-pino \
08-energia: 02-kuormat
05-vertailu: 05-muisti
06-intervalli 06-simpoint 10-validointi: 06-ydin
07-jako: 07-prototyyppi
# @loppu riippuvuudet

.PHONY: kaikki tarkista testit siivoa $(CPP) $(PY)

kaikki: tarkista testit $(CPP) $(PY)
	@echo "OK: $(words $(CPP)) C++-esimerkkiä ja $(words $(PY))" \
	    "Python-esimerkkiä"

tarkista:
	@ruff check --no-cache --quiet . ../kuvat/piirra.py
	@mypy --no-incremental --cache-dir=/dev/null --no-error-summary \
	    . ../kuvat/piirra.py
	@shellcheck testaa.sh $(wildcard */aja.sh)

testit:
	@$(PYTHON) -m pytest -q

$(CPP):
	@./testaa.sh $@

$(PY):
	@tulos=$$($(PYTHON) $@.py $(args_$@)) || \
	    { echo "VIRHE: $@ kaatui"; exit 1; }; \
	printf '%s\n' "$$tulos" | diff -u $@.odotettu - \
	    || { echo "VIRHE: $@ poikkeaa odotetusta"; exit 1; }

siivoa:
	@rm -rf build __pycache__ arkki/__pycache__ testit/__pycache__ \
	    ../kuvat/__pycache__
