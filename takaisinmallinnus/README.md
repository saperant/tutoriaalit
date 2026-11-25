# Takaisinmallinnus

Tiivis suomenkielinen tutoriaali ohjelman toiminnan selvittämisestä
konekielestä, tiedostomuodoista ja ajonaikaisesta käytöksestä
(Linux, x86-64, ELF). Aiheina x86-64-assemblyn lukeminen,
disassemblointi ja dekompilointi, kääntäjän tuottamat rakenteet ja
optimoinnit, C++-ohjelmat, symbolittomat binäärit, dynaaminen analyysi
(gdb, strace, ltrace, `LD_PRELOAD`), tiedostomuotojen ja protokollien
päättely sekä obfuskoinnin purkaminen. Kohteet ovat paketin omia, itse
käännettyjä ohjelmia, ja jokainen analyysi on skripti, joka ajetaan ja
tarkistetaan.

**Vastuulauseke.** Materiaali on tarkoitettu opetukseen, omien
ohjelmien tutkimiseen ja luvalliseen ammattityöhön. Kaikki kohteet
ovat paketin omia ohjelmia. Käytä tekniikoita vain omiin ohjelmiisi
tai kohteisiin, joihin sinulla on lain tai kirjallisen luvan antama
oikeus; toisten ohjelmien kopiosuojausten ja lisenssitarkistusten
kiertämiseen materiaalia ei ole tarkoitettu. Luvussa 1 on
takaisinmallinnuksen lailliset ja eettiset rajat ja luvussa 12
lailliset harjoituskohteet (CTF). Tekijät eivät vastaa materiaalin
väärinkäytöstä.

Valmis dokumentti:
[takaisinmallinnus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/takaisinmallinnus.pdf),
pikaopas
[takaisinmallinnus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/takaisinmallinnus-pikaopas.pdf).

## Sisältö

1. Johdanto – käyttökohteet, laki ja etiikka, työkalut
2. x86-64-assemblyn lukeminen – rekisterit, kutsukonventio, pinokehys
3. Disassemblointi ja dekompilointi – lineaarinen vs. rekursiivinen,
   radare2, ristiviittaukset, Ghidra
4. Kääntäjän tuottamat rakenteet – ehdot, silmukat, hyppytaulut, tietueet
5. Optimoinnit konekielessä – upotus, häntäkutsut, vektorointi, jako
   vakiolla
6. C++-ohjelmien takaisinmallinnus – nimet, vtablet, RTTI, poikkeukset
7. Symbolittomat ohjelmat – `.eh_frame`, `main`, allekirjoitukset
8. Dynaaminen analyysi – gdb, strace, ltrace, `LD_PRELOAD`
9. Tiedostomuodot ja protokollat – heksavedos, entropia, jäsennin
10. Obfuskointi ja sen purkaminen – salatut merkkijonot, litistys,
    debuggerin havaitseminen ja miksi se ei ole suoja
11. Kokonainen analyysi – yhteentoimivuustyö alusta loppuun
12. Lopuksi – muut arkkitehtuurit, nyrkkisäännöt, lailliset
    harjoituskohteet, lähteet

## Rakentaminen

```text
make testaa   # kääntää kohteet, ajaa analyysit ja vertaa tulosteet
make pdf      # rakentaa takaisinmallinnus.pdf:n ja pikaoppaan
```

Esimerkit tarvitsevat GCC 14:n, GNU binutilsin, gdb:n, radare2:n,
stracen, ltracen, Pythonin (`ruff`, `mypy`) ja ShellCheckin.
Jokainen esimerkki on hakemisto `esimerkit/NN-nimi/`, jossa on
kohdeohjelma, analyysiskriptit ja `aja.sh`. `esimerkit/testaa.sh` ajaa
ne ja vertaa tulosteita tiedostoihin `odotettu`. Kehityskontti on
hakemistossa `.devcontainer/takaisinmallinnus`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.
