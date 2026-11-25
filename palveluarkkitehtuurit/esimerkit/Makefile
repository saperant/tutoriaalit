# Palveluarkkitehtuurien esimerkit: Maven-projekti, jossa neljä modulia.
#
#   make           kääntää ja ajaa kaikkien modulien testit (mvnw verify)
#                  ja tarkistaa lähdekoodista tuotetut kaaviot
#   make kaaviot   vertaa tilakonekaaviota koodista tuotettuun
#   make siivoa    poistaa käännöstuotteet
#
# Maven Wrapper (mvnw) lataa oikean Maven-version ensimmäisellä kerralla.

MVN := ./mvnw -B -q

.PHONY: kaikki testit kaaviot siivoa

kaikki: kaaviot testit

testit:
	$(MVN) verify

# Luvun 10 tilakonekaavio tuotetaan orkestroijan lähdekoodista. Jos
# siirtymät muuttuvat, tallennettu kaavio on päivitettävä:
#   python3 kaaviot/saga_tilat.py > kaaviot/saga-tilat.dot
kaaviot:
	python3 kaaviot/saga_tilat.py | diff -u kaaviot/saga-tilat.dot -
	@echo "OK: kaaviot/saga-tilat.dot"

siivoa:
	$(MVN) clean
