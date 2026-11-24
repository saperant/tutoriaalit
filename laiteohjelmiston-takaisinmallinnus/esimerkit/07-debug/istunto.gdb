# gdb ilman symboleita: osoitteet ovat analyysin tuloksia (luvut 4-7).
set pagination off
set confirm off
set width 0
set style enabled off
# @alku yhteys
target remote | ./qemu-gdb.sh ../laite/flash.bin
# @loppu yhteys
# @alku reset
echo --- resetin jälkeen\n
p/x $pc
p/x $sp
x/2wx 0
# @loppu reset
# @alku kelpaa
echo --- käynnistyslataimen tarkistusfunktio 0x54\n
break *0x54
continue
p/x $r0
x/6wx $r0
# Paluuosoite on lr-rekisterissä (Thumb-bitti pois).
tbreak *($lr & ~1)
continue
p $r0
# @loppu kelpaa
# @alku sovellus
echo --- sovelluksen Reset_Handler\n
tbreak *0x10180
continue
p/x $sp
p/x *(unsigned *)0xE000ED08
x/s 0x110b6
# @loppu sovellus
