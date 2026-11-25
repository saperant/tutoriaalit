# Johdanto {.runko-johdanto}

Kolmiulotteinen peli on samaa peliohjelmointia kuin kaksiulotteinen:
kiinteä aika-askel, syöte, tila, törmäykset ja resurssit pysyvät.
Kolmas ulottuvuus muuttaa kuitenkin lähes jokaista osaa. Asento ei ole
enää yksi kulma vaan kierto avaruudessa, ja kiertoja ei voi laskea
yhteen. Kamera on pelin olio, jolla on oma paikkansa, liikkeensä ja
törmäyksensä. Maailma on kolmioverkko, jossa hahmo kulkee rinteitä ja
portaita. Hahmo ei ole kuvasarja vaan luuranko, jonka asento lasketaan
joka ruudulla.

Tämä tutoriaali käsittelee näitä muutoksia: orientaatioita ja
kvaternioita, muunnoshierarkiaa, törmäyksiä ja säteenheittoa kolmessa
ulottuvuudessa, kameroita, hahmon liikettä, näkyvyyskarsintaa,
luurankoanimaatiota ja resurssien lataamista. Lopuksi osat kootaan
pieneksi kolmannen persoonan peliksi, *Lyhdyksi*.

Aiheena on pelin rakenne, ei kuvan piirtäminen. Kuvat syntyvät
pienellä ohjelmistorenderöijällä, joka on apuväline: sen periaatteet
opetetaan taidossa *Renderöinnin perusteet*.

## Esitiedot ja rajaus

Tutoriaali jatkaa kahdesta taidosta, ja niiden sisältöä ei opeteta
uudelleen:

- *Peliohjelmointi*: pelisilmukka ja kiinteä aika-askel, syötteen
  tallennus, tilakoneet, entiteetit ja ECS, kaksiulotteiset törmäykset
  ja törmäysvaste, laajan vaiheen ruudukko, reitinhaku ja resurssien
  kahvat.
- *Renderöinnin perusteet*: vektorit ja 4 × 4 -matriisit koodina,
  malli-, näkymä- ja projektiomatriisi, perspektiivijako, rasterointi,
  syvyyspuskuri ja valaistus.

Näiden kautta oletetaan myös *Moderni C++* ja *Lineaarialgebra*.

Tutoriaalin ulkopuolelle jäävät:

- **Dynamiikka.** Hahmo liikkuu tässä *kinemaattisesti*: koodi päättää
  sen liikkeen, ja törmäykset vain estävät sitä. Voimat, jäykän
  kappaleen pyöriminen, nivelet ja pinoutuvat kappaleet kuuluvat
  taitoon *Pelifysiikka*.
- **Renderöinti ja grafiikkarajapinnat.** Varjostus, tekstuurit ja
  näytönohjaimen ohjelmointi ovat taidoissa *Renderöinnin perusteet*
  ja *GPU-ohjelmointi: OpenGL ja Vulkan*.
- **Verkkopelaaminen** on taidossa *Reaaliaikaiset moninpelit*.
- **Pelimoottorin käyttö.** Viimeinen luku kertoo, missä tässä opitut
  asiat näkyvät Godotissa, Unityssä ja Unrealissa, mutta moottorin
  käyttöä ei opeteta.

## Sopimukset

Kolmiulotteisessa pelissä on sovittava asioista, jotka kahdessa
ulottuvuudessa olivat itsestään selviä. Tutoriaali käyttää samoja
sopimuksia kuin *Renderöinnin perusteet* ja glTF-tiedostomuoto:

| Asia | Sopimus |
|------|---------|
| koordinaatisto | oikeakätinen, y ylös |
| kameran katselusuunta | paikallinen −z; +x on oikealla |
| mallin etupuoli | paikallinen +z (glTF) |
| yksikkö | metri; kulmat koodissa radiaaneina |
| vektorit ja matriisit | sarakevektorit, `M * v`; tulossa oikeanpuoleinen muunnos tehdään ensin |
| kierron suunta | positiivinen kulma kiertää vastapäivään, kun akseli osoittaa katsojaa kohti |

Sopimukset vaihtelevat moottorista ja työkalusta toiseen: Unrealissa
z on ylös ja koordinaatisto vasenkätinen, Blenderissä z on ylös ja
koordinaatisto oikeakätinen, Unityssä y on ylös ja koordinaatisto
vasenkätinen. Väärä oletus näkyy kyljelleen kaatuneena tai
peilikuvaksi kääntyneenä mallina. Muunnos tehdään kerran, kun resurssi
tuodaan peliin, eikä pelikoodissa.

## Ensimmäinen kohtaus

Pelin tila on kolmessakin ulottuvuudessa dataa. Kappaleella on
*muunnos* eli sijainti, kierto ja skaala, ja sen muoto on resurssi,
jonka moni kappale voi jakaa.

```{.cpp tiedosto="esimerkit/01-kohtaus.cpp" osa="kappale"}
```

Kohtaus on luettelo kappaleita ja kamera. Kierto annetaan akselina ja
kulmana; mitä `akselikulma` palauttaa, selviää luvussa *Kvaterniot*.

```{.cpp tiedosto="esimerkit/01-kohtaus.cpp" osa="kohtaus"}
```

Kappaleen paikka ruudulla saadaan viemällä sen sijainti näkymä- ja
projektiomatriisin läpi ja jakamalla w:llä. Leikkausavaruuden w on
samalla kappaleen etäisyys kamerasta katselusuunnassa.

```{.cpp tiedosto="esimerkit/01-kohtaus.cpp" osa="ruudulle"}
```

```{.tuloste tiedosto="esimerkit/01-kohtaus.odotettu"}
```

![Ensimmäinen kohtaus. Maailman akselit on piirretty origoon: x
punainen, y vihreä ja z sininen.](kuvat/kohtaus.png){width=70%}

Tuloste on se, mitä testit tarkistavat: lukuja, jotka ovat samat
jokaisella ajokerralla. Kuva syntyy samasta ohjelmasta, kun sille
annetaan argumentiksi tiedoston nimi.

## Tutoriaalin rakenne

| Luku | Aihe |
|------|------|
| Orientaatio ja Eulerin kulmat | kolme kulmaa, kiertojen järjestys, lukkiutuminen |
| Kvaterniot | akseli ja kulma, yhdistäminen, normalisointi, slerp |
| Muunnoshierarkia | paikallinen ja maailmamuunnos, likaisuuslippu, vanhemman vaihto |
| Törmäysmuodot | pallo, laatikko, kapseli ja kolmio; lähin piste |
| Säteenheitto | säde ja muodot, valinta hiirellä, pyyhkäisy |
| Laaja vaihe: BVH | hierarkian rakennus ja läpikäynti kolmioverkolle |
| Kamerat | ensimmäinen ja kolmas persoona, pehmennys, törmäys |
| Hahmon liike | kapseli kolmioverkossa: rinteet, portaat, seinät |
| Näkyvyyskarsinta | näkymäkartion tasot, hierarkkinen karsinta |
| Luurankoanimaatio | nivelet, skinnaus, leikkeet ja sekoitus |
| Resurssit ja glTF | tiedoston rakenne, lataus ja tarkistus |
| Lyhty | kokonainen pieni peli |
| Lopuksi | pelimoottorit, nyrkkisäännöt, jatkotaidot ja lähteet |

Luvut rakentuvat toistensa päälle: hahmon liike tarvitsee
törmäysmuodot, säteenheiton ja BVH:n, ja animaatio tarvitsee
kvaterniot ja hierarkian. Kokenut lukija voi lukea lukujen
itsearvioinnit ensin ja ohittaa hallitsemansa luvut.

## Esimerkit ja työkalut

Esimerkit ovat C++23:a. Ne käännetään testeissä GCC 14:llä ja Clang
20:llä AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa, ja
molempien kääntäjien tulosteen on oltava sama. Yhteinen koodi on
otsaketiedostoina hakemistossa `esimerkit/yhteinen/`:

| Otsake | Sisältö |
|--------|---------|
| `vektori.hpp` | `Vec3`, `Mat4`, kamera- ja projektiomatriisi |
| `kvaternio.hpp` | `Kvat`, slerp ja TRS-muunnos `Muunnos` |
| `tormays.hpp`, `sade.hpp` | törmäysmuodot, lähimmät pisteet ja säteet |
| `bvh.hpp`, `maailma.hpp` | laaja vaihe ja staattinen törmäysmaailma |
| `kartio.hpp` | näkymäkartion tasot |
| `hahmo.hpp` | hahmo-ohjain |
| `luuranko.hpp` | nivelet, skinnaus ja animaatioleikkeet |
| `gltf.hpp` | glTF-lataaja |
| `piirto.hpp`, `mallit.hpp`, `maasto.hpp` | kuvitus: renderöijä ja verkot koodista |

Ainoa ulkoinen kirjasto on JSON-jäsennin *nlohmann/json* glTF-lukua
varten (Ubuntun paketti `nlohmann-json3-dev`). Kehityskontissa
(`.devcontainer/peliohjelmointi-3d`) se on asennettuna.

Yksittäisen esimerkin voi kääntää ja ajaa esimerkkihakemistossa:

```text
g++ -std=c++23 -Wall -Wextra -fsanitize=address,undefined 09-hahmo.cpp
./a.out             # testattu tuloste
./a.out rata        # lisäksi kuva rata.ppm ja reitti rata.txt
```

Esimerkit eivät avaa ikkunaa eivätkä tarvitse näytönohjainta. Kuvat
tallentuvat PPM-tiedostoiksi, jotka useimmat kuvankatselijat avaavat.
Paketin kuvat tuottaa `make kuvat`, joka ajaa samat ohjelmat
suuremmalla tarkkuudella.
