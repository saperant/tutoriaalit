# Paluuarvon muuttaminen: ohjelma hyväksyy minkä tahansa koodin.
# @alku muuta
python
class Paluu(gdb.FinishBreakpoint):
    def stop(self):
        arvo = int(gdb.parse_and_eval("$rax"))
        print(f"> tarkista_koodi palautti {arvo}, asetetaan rax = 1")
        gdb.execute("set $rax = 1")
        return False


class Tarkistus(gdb.Breakpoint):
    def stop(self):
        koodi = gdb.parse_and_eval("(char *)$rdi").string()
        print(f'> tarkista_koodi("{koodi}")')
        Paluu(gdb.newest_frame(), internal=True)
        return False


Tarkistus("tarkista_koodi")
end
run > ohjelma.txt
# @loppu muuta
