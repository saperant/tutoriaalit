# gdb-istunto: ajetaan komennolla make (ks. Makefile) tai käsin:
#   gdb-multiarch -q -batch -nx -x 11-gdb/istunto.gdb build/11-gdb.elf
set pagination off
set confirm off
set width 0
set style enabled off
set print entry-values no
set filename-display basename
# @alku yhteys
# gdb käynnistää QEMU:n itse ja puhuu sille putken kautta.
target remote | 11-gdb/qemu.sh build/11-gdb.elf
# @loppu yhteys
# @alku alku
echo --- resetin jälkeen\n
info symbol $pc
p/x $sp
x/1wx 0
info symbol *(unsigned *)4
p/x *(unsigned *)0xE000ED00
# @loppu alku
# @alku katko
echo --- katkopiste\n
break keskiarvo
continue
bt
p taulukko[0]@n
# @loppu katko
# @alku ehto
echo --- ehdollinen katkopiste silmukkaan\n
break main.c:18 if i >= 7
continue
p i
p taulukko[i]
continue
p i
p taulukko[i]
info symbol &taulukko[i]
# @loppu ehto
# @alku finish
echo --- funktion loppuun\n
delete
finish
# @loppu finish
# @alku watch
echo --- vahtipiste\n
watch viimeisin
continue
# Lopuksi ajetaan semihosting-lopetukseen asti; gdb lopettaa QEMU:n.
delete
break lopeta
continue
# @loppu watch
