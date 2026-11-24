# Rakentaa ja testaa kaikki tutoriaalit.
# Sivusto kokoaa muiden hakemistojen PDF:t ja esimerkit, joten se
# käsitellään viimeisenä.
TUTORIAALIT := $(filter-out sivusto,$(patsubst %/Makefile,%,$(wildcard */Makefile))) sivusto

.PHONY: kaikki testaa pdf
kaikki testaa pdf:
	@for t in $(TUTORIAALIT); do $(MAKE) -C $$t $@ || exit 1; done
