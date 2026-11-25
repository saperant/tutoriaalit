# Palvelintietokantojen esimerkit (PostgreSQL ja MariaDB), Java-otteiden
# käännöstarkistus ja tulosteista tuotettujen kaavioiden tarkistus.
# SQLite- ja Python-esimerkit testaa yhteinen testaaja (ks. ../Makefile);
# tämä tiedosto ajetaan sen jälkeen.
#
#   make            ajaa kaiken
#   make paivita    kirjoittaa palvelinesimerkkien odotetut tulosteet ja
#                   tulosteista tuotetut kaaviot

.PHONY: kaikki palvelimet java kaaviot paivita siivoa

kaikki: palvelimet java kaaviot

palvelimet:
	bash palvelimet/aja.sh

# JDBC-ote käännetään, jotta kirjassa näkyvä Java-koodi on kelvollista.
java:
	@mkdir -p build/java
	@javac -Xlint:all -Werror -d build/java java/TuoteDao.java \
	    > build/java.loki 2>&1 || { cat build/java.loki; exit 1; }
	@echo "OK: Java-otteet kääntyvät"

# Kyselysuunnitelman kaavio (../kaaviot) tuotetaan esimerkin testatusta
# tulosteesta; tarkistetaan, että se vastaa tulostetta.
kaaviot:
	@mkdir -p build
	@ruff check -q ../kaaviot/tee.py
	@mypy --strict ../kaaviot/tee.py > build/kaaviot.loki 2>&1 \
	    || { cat build/kaaviot.loki; exit 1; }
	@python3 ../kaaviot/tee.py

paivita:
	PAIVITA=1 bash palvelimet/aja.sh
	python3 ../kaaviot/tee.py kirjoita

siivoa:
	rm -rf build
