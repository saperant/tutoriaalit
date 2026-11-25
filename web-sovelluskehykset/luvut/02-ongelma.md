# Mitä kehys ratkaisee

Kehyksen arvo näkyy vasta, kun saman sovelluksen kirjoittaa ilman sitä.
Tämän luvun toteutus käyttää pelkkiä selaimen rajapintoja. Se toimii ja
läpäisee saman testisarjan kuin muutkin, mutta sen rakenteesta näkyy,
minkä työn kehykset ottavat itselleen.

## Kaksi totuutta

Selainsovelluksessa sama tieto on kahdessa paikassa. Ohjelman muuttujissa
on **tila**: tehtävät, valittu suodatin ja tieto siitä, onko lataus
kesken. Sivulla on **DOM**: elementit, jotka käyttäjä näkee. Jokaisen
tilan muutoksen jälkeen DOM on saatettava vastaamaan tilaa, ja jokainen
unohdus on virhe, jota mikään kääntäjä ei huomaa.

```{.dot otsikko="Sovelluksen kierros: tapahtuma muuttaa tilaa, ja näkymä on saatettava vastaamaan sitä"}
digraph {
  rankdir=LR;
  tila [label="tila\n(muuttujat)"];
  dom [label="näkymä\n(DOM)"];
  kayttaja [label="käyttäjä", shape=ellipse];
  tila -> dom [label="synkronointi:\ntämä on vaikea osa"];
  dom -> kayttaja [label="näkee"];
  kayttaja -> tila [label="tapahtuma\nmuuttaa tilaa"];
}
```

Ilman kehystä tila on tavallisissa muuttujissa. Sopimus on, että tilaa
muutetaan vain funktion `muuta` kautta, joka kutsuu lopuksi
päivitysfunktiota:

```{.typescript tiedosto="esimerkit/paljas/main.ts" osa="tila"}
```

Sopimusta ei valvo mikään. Jos jokin käsittelijä sijoittaa muuttujaan
suoraan, näkymä jää vanhaksi.

## Päivitysfunktio

Koko synkronointi on yhdessä funktiossa. Se käy läpi jokaisen DOM:n
kohdan, joka riippuu tilasta:

```{.typescript tiedosto="esimerkit/paljas/main.ts" osa="paivita"}
```

Funktiossa on kolme asiaa, jotka toistuvat jokaisessa kehyksessä
automaattisina:

1. **Johdettu tieto.** Yhteenvedon teksti, virheilmoitus ja näkyvien
   tehtävien lista lasketaan tilasta. Niitä ei tallenneta, joten ne
   eivät voi jäädä ristiriitaan tilan kanssa.
2. **Ehdollinen sisältö.** Latausilmoitus, virhe ja lista ovat näkyvissä
   vain tietyissä tiloissa. Elementit on lisättävä ja poistettava oikeassa
   järjestyksessä koskematta niihin, jotka ovat jo paikallaan.
3. **Sivuvaikutukset.** Tallennus ja sivun otsikko seuraavat tilaa.

Lisäksi funktio ajetaan kokonaan jokaisen muutoksen jälkeen, vaikka vain
yksi rivi muuttui. Tässä sovelluksessa sillä ei ole väliä. Suuressa
näkymässä on: joko päivitetään kaikki varmuuden vuoksi tai kirjoitetaan
jokaiselle muutokselle oma, täsmällinen päivityksensä. Jälkimmäinen on
nopea ja virhealtis, ja se oli jQuery-ajan sovellusten tavallinen tila.

## Listan rivit

Lista on vaikein kohta. Helpoin tapa olisi tyhjentää `<ul>` ja luoda
rivit uudelleen. Silloin kuitenkin häviää kaikki, mitä DOM itse muistaa:
kohdistus, tekstin valinta, vierityskohta ja kesken oleva animaatio.
Käyttäjä, joka on sarkaimella edennyt kolmannen rivin valintaruutuun,
putoaisi sivun alkuun aina, kun jokin rivi muuttuu.

Siksi jokaista tehtävää vastaa yksi pysyvä `<li>`, joka etsitään
tehtävän tunnisteella:

```{.typescript tiedosto="esimerkit/paljas/main.ts" osa="rivit"}
```

Tämä on käsin kirjoitettu versio siitä, mitä kehykset kutsuvat
**avaimiksi** (`key`, `track`): tapa kertoa, mikä vanha rivi vastaa
mitäkin uutta. Testisarja tarkistaa tämän ominaisuuden jokaisesta
toteutuksesta (luku 8).

## Tapahtumat

Tapahtumankäsittelijät luetaan DOM:sta ja kirjoitetaan tilaan:

```{.typescript tiedosto="esimerkit/paljas/main.ts" osa="tapahtumat"}
```

Lomakkeen kohdalla näkyy vielä yksi kahden totuuden ongelma. Kentän
arvo elää DOM:ssa (`nimiEl.value`), ei tilassa, joten tyhjennys
tehdään suoraan elementtiin. Kehyksissä sama valinta on tehtävä
tietoisesti: joko tila omistaa kentän arvon (ohjattu kenttä) tai DOM
omistaa sen.

## Mitä jäi käsin tehtäväksi

Toteutuksessa on noin 180 riviä, suunnilleen saman verran kuin
kehyksillä tehdyissä. Ero ei ole rivimäärässä vaan siinä, mistä rivit
koostuvat:

| Tehtävä | Ilman kehystä | Kehyksessä |
|---------|---------------|------------|
| näkymän rakenne | HTML-tiedosto ja `createElement`-kutsut kahdessa paikassa | yksi kuvaus komponentissa |
| tilan ja DOM:n synkronointi | `paivita` käsin, joka kohta muistettava | automaattinen |
| mikä muuttui | päivitetään kaikki tai kirjoitetaan erot itse | kehys selvittää (luku 3) |
| listan rivien säilyminen | oma taulu tunnisteesta elementtiin | avain |
| osiin jakaminen | funktioita, joilla on yhteiset muuttujat | komponentit, joilla on rajapinta |
| sivuvaikutusten ajoitus | päivitysfunktion lopussa | efektit |

Kehys ei siis tee mitään, mitä ei voisi tehdä itse. Se poistaa yhden
virheluokan, unohtuneen päivityksen, ja antaa osille rajapinnat, jolloin
sovellus voi kasvaa ilman, että jokaisen on tunnettava kaikki
muuttujat. Hinta on kehyksen oma koodi selaimessa, sen säännöt ja
riippuvuus sen elinkaaresta. Näitä punnitaan luvussa 10.

## Käytännössä

- **Pieni, enimmäkseen staattinen sivu ei tarvitse kehystä.** Lomake,
  joka lähetetään palvelimelle, tai sivu, jolla on pari vuorovaikutteista
  kohtaa, on helpompi ylläpitää ilman. Kehys kannattaa, kun samasta
  tilasta riippuu monta näkymän kohtaa.
- **Jos kirjoitat ilman kehystä, pidä yksi totuus.** Tila muuttujissa,
  yksi päivitysfunktio ja muutokset yhden portin kautta. Tilan lukeminen
  DOM:sta ("onko tämä luokka päällä") on se tapa, jolla jQuery-sovellukset
  menivät sekaisin.
- **Älä rakenna listaa uudelleen.** Uudelleenluonti hävittää
  kohdistuksen ja valinnat ja on saavutettavuusvirhe, vaikka sivu
  näyttäisi oikealta.
- **Kehysten sanasto kuvaa näitä samoja asioita.** Kun uudessa kehyksessä
  on outo käsite, kysy, mihin tämän luvun kuudesta tehtävästä se
  vastaa.

## Itsearviointi

- Osaat selittää, miksi sovelluksen tila ja DOM ovat kaksi totuutta ja
  mitä niiden synkronoinnin unohtamisesta seuraa.
- Osaat nimetä tehtävät, jotka kehys ottaa hoitaakseen, ja näyttää ne
  kehyksettömästä toteutuksesta.
- Osaat perustella, miksi listan rivit säilytetään eikä luoda uudelleen.
- Osaat arvioida, milloin sivu on niin yksinkertainen, ettei kehystä
  kannata ottaa.
