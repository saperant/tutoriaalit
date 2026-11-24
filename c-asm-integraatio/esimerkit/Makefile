# C ja assembly yhteen: esimerkit x86-64:lle ja RISC-V:lle.
#
#   make           kääntää, ajaa ja tarkistaa kaikki esimerkit
#   make siivoa    poistaa build/-hakemiston
#
# x86-64-ohjelmat ajetaan suoraan, RISC-V-ohjelmat QEMU:n käyttäjätilan
# emulaattorilla (qemu-riscv64). Esimerkkien rakenne: ks. testaa.sh.

.PHONY: kaikki siivoa

kaikki:
	./testaa.sh

siivoa:
	rm -rf build
