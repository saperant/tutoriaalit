# Korkean tason mallinnus (SystemC/TLM)

Tiivis suomenkielinen tutoriaali laitteiston toiminnallisesta ja
ajoitetusta mallintamisesta C++:lla ennen RTL-toteutusta: SystemC:n
moduulit, prosessit ja simulaatioydin, bittitarkat tietotyypit, TLM-2.0:n
transaktiot ja ajoitustyylit, virtuaaliprototyyppi, jossa RISC-V-ISS
ajaa ohjelmaa, sekä mallin ja RTL:n vastaavuuden tarkistus
Verilatorilla. Valmis dokumentti:
[hlm-mallinnus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/hlm-mallinnus.pdf),
pikaopas
[hlm-mallinnus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/hlm-mallinnus-pikaopas.pdf).

## Sisältö

1. Johdanto – abstraktiotasot, virtuaaliprototyypit, työkalut
2. Ensimmäinen malli – moduuli, portit, signaalit, kello, elaborointi
3. Prosessit ja tapahtumat – `SC_METHOD`, `SC_THREAD`, ilmoitukset,
   aikaraja, dynaaminen herkkyys
4. Simulaatioydin, delta-syklit ja aika – päivityssemantiikka,
   aikatarkkuus, tavalliset virheet
5. Kanavat ja rajapinnat – oma FIFO-kanava, vastapaine, portit ja
   exportit
6. Bittitarkat tietotyypit – `sc_int`, `sc_lv`, `sc_fixed`, FIR-suotimen
   bittileveydet
7. TLM-2.0:n perusteet – generic payload, `b_transport`, ajan
   annotointi, vastauksen tilat
8. Väylä ja oheislaitteet – osoitekartta, dekoodaus, rekisterit,
   debug-liikenne
9. Ajallinen irrottaminen ja DMI – kvantti, tarkkuuden hinta, suora
   muistiväylä
10. AT-mallinnus – neljä vaihetta, PEQ, muistinhallinta, liukuhihna
11. Virtuaaliprototyyppi – RV32I-osajoukon ISS, ohjelma, lataaja,
    tilastot
12. Mallin ja RTL:n vastaavuus – Verilator ja SystemC, vertailija,
    transaktorit
13. Lopuksi – nyrkkisäännöt, vianetsintä, työnkulku, lähteet

## Rakentaminen

```text
make testaa   # kääntää ja ajaa esimerkit ja vertaa tulosteet
make pdf      # rakentaa hlm-mallinnus.pdf:n ja pikaoppaan
```

Esimerkit tarvitsevat GCC 14:n (`g++-14`), SystemC 2.3:n
(`libsystemc-dev`, joka sisältää TLM-2.0:n), `pkg-config`in, Verilator
5:n ja ShellCheckin. SystemC-ohjelmat käännetään valitsimella
`-std=c++17`, koska Ubuntun SystemC-kirjasto on käännetty sillä.
Jokainen esimerkki on hakemisto `esimerkit/NN-nimi/`; sen `.cpp`-tiedostot
käännetään yhdeksi ohjelmaksi, tai hakemiston `aja.sh` rakentaa ja ajaa
esimerkin itse. `esimerkit/testaa.sh` vertaa tulosteen tiedostoon
`odotettu`. Yhteiset TLM-mallit ovat hakemistossa `esimerkit/mallit/`.
Kehityskontti on hakemistossa `.devcontainer/hlm-mallinnus`.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.
