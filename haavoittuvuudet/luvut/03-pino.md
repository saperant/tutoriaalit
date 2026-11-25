# Pinon ylivuoto

Pinossa ovat funktion paikalliset muuttujat ja kutsujen hallintatieto:
tallennettu kehysosoitin ja *paluuosoite*, johon `ret`-käsky hyppää
funktion lopussa (*Takaisinmallinnus*, luku 2). Kun paikallinen puskuri
vuotaa yli, kirjoitus jatkuu kohti näitä arvoja. Siksi pinon ylivuoto
on ollut vakavimpia C-virheitä: se ei vain korruptoi dataa, vaan voi
muuttaa sen, minne ohjelma jatkaa. Tämä luku näyttää, miltä ylivuoto
näyttää sanitoijalle, debuggerille ja pinokanarille.

## Haavoittuva rajapinta

Kirjautumistunnuksen lukija kopioi syötettä puskuriin, jonka kokoa se
ei tiedä:

```{.c tiedosto="esimerkit/03-pino/tunnus.c" osa="lue"}
```

`lue_rivi` on käytännössä `gets`: koska koko ei kulje rajapinnassa,
funktio ei voi pysähtyä ajoissa. Virhe ei ole funktion sisällä vaan sen
allekirjoituksessa. ASan pysäyttää ensimmäisen kirjoituksen puskurin
ulkopuolelle ja nimeää muuttujan:

```{.tuloste tiedosto="esimerkit/03-pino/odotettu" osa="t1"}
```

ASan ympäröi jokaisen pinomuuttujan *punaisilla vyöhykkeillä*
(*redzone*), joihin kirjoittaminen on virhe. Siksi se huomaa jo
yhden tavun ylityksen, kun taas ilman sanitoijaa virhe näkyy vasta,
jos jokin tärkeä arvo korruptoituu.

## Pinokehyksen asettelu

Ilman sanitoijaa ja ilman pinokanaria ohjelma ei huomaa ylivuotoa
lainkaan. gdb:llä voi katsoa, mitä tapahtuu. Ensin skripti laskee, kuinka
kaukana tallennettu paluuosoite on puskurin alusta, ja jatkaa sitten,
kunnes ohjelma kaatuu:

```{.text tiedosto="esimerkit/03-pino/kehys.gdb" osa="kehys"}
```

```{.bash tiedosto="esimerkit/03-pino/aja.sh" osa="ilman"}
```

```{.tuloste tiedosto="esimerkit/03-pino/odotettu" osa="t3"}
```

Puskuri on 16 tavua, ja sen jälkeen on 8 tavun tallennettu
kehysosoitin; 24 tavun jälkeen alkaa paluuosoite.

```{.dot otsikko="Funktion `tarkista` kehys. Kopiointi etenee puskurin alusta kohti suurempia osoitteita, joten ylivuoto osuu siihen, mikä on puskurin yläpuolella. Ilman kanaria tallennettu `rbp` on 16 ja paluuosoite 24 tavun päässä puskurin alusta."}
digraph {
  node [shape=plain, style=""];
  a [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="right"><font point-size="8">suuret osoitteet</font></td><td width="130">kutsujan kehys</td><td border="0" align="left"><font point-size="8"> </font></td></tr>
    <tr><td border="0" align="right"><font point-size="8">rbp+8</font></td><td bgcolor="#F6D5D5" width="130">paluuosoite</td><td border="0" align="left"><font point-size="8">ret hyppää tähän osoitteeseen</font></td></tr>
    <tr><td border="0" align="right"><font point-size="8">rbp</font></td><td bgcolor="#F6D5D5" width="130">tallennettu rbp</td><td border="0" align="left"><font point-size="8"> </font></td></tr>
    <tr><td border="0" align="right"><font point-size="8">rbp-8</font></td><td style="dashed" width="130">kanari</td><td border="0" align="left"><font point-size="8">vain kanarikäännöksessä: tarkistetaan ennen ret-käskyä</font></td></tr>
    <tr><td border="0" align="right"><font point-size="8"> </font></td><td bgcolor="#EEF1F6" width="130">tunnus[16]</td><td border="0" align="left"><font point-size="8">kopiointi alkaa tästä ja etenee ylöspäin</font></td></tr>
    <tr><td border="0" align="right"><font point-size="8">pienet osoitteet</font></td><td border="0" width="130"> </td><td border="0" align="left"><font point-size="8"> </font></td></tr>
  </table>>];
}
```

Syötteen 40 A-kirjainta ylikirjoittivat sen, ja `ret` yritti hypätä
osoitteeseen `0x4141414141414141`. Se ei ole kelvollinen
x86-64-osoite, joten prosessori kieltäytyi ja ohjelma sai SIGSEGV:n
juuri `ret`-käskyssä.

Tämä on kaatumisen *luokittelu*, ei hyökkäys: kun kaatumiskohta on
`ret` ja paluuosoitteen paikalla on syötteen dataa, virhe antaa
syötteen antajalle vallan ohjausvuohon. Se on vakavin luokka, ja
korjaus kiirehtii (luku 9). Asettelu vaihtelee kääntäjän, optimointien
ja suojausten mukaan; 24 tavua koskee tätä käännöstä.

| Kaatumiskohta | Mitä se kertoo |
|---------------|----------------|
| `ret`, paluuosoitteessa syötettä | ohjausvuo syötteen vallassa |
| luku tai kirjoitus syötteen kaltaisesta osoitteesta | mielivaltainen luku tai kirjoitus |
| `__stack_chk_fail`, `abort` | suojaus havaitsi ylivuodon |
| nollaosoitin | yleensä palvelunesto |

## Pinokanari

*Pinokanari* (*stack canary*, *stack protector*) on satunnainen arvo,
jonka kääntäjä kirjoittaa funktion alussa paikallisten puskurien ja
paluuosoitteen väliin. Funktion lopussa arvo tarkistetaan ennen
`ret`-käskyä. Jos se on muuttunut, ohjelma lopetetaan:

```{.bash tiedosto="esimerkit/03-pino/aja.sh" osa="kanari"}
```

```{.text tiedosto="esimerkit/03-pino/kanari.gdb" osa="kanari"}
```

```{.tuloste tiedosto="esimerkit/03-pino/odotettu" osa="t2"}
```

Kanari on kehyksessä kohdassa `rbp-8` (GCC tallentaa sen sinne
säikeen tietolohkosta `fs:0x28`). Sen alin tavu on aina nolla, jotta
merkkijonofunktio ei voi kopioida kanaria sellaisenaan eteenpäin: nolla
päättää kopioinnin. Ylivuoto korvasi kanarin A-kirjaimilla, ja
funktion lopun tarkistus kutsui `__stack_chk_fail`-funktiota, joka
tulosti viestin ja lopetti ohjelman SIGABRT:lla. Kaatuminen on
hallittu: paluuosoitteeseen ei koskaan hypätty.

GCC:n vaihtoehdot:

| Valitsin | Suojattavat funktiot |
|----------|----------------------|
| `-fstack-protector` | funktiot, joissa on vähintään 8 tavun merkkitaulukko |
| `-fstack-protector-strong` | kaikki taulukot ja osoitteen saavat muuttujat |
| `-fstack-protector-all` | kaikki funktiot |

Ubuntu ja useimmat jakelut kääntävät oletuksena valitsimella
`-fstack-protector-strong`. Kanari ei suojaa kaikelta: se ei huomaa
kirjoitusta, joka ohittaa kanarin (esimerkiksi taulukon indeksi, joka
osuu suoraan paluuosoitteeseen), eikä ylivuotoa saman kehyksen muihin
muuttujiin. Se havaitsee vain jatkuvan ylivuodon, ja vasta funktion
lopussa.

## Korjaus

Korjaus on rajapinnassa: koko kulkee osoittimen mukana, ja ylipitkä
rivi hylätään.

```{.c tiedosto="esimerkit/03-pino/tunnus.c" osa="korjattu"}
```

```{.tuloste tiedosto="esimerkit/03-pino/odotettu" osa="t4"}
```

## Käytännössä

- **Korjaa rajapinta, älä yksittäistä kutsua.** Jos funktio ottaa
  vastaan osoittimen ilman kokoa, jokainen kutsupaikka on riski.
- **Luokittele kaatuminen kohdan mukaan.** Kaatuminen `ret`-käskyyn
  syötteen kaltaisella osoitteella on aina vakava, vaikka se näyttäisi
  pelkältä kaatumiselta.
- **Pidä pinokanari päällä** (`-fstack-protector-strong`), mutta älä
  pidä sitä korjauksena: se muuttaa ylivuodon hallituksi kaatumiseksi,
  joka on edelleen palvelunesto.
- **Testaa sanitoijilla.** Ilman ASania yhden tai muutaman tavun
  ylivuoto voi jäädä täysin huomaamatta.

## Itsearviointi

- Osaat selittää pinokehyksen rakenteen ja sen, miksi puskurin ylivuoto
  voi ylikirjoittaa paluuosoitteen.
- Osaat tutkia gdb:llä puskurin ja paluuosoitteen etäisyyden ja
  luokitella kaatumisen sen kohdan perusteella.
- Osaat selittää pinokanarin toiminnan, sen alimman nollatavun
  merkityksen ja kanarin rajoitukset.
- Osaat korjata rajapinnan, joka ei kerro puskurin kokoa.
