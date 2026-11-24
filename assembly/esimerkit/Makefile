# Assembly-esimerkit x86-64:lle ja RISC-V:lle.
#
#   make           kokoaa, ajaa ja tarkistaa kaikki esimerkit
#   make naytteet  kääntää C-rakenteiden näytteet uudelleen (.s-tiedostot)
#   make siivoa    poistaa build/-hakemiston
#
# x86-64-ohjelmat ajetaan suoraan, RISC-V-ohjelmat QEMU:n käyttäjätilan
# emulaattorilla (qemu-riscv64). Esimerkkien rakenne ja tarkistus:
# ks. testaa.sh.

.PHONY: kaikki naytteet siivoa

kaikki:
	./testaa.sh

naytteet:
	./testaa.sh --naytteet

siivoa:
	rm -rf build
