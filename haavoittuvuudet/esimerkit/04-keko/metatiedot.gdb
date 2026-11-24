# Keon lohkon metatiedot: koko-kenttä on heti varauksen edellä.
# @alku metatiedot
break ylivuoto
run ylivuoto
next 4
python
def koko(nimi: str) -> int:
    osoite = int(gdb.parse_and_eval(f"(long){nimi}")) - 8
    tavut = gdb.selected_inferior().read_memory(osoite, 8).tobytes()
    return int.from_bytes(tavut, "little")
print(f"> kentta: koko-kenttä {koko('kentta'):#x}")
print(f"> seuraava: koko-kenttä {koko('seuraava'):#x}")
etaisyys = int(gdb.parse_and_eval("(long)seuraava - (long)kentta"))
print(f"> seuraava alkaa {etaisyys} tavua kentän jälkeen")
end
next
python
arvo = koko("seuraava").to_bytes(8, "little")
print(f"> kopioinnin jälkeen seuraavan koko-kenttä: {arvo!r}")
end
kill
# @loppu metatiedot
