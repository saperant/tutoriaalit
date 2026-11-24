# Rakentaa ja testaa kaikki tutoriaalit.
# Sivusto kokoaa muiden hakemistojen PDF:t ja esimerkit, joten se
# käsitellään viimeisenä.
PAKETIT := $(filter-out sivusto,$(patsubst %/Makefile,%,$(wildcard */Makefile)))
TUTORIAALIT := $(PAKETIT) sivusto

.PHONY: kaikki testaa pdf $(addprefix pdf/,$(PAKETIT))

# PDF:t ovat toisistaan riippumattomia, joten ne voi rakentaa
# rinnakkain: make -k -j4 pdf.
pdf: $(addprefix pdf/,$(PAKETIT))
	$(MAKE) -C sivusto pdf

$(addprefix pdf/,$(PAKETIT)): pdf/%:
	$(MAKE) -C $* pdf

# Testit ajetaan peräkkäin, koska monet käynnistävät palvelimia ja
# QEMU-koneita. Kaikki tutoriaalit käsitellään, vaikka jokin
# epäonnistuisi, ja lopuksi luetellaan epäonnistuneet.
kaikki testaa:
	@virheet=""; \
	for t in $(TUTORIAALIT); do \
	  $(MAKE) -C $$t $@ || virheet="$$virheet $$t"; \
	done; \
	if [ -n "$$virheet" ]; then echo "VIRHE ($@):$$virheet"; exit 1; fi
