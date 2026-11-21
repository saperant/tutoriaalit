# Rakentaa ja testaa kaikki tutoriaalit.
TUTORIAALIT := $(patsubst %/Makefile,%,$(wildcard */Makefile))

.PHONY: kaikki testaa pdf
kaikki testaa pdf:
	@for t in $(TUTORIAALIT); do $(MAKE) -C $$t $@ || exit 1; done
