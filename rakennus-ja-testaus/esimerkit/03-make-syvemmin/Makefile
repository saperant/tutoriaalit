# Tilasto-ohjelma: erillinen käännöshakemisto, mallisääntö ja
# kääntäjän tuottamat automaattiset riippuvuudet.

# @alku muuttujat
LAHDE    := lahde
RAKENNUS := build
OHJELMA  := $(RAKENNUS)/tilasto

LAHTEET  := $(wildcard $(LAHDE)/*.c)
OBJEKTIT := $(LAHTEET:$(LAHDE)/%.c=$(RAKENNUS)/%.o)

# Pakolliset liput omassa muuttujassaan: käyttäjän CFLAGS (esim.
# make CFLAGS=-O0) vaihtaa optimoinnin mutta ei poista varoituksia.
PAKOLLISET := -std=c17 -Wall -Wextra -Werror
CFLAGS     ?= -O2
CPPFLAGS   += -MMD -MP
LDLIBS     := -lm

# Tiivis tuloste; make V=1 näyttää komennot kokonaan.
Q := $(if $(V),,@)
# @loppu muuttujat

# @alku saannot
$(OHJELMA): $(OBJEKTIT)
	@echo "  LD      $@"
	$(Q)$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $@

# Mallisääntö: mikä tahansa build/X.o tehdään tiedostosta lahde/X.c.
# Pystyviivan jälkeinen hakemisto on järjestysriippuvuus: sen on oltava
# olemassa, mutta sen aikaleima ei käynnistä uudelleenkäännöstä.
$(RAKENNUS)/%.o: $(LAHDE)/%.c | $(RAKENNUS)
	@echo "  CC      $@ $(CFLAGS)"
	$(Q)$(CC) $(CPPFLAGS) $(PAKOLLISET) $(CFLAGS) -c $< -o $@

$(RAKENNUS):
	$(Q)mkdir -p $@

# Kääntäjän kirjoittamat .d-tiedostot: mitkä otsakkeet kukin .o lukee.
-include $(OBJEKTIT:.o=.d)
# @loppu saannot

.PHONY: testaa siivoa

testaa: $(OHJELMA)
	$(OHJELMA) < $(LAHDE)/mittaukset.txt

siivoa:
	rm -rf $(RAKENNUS)
