# Miten tietokone laskee

Tiivis suomenkielinen tutoriaali lukujen esityksestä ja aritmetiikasta
ohjelmoijan näkökulmasta: kokonaisluvut ja ylivuoto, bittioperaatiot,
jakolasku, IEEE 754 -liukuluvut ja virheen kertyminen, koneoppimisen
lukumuodot (bfloat16, FP8, int8) sekä matriisit ja tensorit muistissa.
Valmis dokumentti: [tietokonearitmetiikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietokonearitmetiikka.pdf),
pikaopas: [tietokonearitmetiikka-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietokonearitmetiikka-pikaopas.pdf).

## Sisältö

1. Johdanto – bitit, tavut ja tavujärjestys, työkalut
2. Kokonaisluvut bitteinä – kahden komplementti, etumerkki, laajennus
3. Ylivuoto ja tarkistettu aritmetiikka – `ckd_add`, kiertyvät laskurit
4. Bittioperaatiot – liput, kentät, siirrot, `<stdbit.h>`
5. Jakolasku ja kääntäjän muunnokset – katkaisu vs. lattia
6. Liukuluvut – kentät, ulp, erikoisarvot, vertailu
7. Pyöristys ja virheen kertyminen – Kahan, Welford, FMA, `-ffast-math`
8. Koneoppimisen lukumuodot – binary16, bfloat16, FP8, int8
9. Matriisit ja tensorit muistissa – järjestys, askeleet, näkymät
10. Matriisitulo ja BLAS – silmukkajärjestys ja lohkominen
11. Lopuksi – nyrkkisäännöt, mallit ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on 29 C-ohjelmaa ja 13 Python-ohjelmaa.
Testaaja kääntää C-esimerkit GCC 14:llä ja Clang 20:llä (C23,
varoitukset virheinä, AddressSanitizer ja UndefinedBehaviorSanitizer)
ja tarkistaa Python-esimerkit ruffilla ja mypyllä (`--strict`).
Optimoinnista riippuvat kokeet ajetaan esimerkkien Makefilellä:

```text
make -C esimerkit nopea    # -ffast-math-valitsimen vaikutus
make -C esimerkit mittaa   # välimuistikokeet -O2:lla
```

## Rakentaminen

```text
make testaa    # rakenne, esimerkit ja Makefilen kokeet
make pdf       # tutoriaali ja pikaopas
```

Lisenssi: CC BY-SA 4.0.
