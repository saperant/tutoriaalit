# Testit ja tuotanto-ohjelma samoista lähteistä. Testit linkitetään
# valekelloa ja malloc-käärettä vasten, tuotanto oikeaa kelloa vasten.

CFLAGS ?= -O0 -g
PAKOLLISET := -std=c17 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Werror \
              -Ilahde -I.
LDLIBS := -lm

# @alku testit
YHTEISET := raportti.c lahde/tilasto.c

testit: testit.c testi.c kello_vale.c $(YHTEISET)
	$(CC) $(PAKOLLISET) $(CFLAGS) $^ -Wl,--wrap=malloc $(LDLIBS) -o $@

raportti: raportti_main.c kello.c $(YHTEISET)
	$(CC) $(PAKOLLISET) $(CFLAGS) $^ $(LDLIBS) -o $@

.PHONY: testaa
testaa: testit
	@./testit
# @loppu testit
