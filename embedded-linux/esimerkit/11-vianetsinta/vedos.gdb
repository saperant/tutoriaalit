# Ydinvedoksen avaus isännällä:
#   gdb-multiarch -q -batch -nx -x vedos.gdb build/anturi build/core.anturi
set pagination off
set confirm off
backtrace
print erotin
up
print numero
print (char *)rivi
