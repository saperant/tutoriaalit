# Palveluarkkitehtuurin tietoturvan esimerkit: Maven-projekti, jossa
# viisi modulia.
#
#   make           kääntää ja ajaa kaikkien modulien testit (mvnw verify)
#   make siivoa    poistaa käännöstuotteet
#
# Maven Wrapper (mvnw) lataa oikean Maven-version ensimmäisellä kerralla.
# Testit eivät tarvitse verkkoa (riippuvuuksien latausta lukuun
# ottamatta) eivätkä Dockeria: varmentaja, salaisuuspalvelu ja palvelut
# käynnistetään testin sisällä.

MVN := ./mvnw -B -q

.PHONY: kaikki siivoa

kaikki:
	$(MVN) verify

siivoa:
	$(MVN) clean
