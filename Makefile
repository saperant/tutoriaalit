# Rakentaa ja testaa kaikki tutoriaalit.
# Sivusto kokoaa muiden hakemistojen PDF:t ja esimerkit, joten se
# käsitellään viimeisenä.
TUTORIAALIT := $(filter-out sivusto,$(patsubst %/Makefile,%,$(wildcard */Makefile))) sivusto

.PHONY: kaikki testaa pdf
# Kaikki tutoriaalit käsitellään, vaikka jokin epäonnistuisi, ja lopuksi
# luetellaan epäonnistuneet. Näin yksi CI-ajo näyttää kaikki virheet.
kaikki testaa pdf:
	@virheet=""; \
	for t in $(TUTORIAALIT); do \
	  $(MAKE) -C $$t $@ || virheet="$$virheet $$t"; \
	done; \
	if [ -n "$$virheet" ]; then echo "VIRHE ($@):$$virheet"; exit 1; fi
