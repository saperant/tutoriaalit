# Emulointi QEMU:lla

Emulointi ajaa laiteohjelmiston ilman fyysistä laitetta. Se on
takaisinmallinnuksen tehokkain dynaaminen työkalu: ajon voi toistaa,
pysäyttää, tarkastella ja muuttaa vapaasti, eikä laitetta voi rikkoa.
QEMU emuloi koko kortin, Unicorn (luku 9) yksittäisiä funktioita.

## Koko kortin emulointi

QEMU:n `mps2-an385`-kone emuloi Cortex-M3:n ja sen oheislaitteet, joten
LT-100:n flash-kuva ajetaan sellaisenaan. `-icount` tekee ajosta
käsky käskyltä toistettavan, `-semihosting` välittää laitteen
lopetuksen, ja sarjaportti kytketään vakiosyötteeseen ja -tulosteeseen.
Tämän tutoriaalin `qemu`-apufunktio (hakemistossa `yhteinen.sh`)
kokoaa valitsimet. Ajetaan komentosarja ja tallennetaan sarjaliikenne:

```{.bash tiedosto="esimerkit/08-qemu/aja.sh" osa="istunto"}
```

```{.tuloste tiedosto="esimerkit/08-qemu/odotettu" osa="s1"}
```

Laite käy läpi komennot: mittaa, näyttää tilan, kaiuttaa kehyksen ja
siirtää lokin. Tuloste sisältää sekä tekstiä että binääristä
kehysliikennettä, joten se tallennetaan tiedostoon ja tutkitaan
erikseen.

## Binäärisen tulosteen tulkinta

Lokin siirto lähettää kehyksiä, jotka luvussa 2 tunnistettiin
alustavasti ja luvussa 6 varmistettiin `switch`-lauseesta. Kehysten
heksavedos:

```{.bash tiedosto="esimerkit/08-qemu/aja.sh" osa="kehykset"}
```

```{.tuloste tiedosto="esimerkit/08-qemu/odotettu" osa="s2"}
```

Kehykset alkavat ja päättyvät tavuun `0x7e`; `0x7e 0x05` on kaiutettu
kehys, `0x7e 0x10` lokitietue ja `0x7e 0x11` lopetus. Ajamalla laitetta
eri syötteillä kehysprotokollan saa selville kokonaan — tämä on
yhteentoimivuustyön ydin.

## Toistettavuus ja koputus

`-icount`-tilassa sama syöte tuottaa tavulleen saman tulosteen joka
ajolla, mikä tekee analyysista toistettavaa ja testit luotettaviksi:

```{.bash tiedosto="esimerkit/08-qemu/aja.sh" osa="toisto"}
```

```{.tuloste tiedosto="esimerkit/08-qemu/odotettu" osa="s3"}
```

Emuloitua kuvaa voi myös muuttaa ja katsoa, mitä tapahtuu. Jos
sovelluksesta muuttaa yhden tavun, käynnistyslataimen CRC-tarkistus
havaitsee sen ja hylkää sovelluksen:

```{.bash tiedosto="esimerkit/08-qemu/aja.sh" osa="muutos"}
```

```{.tuloste tiedosto="esimerkit/08-qemu/odotettu" osa="s4"}
```

Tämä vahvistaa, että käynnistyslatain tarkistaa koko sovelluksen
tarkisteen ennen käynnistystä — ja samalla, että CRC *ei* estä
tahallista muuttamista, koska hyökkääjä laskee sen uudelleen (luku 10).

## Käytännössä

- **Aja koko kuva QEMU:ssa, kun kone on tuettu.** `mps2`-,
  `lm3s`- ja `stm32`-koneet kattavat monta Cortex-M-laitetta.
  `-icount` takaa toistettavuuden ja `-semihosting` lopetuksen.
- **Tallenna binääriliikenne tiedostoon.** Sekamuotoinen (teksti +
  binääri) sarjaliikenne on helpoin tutkia heksavedoksena jälkikäteen,
  ei suoraan päätteessä.
- **Selvitä protokolla ajamalla.** Eri syötteet paljastavat kehysten
  rajat, tyypit ja tarkisteet. Tämä on nopein tie yhteensopivaan
  työkaluun.
- **Puolustus:** emulointi on myös fuzzauksen ja regressiotestauksen
  alusta omalle laiteohjelmistolle. CRC-tarkistus havaitsee vahingon
  muttei hyökkäystä; aitoustakuu vaatii allekirjoituksen.

## Itsearviointi

- Osaat ajaa Cortex-M-kuvan QEMU:ssa syötteineen ja tallentaa sen
  sarjaliikenteen.
- Osaat tulkita binäärisen sarjaprotokollan kehykset heksavedoksesta.
- Osaat selittää, miksi `-icount` tekee ajosta toistettavan.
- Osaat muuttaa emuloitua kuvaa ja havainnoida käynnistyslataimen
  tarkistuksen vaikutuksen.
