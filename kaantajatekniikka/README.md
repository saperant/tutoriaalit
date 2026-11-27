# Kääntäjätekniikka

Suomenkielinen tutoriaali kääntäjän rakentamisesta. Tutoriaalissa
kirjoitetaan C++:lla kokonainen kääntäjä pienelle Kide-kielelle:
selaaja, rekursiivisesti etenevä jäsennin ja Prattin
lausekejäsennin, abstrakti syntaksipuu, semanttinen analyysi,
viitetulkki, kolmiosoitteinen välikieli peruslohkoineen,
elävyysanalyysi ja paikalliset optimoinnit, SSA-muoto ja sen
optimoinnit (harva ehdollinen vakioiden eteneminen, globaali
arvonumerointi, kuolleen koodin poisto) sekä SSA-muodosta poistuminen,
koodingenerointi RISC-V:lle ja rekisterien varaus lineaarisella
pyyhkäisyllä. Käännetyt ohjelmat
ajetaan QEMU-emulaattorissa, ja kääntäjä testataan kultaisilla
tulosteilla, virheohjelmilla, passien yksikkötesteillä ja
differentiaalitestauksella satunnaisohjelmia vastaan. Esitietoina ovat taidot *Algoritmit*,
*Assembly* ja *Funktionaalinen ohjelmointi*.
Valmis dokumentti: [kaantajatekniikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kaantajatekniikka.pdf),
pikaopas: [kaantajatekniikka-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kaantajatekniikka-pikaopas.pdf).

## Sisältö

1. Johdanto – kääntäjän vaiheet, Kide-kieli, työkalut, ensimmäinen
   käännös
2. Kieli ja sen merkitys – kielioppi, tyypit, määritelty aritmetiikka
3. Selaus – tokenit, tilakone, pisin osuma, luvut ja ylivuoto
4. Abstrakti syntaksipuu – `std::variant`, vierailijat, S-lausekkeet
5. Jäsentäminen – rekursiivinen eteneminen ja Prattin menetelmä
6. Virheilmoitukset ja toipuminen – sijainnit, paniikkitila,
   seurannaisvirheet
7. Semanttinen analyysi – symbolitaulu, näkyvyysalueet, tyypit,
   paluupolut
8. Tulkki viitetoteutuksena – kehykset, oikosulku, rajat
9. Välikieli – kolmiosoitekoodi, peruslohkot, ohjausvuograafi,
   hyppykoodi
10. Datavuoanalyysi – elävyys, kiintopiste, muut analyysit
11. Optimoinnit – laskostus, arvonumerointi, kuollut koodi,
    ohjausvuo, kopiot
12. SSA-muoto – dominanssi, dominanssiraja, phi-funktiot,
    uudelleennimeäminen
13. Optimointi SSA-muodossa – SSA-tarkistin, passien testit, harva
    ehdollinen vakioiden eteneminen, globaali arvonumerointi, kuollut
    koodi merkitsemällä
14. SSA-muodosta pois – phien purku, kadonnut kopio, vaihto, kopioiden
    sulauttaminen, `-O1` ja `-O2` mitattuna
15. Koodingenerointi RISC-V:lle – kutsukonventio, pinokehys,
    käskyjen valinta
16. Rekisterien varaus – elinvälit, lineaarinen pyyhkäisy,
    graafinväritys
17. Kääntäjän testaus – kultaiset tulosteet, differentiaalitestaus,
    testien teho
18. Oikeat kääntäjät – GCC ja LLVM, `-O0` ja `-O2`
19. Lopuksi – nyrkkisäännöt, jatkotaidot ja lähteet

## Rakentaminen

```text
make testaa   # rakentaa kääntäjän ja ajaa kaikki testit (QEMU)
make pdf      # rakentaa kaantajatekniikka.pdf:n ja pikaoppaan
make kuvat    # piirtää mittauskuvan uudelleen (Matplotlib)
```

Esimerkit tarvitsevat GCC 14:n, Clang 20:n, RISC-V-ristikääntäjän
(`gcc-riscv64-linux-gnu`, `libc6-dev-riscv64-cross`), QEMU:n
käyttäjätilan emulaattorin (`qemu-user`) ja Python 3:n. Kehityskontti
on hakemistossa `.devcontainer/kaantajatekniikka/`.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
