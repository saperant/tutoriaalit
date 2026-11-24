# Vahtipiste: kuka muuttaa globaalia muuttujaa.
# @alku vahti
break main
run > ohjelma.txt
watch *(long *)&myynti_yhteensa
commands
    silent
    python print(f"> {gdb.selected_frame().name()}: myynti_yhteensa = " \
        f"{int(gdb.parse_and_eval('*(long *)&myynti_yhteensa'))}")
    continue
end
continue
# @loppu vahti
