# Synkronointi

GPU suorittaa komentoja putkimaisesti ja limittäin: kun yksi piirto on
fragmenttivaiheessa, seuraavan verteksit ovat jo työn alla, ja
kopiokomento voi alkaa ennen kuin edellinen piirto on kirjoittanut
kaiken. Jonoon lähetetyt komennot *aloitetaan* järjestyksessä, mutta
niiden ei taata *päättyvän* järjestyksessä. OpenGL-ajuri lisää
tarvittavat odotukset itse; Vulkanissa ne ovat sovelluksen vastuulla.

| Väline | Kenen välillä | Esimerkki |
|--------|---------------|-----------|
| putken este (pipeline barrier) | saman jonon komennot | kirjoitus valmiiksi ennen lukua; asettelun vaihto |
| binäärinen semafori | jonolähetykset (GPU–GPU) | swapchain-kuva valmis ennen piirtoa |
| aikajanasemafori | GPU–GPU ja GPU–CPU | kehysten numerointi, eri jonojen tahdistus |
| aita (fence) | GPU → CPU | komentopuskuri vapaa uudelleenkäyttöön |

## Este: suoritus- ja muistiriippuvuus

Este sanoo kaksi asiaa. **Suoritusriippuvuus**: lähdevaiheiden
(`srcStageMask`) on valmistuttava ennen kuin kohdevaiheet
(`dstStageMask`) alkavat. **Muistiriippuvuus**: lähdevaiheiden
kirjoitukset (`srcAccessMask`) on tehtävä näkyviksi kohdevaiheiden
käytölle (`dstAccessMask`). Pelkkä suoritusjärjestys ei riitä, koska
kirjoitus voi olla vielä välimuistissa.

Esimerkki täyttää puskurin ja kopioi sen toiseen, ensin ilman estettä
ja sitten esteen kanssa. Synkronoinnin validointi on päällä:

```{.cpp tiedosto="esimerkit/09-vk-synkronointi.cpp" osa="kopio"}
```

```{.cpp tiedosto="esimerkit/09-vk-synkronointi.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/09-vk-synkronointi.odotettu"}
```

Ilman estettä *tulos on silti oikein*. Lavapipe suorittaa komennot
käytännössä peräkkäin, ja moni oikea laite tekisi samoin, kun data on
pieni. Ohjelma on silti väärin, ja validointikerros huomaa sen:
`SYNC-HAZARD-READ-AFTER-WRITE`. Isommalla datalla, toisella laitteella
tai uudemmalla ajurilla kopio lukisi osittain vanhaa dataa. Tällaiset
virheet ovat Vulkan-ohjelmoinnin vaikeimpia, koska ne eivät näy
testeissä. Siksi synkronoinnin validointi kuuluu jokaiseen
testiajoon.

Este kannattaa kirjoittaa niin tarkaksi kuin mahdollista. Liian
laaja este (`ALL_COMMANDS` → `ALL_COMMANDS`) on aina oikein, mutta se
pysäyttää koko putken ja hukkaa GPU:n rinnakkaisuuden. Liian kapea
este on virhe. Esimerkissä täyttö luokitellaan siirtovaiheeksi:
`ALL_TRANSFER` kattaa kopioinnit ja täytöt eri toteutusten
luokittelusta riippumatta.

## Aikajanasemafori

Aikajanasemaforilla on 64-bittinen kasvava arvo. Lähetys voi odottaa,
että arvo saavuttaa tietyn luvun, ja nostaa sen valmistuttuaan. Myös
CPU voi odottaa ja nostaa arvoa. Esimerkissä GPU odottaa, kunnes CPU
on nostanut arvon ykköseen:

```{.cpp tiedosto="esimerkit/09-vk-synkronointi.cpp" osa="aikajana"}
```

Aikajanasemafori korvaa monessa paikassa aidat ja binääriset
semaforit: jokaisella ruudulla on numero, ja "ruutu n valmis" on
semaforin arvo n. Binäärisiä semaforeja tarvitaan edelleen
swapchainin kanssa.

## Ruutujen limitys

Tyypillinen sovellus pitää kaksi tai kolme ruutua yhtä aikaa työn
alla (frames in flight). Jokaisella ruudulla on omat
komentopuskurinsa ja usein päivittyvät puskurinsa. Ennen kuin CPU
tallentaa ruudun n komennot, se odottaa, että ruutu n − 2 on valmis,
koska sen resursseja käytetään uudelleen. Liian vähän ruutuja jättää
GPU:n odottamaan CPU:ta; liian moni kasvattaa viivettä syötteestä
kuvaan.

## Käytännössä

- **Synkronoinnin validointi testeihin.** Se löytää puuttuvat ja
  väärät esteet, jotka eivät näy tuloksissa.
- **synchronization2** (Vulkan 1.3) on selkeämpi kuin alkuperäinen
  esterajapinta: vaihe ja käyttö kulkevat parina, ja vaiheita on
  tarkemmin.
- **Tarkat esteet, harvoin.** Kokoa saman kohdan esteet yhteen
  kutsuun; jokainen este on mahdollinen putken tyhjennys.
- **Resurssi per limitetty ruutu.** Älä kirjoita CPU:lta puskuriin,
  jota GPU voi vielä lukea; kierrätä puskureita ruutunumeron mukaan.
- **Käytä valmiita ratkaisuja**, kuten renderöintigraafia
  (render graph), joka päättelee esteet resurssien käytöstä. Useimmat
  nykyiset moottorit toimivat niin.

## Itsearviointi

- Osaat selittää suoritus- ja muistiriippuvuuden eron ja kirjoittaa
  esteen, jossa on oikeat vaiheet ja käytöt.
- Osaat käyttää synkronoinnin validointia ja tulkita sen
  ilmoituksen.
- Osaat tahdistaa CPU:n ja GPU:n aidalla ja aikajanasemaforilla.
- Osaat kuvata ruutujen limityksen ja sen, miksi resursseja on
  useampi kopio.
