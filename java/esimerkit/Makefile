# Esimerkki 10-toimitus on Maven-projekti, jota yhteinen testaaja ei
# käännä. Tämä Makefile
#
#   testit    kääntää projektin, ajaa JUnit-testit (./mvnw test) ja
#             vertaa testiraportin yhteenvetoa tiedostoon
#             10-toimitus.odotettu
#   javadoc   tuottaa dokumentaation ja tarkistaa kommentit
#             (-Xdoclint:all -Werror)
#
# Maven Wrapper (mvnw) lataa Mavenin ja JUnitin ensimmäisellä kerralla
# Maven Central -peilistä (10-toimitus/.mvn), joten verkkoyhteys
# tarvitaan.

SHELL       := /bin/bash
.SHELLFLAGS := -o pipefail -c

RAPORTTI := 10-toimitus/target/surefire-reports/fi.esimerkki.toimitus.ToimitusTest.txt
# JVM:n ilmoitus ympäristömuuttujista ei kuulu tulosteeseen.
HILJAA   := 2>&1 | { grep -v '^Picked up' || true; }

.PHONY: kaikki testit javadoc siivoa

kaikki: testit javadoc

testit:
	cd 10-toimitus && ./mvnw -B -q test $(HILJAA)
	sed -n 's/, Time elapsed.*//; /^Test/p' $(RAPORTTI) \
	    | diff -u 10-toimitus.odotettu -

javadoc:
	javadoc -quiet -Xdoclint:all -Werror \
	    --snippet-path 10-toimitus/src/test/java \
	    -d 10-toimitus/target/javadoc \
	    $$(find 10-toimitus/src/main/java -name '*.java') $(HILJAA)
	@test -f 10-toimitus/target/javadoc/index.html

siivoa:
	rm -rf 10-toimitus/target
