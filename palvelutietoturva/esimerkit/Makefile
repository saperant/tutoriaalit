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

.PHONY: kaikki paivita-naytokset siivoa

# Testien joukossa ovat näytösajot (NaytosTest.java): ne kirjoittavat
# kokeiden tulokset tauluiksi hakemistoon target/naytos ja vertaavat
# niitä tiedostoihin naytos/*.odotettu, jotka näytetään kirjassa.
kaikki:
	$(MVN) verify

# Tallentaa viimeisimmän ajon taulut odotetuiksi.
paivita-naytokset:
	$(MVN) -Dmaven.test.failure.ignore=true verify > /dev/null
	@for t in */target/naytos/*.txt; do \
	  cp $$t naytos/$$(basename $$t .txt).odotettu; done

siivoa:
	$(MVN) clean
