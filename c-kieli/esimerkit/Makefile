# C-kielen tutoriaalin esimerkit.
#
#   make                    kääntää kaikki esimerkit hakemistoon bin/
#   make 01-hei             kääntää yhden esimerkin
#   make aja-09-rivit       kääntää ja ajaa esimerkin; syöte ja argumentit
#                           luetaan tiedostoista .syote ja .argumentit
#   make virhe-02-etumerkki näyttää .ei-kaanny-esimerkin käännösvirheen
#                           (varoitukset virheinä, kuten testeissä)
#   make siivoa             poistaa käännetyt ohjelmat
#
# Ohjelmat käännetään AddressSanitizerin ja UndefinedBehaviorSanitizerin
# kanssa, kuten tutoriaalin testeissä. .ei-kaanny-esimerkit käännetään
# korjattuina (-DKORJATTU).

CC     := $(shell command -v gcc-14 >/dev/null 2>&1 && echo gcc-14 || echo gcc)
CFLAGS := -std=c23 -Wall -Wextra -Wpedantic -g \
          -fsanitize=address,undefined -fno-sanitize-recover=all
LDLIBS := -lm

TAVALLISET := $(basename $(filter-out %.ei-kaanny.c %.kaatuu.c,$(wildcard *.c)))
KAATUVAT   := $(patsubst %.kaatuu.c,%,$(wildcard *.kaatuu.c))
KORJATUT   := $(patsubst %.ei-kaanny.c,%,$(wildcard *.ei-kaanny.c))
HAKEMISTOT := $(sort $(patsubst %/,%,$(dir $(wildcard */*.c))))
OHJELMAT   := $(sort $(TAVALLISET) $(KAATUVAT) $(KORJATUT) $(HAKEMISTOT))

.PHONY: kaikki siivoa $(OHJELMAT)

kaikki: $(addprefix bin/,$(OHJELMAT))

$(OHJELMAT): %: bin/%

bin:
	mkdir -p bin

bin/%: %.c | bin
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

bin/%: %.kaatuu.c | bin
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

bin/%: %.ei-kaanny.c | bin
	$(CC) $(CFLAGS) -DKORJATTU $< -o $@ $(LDLIBS)

define HAKEMISTO
bin/$(1): $(wildcard $(1)/*.c $(1)/*.h) | bin
	$$(CC) $$(CFLAGS) $(wildcard $(1)/*.c) -o $$@ $$(LDLIBS)
endef
$(foreach h,$(HAKEMISTOT),$(eval $(call HAKEMISTO,$(h))))

aja-%: bin/%
	./bin/$* $(if $(wildcard $*.argumentit),$$(cat $*.argumentit)) \
	    < $(if $(wildcard $*.syote),$*.syote,/dev/null)

virhe-%:
	-$(CC) $(CFLAGS) -Werror -fsyntax-only $*.ei-kaanny.c

siivoa:
	rm -rf bin
