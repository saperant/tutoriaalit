# std::stringin ja std::vectorin muistiasettelu libstdc++:ssa. Alkioiden
# kohdalla tulostetaan symboli, johon olion ensimmäinen sana (vptr)
# osoittaa.
# Rivit, jotka alkavat merkillä '>', ovat tarkistettavaa tulostetta.
# @alku asettelu
break kokonaisala
run
up
printf "> sizeof(std::string) = %d\n", sizeof(lyhyt)
printf "> lyhyt: data-osoitin = olio+16: %d\n", \
    *(char **)&lyhyt == (char *)&lyhyt + 16
printf "> lyhyt: pituus (siirtymä 8) = %d\n", *(long *)((char *)&lyhyt + 8)
printf "> pitka: data-osoitin = olio+16: %d\n", \
    *(char **)&pitka == (char *)&pitka + 16
printf "> pitka: pituus %d, kapasiteetti (siirtymä 16) %d\n", \
    *(long *)((char *)&pitka + 8), *(long *)((char *)&pitka + 16)
printf "> sizeof(std::vector) = %d\n", sizeof(muodot)
set $alku = *(char **)&muodot
set $loppu = *(char **)((char *)&muodot + 8)
set $vara = *(char **)((char *)&muodot + 16)
printf "> vector: alkioita %d, kapasiteetti %d\n", \
    ($loppu - $alku) / 8, ($vara - $alku) / 8
pipe info symbol **(void ***)$alku | sed 's/^/> alkio 0: /; s/ of .*//'
pipe info symbol **(void ***)($alku + 8) | sed 's/^/> alkio 1: /; s/ of .*//'
# @loppu asettelu
kill
