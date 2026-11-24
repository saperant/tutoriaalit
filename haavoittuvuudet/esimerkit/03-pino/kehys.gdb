# Pinokehyksen asettelu: missä puskuri ja tallennettu paluuosoite ovat.
# @alku kehys
break lue_rivi
run < pitka.txt
up
python
puskuri = int(gdb.parse_and_eval("(long)&tunnus"))
paluu = int(gdb.parse_and_eval("(long)$rbp")) + 8
print(f"> puskurin koko: {gdb.parse_and_eval('sizeof tunnus')} tavua")
print(f"> puskurin alusta paluuosoitteeseen: {paluu - puskuri} tavua")
end
continue
python
rsp = int(gdb.parse_and_eval("(long)$rsp"))
paluu = gdb.selected_inferior().read_memory(rsp, 8).tobytes()
kasky = gdb.execute("x/i $pc", to_string=True).split(":")[-1].strip()
print(f"> pysähtyi käskyyn: {kasky}")
print(f"> paluuosoite pinossa: {paluu!r}")
end
# @loppu kehys
