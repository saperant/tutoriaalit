# Kutsujen jäljitys Pythonilla: argumentit ja paluuarvot sisennettyinä.
# @alku jaljita
python
REKISTERIT = ("$rdi", "$rsi", "$rdx")
syvyys = 0


def arvo(rekisteri):
    """Rekisterin arvo; osoittimelta näyttävät arvot ilman osoitetta."""
    luku = int(gdb.parse_and_eval(rekisteri)) & 0xFFFFFFFFFFFFFFFF
    if luku > 0xFFFFFFFF:
        return "osoitin"
    return str(luku if luku < 2**31 else luku - 2**32)


class Paluu(gdb.FinishBreakpoint):
    def __init__(self, nimi):
        super().__init__(gdb.newest_frame(), internal=True)
        self.nimi = nimi

    def stop(self):
        global syvyys
        syvyys -= 1
        print(f"> {'  ' * syvyys}{self.nimi} -> {arvo('$rax')}")
        return False


class Jaljitin(gdb.Breakpoint):
    def __init__(self, nimi, argumentteja):
        super().__init__(nimi, internal=True)
        self.nimi = nimi
        self.argumentteja = argumentteja

    def stop(self):
        global syvyys
        argumentit = ", ".join(arvo(r) for r in
                               REKISTERIT[:self.argumentteja])
        print(f"> {'  ' * syvyys}{self.nimi}({argumentit})")
        syvyys += 1
        Paluu(self.nimi)
        return False


Jaljitin("laske_hinta", 3)
Jaljitin("alennus", 2)
Jaljitin("tarkista_koodi", 1)
end
run > ohjelma.txt
# @loppu jaljita
