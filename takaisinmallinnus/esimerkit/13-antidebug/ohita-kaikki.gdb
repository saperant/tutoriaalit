# Ohittaa koko päätösfunktion: debuggeri_havaittu palauttaa heti 0.
# @alku ohita-kaikki
break debuggeri_havaittu
commands
    silent
    printf "> debuggeri_havaittu ohitetaan: rax = 0, paluu kutsujaan\n"
    return (int) 0
    continue
end
run > ohjelma.txt
# @loppu ohita-kaikki
