# Sulautettujen järjestelmien tietoturva: esimerkit.
#
#   make          rakentaa käynnistysketjun Cortex-M3:lle ja ajaa sen
#                 skenaariot QEMU:ssa (ks. laite/Makefile)
#   make siivoa   poistaa käännöstuotteet
#
# Isäntäkoneen C- ja Python-esimerkit ajetaan tutoriaalin juuresta:
#   make -C .. testaa

.PHONY: kaikki siivoa
kaikki:
	$(MAKE) -C laite

siivoa:
	$(MAKE) -C laite siivoa
