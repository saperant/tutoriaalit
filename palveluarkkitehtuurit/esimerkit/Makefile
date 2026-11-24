# Palveluarkkitehtuurien esimerkit: Maven-projekti, jossa neljä modulia.
#
#   make           kääntää ja ajaa kaikkien modulien testit (mvnw verify)
#   make siivoa    poistaa käännöstuotteet
#
# Maven Wrapper (mvnw) lataa oikean Maven-version ensimmäisellä kerralla.

MVN := ./mvnw -B -q

.PHONY: kaikki siivoa

kaikki:
	$(MVN) verify

siivoa:
	$(MVN) clean
