# Palvelintietokantojen esimerkit (PostgreSQL ja MariaDB) ja Java-otteiden
# käännöstarkistus. SQLite- ja Python-esimerkit testaa yhteinen testaaja
# (ks. ../Makefile); tämä tiedosto ajetaan sen jälkeen.
#
#   make            ajaa kaiken
#   make paivita    kirjoittaa palvelinesimerkkien odotetut tulosteet

.PHONY: kaikki palvelimet java paivita siivoa

kaikki: palvelimet java

palvelimet:
	bash palvelimet/aja.sh

# JDBC-ote käännetään, jotta kirjassa näkyvä Java-koodi on kelvollista.
java:
	@mkdir -p build/java
	@javac -Xlint:all -Werror -d build/java java/TuoteDao.java \
	    > build/java.loki 2>&1 || { cat build/java.loki; exit 1; }
	@echo "OK: Java-otteet kääntyvät"

paivita:
	PAIVITA=1 bash palvelimet/aja.sh

siivoa:
	rm -rf build
