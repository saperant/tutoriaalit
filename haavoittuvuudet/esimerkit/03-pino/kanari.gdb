# Pinokanari: kehyksen tarkistusarvo ennen ja jälkeen ylivuodon.
# @alku kanari
break lue_rivi
run < pitka.txt
up
python
def kanari() -> int:
    arvo = gdb.parse_and_eval("*(unsigned long *)($rbp - 8)")
    return int(arvo)
alkuperainen = kanari()
print(f"> kanarin alin tavu: {alkuperainen & 0xff:#04x}")
end
down
finish
python
print(f"> kanari ennallaan: {kanari() == alkuperainen}")
print(f"> kanarin paikalla nyt: {kanari().to_bytes(8, 'little')!r}")
end
continue
# @loppu kanari
