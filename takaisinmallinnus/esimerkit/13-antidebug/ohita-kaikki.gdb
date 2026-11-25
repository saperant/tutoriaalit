# Koe omalla esimerkkiohjelmalla: debuggeri palauttaa päätösfunktiosta
# debuggeri_havaittu heti nollan, joten tarkistus ei suojaa mitään.
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
