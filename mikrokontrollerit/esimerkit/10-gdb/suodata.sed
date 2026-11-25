# Koodiosoitteet riippuvat kääntäjäversiosta: korvataan ne.
s/ at 0x[0-9a-f]+: / at ...: /
s/0x[0-9a-f]{8} in /... in /
# Lähdekoodirivin numeron jälkeinen sarkain välilyönneiksi.
s/\t/  /
# Lopussa gdb irrottautuu QEMU:sta; ilmoitus riippuu siitä, kumpi ehtii
# ensin sulkea putken, joten se jätetään pois.
/^\[Inferior 1 /d
/^Remote communication error/d
