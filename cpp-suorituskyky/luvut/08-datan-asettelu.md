# Datan asettelu

Prosessori lukee muistia 64 tavun välimuistiriveinä, joten nopeus
riippuu siitä, kuinka paljon hyödyllistä dataa kukin rivi sisältää.
Taito *Suorituskyvyn analyysi ja optimointi* mittaa läpikäyntijärjestyksen,
rakenteen täytteen ja AoS/SoA-asettelun C:llä. Tässä luvussa samat
asiat tehdään C++:n välinein: oliot, joiden kokoa kääntäjä kasvattaa,
`std::vector<bool>`, `std::views::zip` ja standardikirjaston säiliöt,
joiden asettelu poikkeaa toisistaan paljon.

## Täyte ja tasaus

Jäsenet sijoitetaan muistiin esittelyjärjestyksessä, ja jokainen
tasataan omaan tasaukseensa. Väärä järjestys jättää aukkoja:

```{.cpp tiedosto="esimerkit/08-asettelu.cpp" osa="tayte"}
```

Sääntö on järjestää jäsenet suurimmasta tasauksesta pienimpään.
`static_assert` koon kanssa on halpa vakuutus, joka hälyttää, kun joku
lisää jäsenen väärään kohtaan. Kääntäjän `-Wpadded` varoittaa jokaisesta
täytteestä, mutta se on liian äänekäs jatkuvaan käyttöön. Kertaluontoiseen
tarkastukseen sopivat se ja työkalu `pahole`, joka näyttää rakenteiden
aukot ohjelman debug-tiedoista.

Tyhjä luokka, kuten vertailija `std::less<int>` tai tilaton
allokaattori, vie jäsenenä tavun ja tasauksen verran tilaa. C++20:n
`[[no_unique_address]]` sallii kääntäjän sijoittaa sen toisen jäsenen
päälle:

```{.cpp tiedosto="esimerkit/08-asettelu.cpp" osa="tyhja"}
```

Tasaus voi myös olla tarkoituksellinen. `alignas(64)` antaa
laskurille oman välimuistirivin, mikä estää usean säikeen laskureita
jakamasta riviä (väärä jakaminen, ks. *Rinnakkaisohjelmointi*).
`std::hardware_destructive_interference_size` kertoo rivin koon
kääntäjän arvion mukaan.

```{.cpp tiedosto="esimerkit/08-asettelu.cpp" osa="tasaus"}
```

```{.cpp tiedosto="esimerkit/08-asettelu.cpp" osa="koot"}
```

## `std::vector<bool>`

`std::vector<bool>` on erikoistettu pakkaamaan arvot biteiksi.
Muistia kuluu kahdeksasosa, mutta alkio ei ole `bool`: `operator[]`
palauttaa välityöolion (engl. proxy), joka viittaa bittiin. Siitä
seuraa yllätyksiä:

```{.cpp tiedosto="esimerkit/08-asettelu.cpp" osa="vektoribool"}
```

```{.tuloste tiedosto="esimerkit/08-asettelu.odotettu"}
```

`auto` päättelee välityöolion tyypin, joten sijoitus muuttaa vektoria.
Lisäksi `&v[0]` ei ole `bool*`, alkioita ei voi antaa funktiolle, joka
odottaa `bool&`, eikä eri bittien kirjoittaminen eri säikeistä ole
turvallista, koska ne jakavat tavun. Jos bittejä ei tarvita,
`std::vector<char>` tai `std::vector<std::uint8_t>` käyttäytyy kuin
tavallinen vektori. Kiinteän kokoiseen joukkoon sopii `std::bitset`.

## AoS ja SoA

Olio-ohjelmoinnin luonteva asettelu on rakenteiden taulukko (engl.
array of structures, AoS): jokainen hiukkanen on olio, ja oliot ovat
vektorissa.

```{.cpp tiedosto="esimerkit/08-soa.cpp" osa="aos"}
```

Kun silmukka päivittää vain yhtä kenttää, jokainen 88 tavun olio
tuodaan välimuistiin, vaikka siitä käytetään 16 tavua. Taulukoiden
rakenne (engl. structure of arrays, SoA) tallentaa kunkin kentän omaan
vektoriinsa. C++23:n `std::views::zip` palauttaa rivikohtaisen
kirjoitustavan:

```{.cpp tiedosto="esimerkit/08-soa.cpp" osa="soa"}
```

```{.makefile tiedosto="esimerkit/Makefile" osa="soa"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-soa.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/08-soa.txt"}
```

L1-hutia on AoS-asettelussa 88/64 ≈ 1,4 hiukkasta kohden, kuten
rivin koosta voi laskea, ja SoA-asettelussa 16/64 = 0,25. Käskyjä SoA
tekee tässä enemmän, koska GCC ei vektoroinut `zip`-silmukkaa, mutta
muistiliikenne ratkaisee, ja SoA on moninkertaisesti nopeampi. SoA:n
hinta on kirjoitustapa ja oikeellisuus: kentät on pidettävä yhtä
pitkinä, ja yhden hiukkasen kaikkien kenttien käsittely koskee kahdeksaa
eri taulukkoa. Usein paras on välimuoto: kuumat kentät yhteen
rakenteeseen ja harvoin käytetyt, kuten nimi, erilliseen taulukkoon
(engl. hot/cold splitting).

## Säiliöiden asettelu

Standardikirjaston säiliöt jakautuvat kahteen ryhmään. *Yhtenäiset*
säiliöt (`std::vector`, `std::array`, `std::string`, `std::deque`
lohkoittain) tallentavat alkiot peräkkäin. *Solmupohjaiset* säiliöt
(`std::list`, `std::map`, `std::set`, `std::unordered_map`) varaavat
jokaiselle alkiolle oman solmun, jossa on alkion lisäksi osoittimia.
Haku solmupohjaisesta säiliöstä on osoittimien seuraamista, ja jokainen
askel voi olla välimuistihuti.

Järjestetty vektori on hakuun usein parempi kuin `std::map`: sama
logaritminen haku, mutta data on yhtenäistä. C++23:n `std::flat_map`
(GCC 15:stä alkaen) tarjoaa saman valmiina; tässä se on
kirjoitettu itse:

```{.cpp tiedosto="esimerkit/08-sailiot.cpp" osa="jarjestetty"}
```

```{.cpp tiedosto="esimerkit/08-sailiot.cpp" osa="haut"}
```

```{.tuloste tiedosto="esimerkit/08-sailiot.odotettu"}
```

Cachegrind laskee haun käskyt, L1-hudit ja viimeisen tason hudit
kahdellakymmenellätuhannella avaimella:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-sailiot.txt"}
```

Järjestetty vektori tekee jopa enemmän käskyjä kuin puu, mutta
välimuistihutia on kolmannes eikä viimeisen tason huteja juuri ollenkaan:
koko taulukko (160 kt) mahtuu simuloituun 256 kt:n välimuistiin, mutta
puun 20 000 solmua eivät. Miljoonalla avaimella ero näkyy ajassa:

```{.tuloste tiedosto="esimerkit/tulokset/08-sailiot.txt"}
```

Hajautustaulu on hakuun nopein, koska se tekee keskimäärin yhden
hyppäyksen. libstdc++:n `std::unordered_map` on kuitenkin
solmupohjainen: jokainen alkio on oma varauksensa, ja läpikäynti on
osoittimien seuraamista. Standardi vaatii, että alkioiden osoitteet
pysyvät, joten avoimen osoituksen tauluja, kuten Abseilin
`flat_hash_map` tai Boostin `unordered_flat_map`, ei voi käyttää
standardin nimellä. Ne ovat usein moninkertaisesti nopeampia.

Järjestetyn vektorin lisäys on lineaarinen, koska alkiot on
siirrettävä. Se sopii siis kokoelmiin, jotka rakennetaan kerran ja
joista haetaan paljon, kuten asetuksiin, sanakirjoihin ja
reititystauluihin. Usein lisättäviin ja poistettaviin kokoelmiin sopii
hajautustaulu.

## Käytännössä

- **Järjestä jäsenet tasauksen mukaan** ja tarkista koko
  `static_assert`illa tyypeille, joita on paljon.
- **Vältä `std::vector<bool>`ia** yleiskäyttöisessä koodissa; käytä
  `std::vector<std::uint8_t>`ia tai `std::bitset`iä.
- **Kuumat kentät yhteen**, kylmät erilleen. SoA kun silmukat käyttävät
  harvoja kenttiä kerrallaan ja datamäärä on suuri.
- **Oletussäiliö on `std::vector`.** Järjestetty vektori tai
  `std::flat_map` hakuun, hajautustaulu usein muuttuvaan kokoelmaan,
  `std::map` vasta kun tarvitaan järjestys ja pysyvät osoitteet.
- **Mittaa välimuistihudit**, älä pelkkiä käskyjä: säiliöiden erot ovat
  muistissa.

## Itsearviointi

- Osaat laskea rakenteen koon täytteineen ja pienentää sitä jäsenten
  järjestyksellä ja `[[no_unique_address]]`-määreellä.
- Osaat selittää `std::vector<bool>`in välityöolion ja sen sudenkuopat.
- Osaat muuttaa AoS-asettelun SoA-asetteluksi ja mitata eron
  välimuistihuteina.
- Osaat valita järjestetyn vektorin, `std::map`in ja hajautustaulun
  välillä haku- ja muutostarpeen perusteella.
