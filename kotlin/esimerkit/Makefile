# Esimerkit, jotka tarvitsevat kääntäjän mukana tulevia kirjastoja
# (kotlinx.coroutines ja kotlin.test). Yksittäiset ohjelmat testaa
# yhteinen testaaja; tämä Makefile kääntää ja ajaa hakemistojen
#
#   12-korutiinit/src  rakenteinen rinnakkaisuus ja Flow
#   13-testit          kirjasto ja sen yksikkötestit
#
# ohjelmat ja vertaa tulosteet .odotettu-tiedostoihin.
#
# Kirjastot löytyvät kääntäjän hakemistosta (kotlinc/lib), joten
# verkkoa ei tarvita.

KOTLINC := $(firstword $(shell command -v kotlinc) /opt/kotlinc/bin/kotlinc)
LIB     := $(realpath $(dir $(realpath $(KOTLINC)))/../lib)
KORUT   := $(LIB)/kotlinx-coroutines-core-jvm.jar
TESTI   := $(LIB)/kotlin-test.jar
JAVA    := java -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8
KOHDE   := rakennus

.PHONY: kaikki korutiinit testit siivoa

kaikki: korutiinit testit

$(KOHDE)/rakenteinen.jar: 12-korutiinit/src/Rakenteinen.kt
	@mkdir -p $(KOHDE)
	$(KOTLINC) -Werror -cp $(KORUT) -include-runtime -d $@ $< 2>&1 \
	    | grep -v '^Picked up' || true
	@test -f $@

$(KOHDE)/virta.jar: 12-korutiinit/src/Virta.kt
	@mkdir -p $(KOHDE)
	$(KOTLINC) -Werror -cp $(KORUT) -include-runtime -d $@ $< 2>&1 \
	    | grep -v '^Picked up' || true
	@test -f $@

$(KOHDE)/testit.jar: $(wildcard 13-testit/src/*.kt 13-testit/testit/*.kt)
	@mkdir -p $(KOHDE)
	$(KOTLINC) -Werror -cp $(TESTI) -include-runtime -d $@ $^ 2>&1 \
	    | grep -v '^Picked up' || true
	@test -f $@

korutiinit: $(KOHDE)/rakenteinen.jar $(KOHDE)/virta.jar
	$(JAVA) -cp $(KOHDE)/rakenteinen.jar:$(KORUT) RakenteinenKt 2>/dev/null \
	    | diff -u 12-korutiinit/rakenteinen.odotettu -
	$(JAVA) -cp $(KOHDE)/virta.jar:$(KORUT) VirtaKt 2>/dev/null \
	    | diff -u 12-korutiinit/virta.odotettu -

testit: $(KOHDE)/testit.jar
	$(JAVA) -cp $(KOHDE)/testit.jar:$(TESTI) \
	    hinnoittelu.HinnoitteluTestiKt 2>/dev/null \
	    | diff -u 13-testit/testit.odotettu -

siivoa:
	rm -rf $(KOHDE)
