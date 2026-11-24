# Taustapalvelujen esimerkit: Maven-projekti, jossa kaksi modulia.
#
#   make           kääntää ja ajaa kaikkien modulien testit (mvnw verify)
#   make aja       käynnistää kauppa-palvelun porttiin 8080
#   make siivoa    poistaa käännöstuotteet
#
# Maven Wrapper (mvnw) lataa oikean Maven-version ensimmäisellä kerralla.

MVN := ./mvnw -B -q

.PHONY: kaikki aja siivoa

kaikki:
	$(MVN) verify

aja:
	$(MVN) -pl kauppa spring-boot:run

siivoa:
	$(MVN) clean
