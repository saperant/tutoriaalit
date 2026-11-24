# Laitteisto–ohjelmisto-jako

Kiihdytin on laitteisto, joka tekee yhden tehtävän nopeammin tai
pienemmällä energialla kuin suoritin: suodin, salaus, pakkaus,
neuroverkon kerros. Päätös siitä, mitä tehdään laitteistolla ja mitä
ohjelmistolla, on *laitteisto–ohjelmisto-jako* (*HW/SW partitioning*).
Se on kauppa: kiihdytin vie pinta-alaa ja suunnittelutyötä, ja sen
käyttäminen maksaa aina jotakin: ajurin, datansiirrot ja keskeytykset.
Kiihdytin kannattaa vain, jos säästö on suurempi kuin nämä kulut.

Tämä luku mallintaa saman päätöksen kahdesti: analyyttisesti ja
virtuaaliprototyypillä. Analyyttinen malli käy vaihtoehdot läpi
nopeasti, ja prototyyppi tarkistaa, että malli on oikein ja ettei siitä
puutu mitään.

## Profiilista ehdokkaaseen

Jaon lähtökohta on profiili: mihin ohjelman aika kuluu (paketti
*Suorituskyvyn analyysi ja optimointi*). Hyvällä ehdokkaalla on neljä
ominaisuutta:

1. **Suuri osuus ajasta.** Amdahlin laki rajaa koko sovelluksen
   nopeutuksen: jos tehtävä on 60 % ajasta, ääretönkin kiihdytin antaa
   enintään 2,5-kertaisen nopeutuksen.
2. **Säännöllinen laskenta.** Kiinteät silmukat, ennustettava
   muistinkäyttö ja vähän haaroja sopivat laitteistoon. Osoitinjahti ja
   monimutkainen ohjaus eivät.
3. **Paljon laskentaa siirrettyä dataa kohden.** Jokainen tavu on
   siirrettävä kiihdyttimelle ja takaisin.
4. **Riittävän suuret kutsut.** Kiinteät kulut kuoletetaan kutsun
   koolla, joten pienet kutsut eivät kannata.

## Esimerkki: FIR-suodin

16-tappinen FIR-suodin 32-bittisillä kokonaisluvuilla. Sama funktio on
ohjelmiston ja kiihdyttimen viitemalli:

```{.cpp tiedosto="esimerkit/07-prototyyppi/kiihdytin.hpp" osa="fir"}
```

Ohjelmistototeutuksen kustannus tulee profiloinnista: kaksi jaksoa
tappia kohden ja kymmenen jaksoa näytettä kohden silmukan hallintaan,
yhteensä 42 ns näytteelle 1 GHz:n suorittimella. Kiihdytin laskee yhden
näytteen jaksossa, mutta sen käyttäminen maksaa:

```{.cpp tiedosto="esimerkit/07-prototyyppi/main.cpp" osa="kustannukset"}
```

## Analyyttinen malli

Malli laskee kiihdyttimen ajan osista: asetus (rekisterikirjoitukset),
välimuistin huuhtelu, jotta kiihdytin näkee ajantasaisen datan
muistissa, DMA-siirrot palasina, laskenta, liukuhihnan tyhjennys ja
keskeytyksen käsittely:

```{.python tiedosto="esimerkit/07-jako.py" osa="malli"}
```

Ilman kaksoispuskurointia kiihdytin lukee palan, laskee sen ja kirjoittaa
tuloksen ennen seuraavaa palaa. Kaksoispuskuroinnilla siirrot ja
laskenta ovat käynnissä yhtä aikaa, ja pala kestää pisimmän niistä.

## Virtuaaliprototyyppi

Prototyyppi on SystemC-malli: prosessori, väylä, muisti ja kiihdytin,
jolla on rekisterit ja DMA. Väylä ja muisti ovat samat kuin luvussa 5.
Kiihdytin on TLM-kohde rekistereilleen ja TLM-aloittaja DMA:lleen:

```{.cpp tiedosto="esimerkit/07-prototyyppi/kiihdytin.hpp" osa="rekisterit"}
```

```{.cpp tiedosto="esimerkit/07-prototyyppi/kiihdytin.hpp" osa="dma"}
```

Prosessori ajaa saman suotimen ohjelmistona ja kiihdyttimellä.
Ohjelmistoversio laskee tuloksen ja kuluttaa kustannusmallin mukaisen
ajan. Laitteistoversio on ajuri: huuhtelu, neljä rekisterikirjoitusta
väylän yli, odotus keskeytykselle ja keskeytyksen käsittely.

```{.cpp tiedosto="esimerkit/07-prototyyppi/main.cpp" osa="ohjelmisto"}
```

```{.cpp tiedosto="esimerkit/07-prototyyppi/main.cpp" osa="laitteisto"}
```

```{.cpp tiedosto="esimerkit/07-prototyyppi/main.cpp" osa="kokoonpano"}
```

```{.tuloste tiedosto="esimerkit/07-prototyyppi/odotettu"}
```

Tulokset ovat samat kummallakin toteutuksella, mikä on prototyypin
ensimmäinen tehtävä: se on myös ajurin ja kiihdyttimen toiminnallinen
testi. 16 näytteen kutsussa kiihdytin on kolme kertaa *hitaampi* kuin
ohjelmisto, koska keskeytyksen käsittely yksin kestää kolme kertaa
kauemmin kuin koko ohjelmistolaskenta. 4096 näytteellä se on seitsemän
kertaa nopeampi.

## Malli ja prototyyppi

Analyyttistä mallia verrataan prototyypin tuloksiin:

```{.python tiedosto="esimerkit/07-jako.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/07-jako.odotettu"}
```

Malli ja prototyyppi ovat täsmälleen samaa mieltä, koska tässä
prototyypissä ei ole mitään, mitä malli ei tunne: väylällä ei ole
kilpailua, koska prosessori odottaa kiihdytintä eikä tee muuta. Jos
prosessori jatkaisi omaa työtään kiihdyttimen rinnalla, sen
muistiliikenne kilpailisi DMA:n kanssa väylästä ja muistista, ja
prototyyppi näyttäisi eron (luku 5). Täsmällinen yhteensopivuus ei siis
todista mallia oikeaksi yleisesti, vain tässä käyttötilanteessa.

Kun malli on tarkistettu, sillä voi tutkia vaihtoehtoja, joita
prototyypissä ei ole:

```{.python tiedosto="esimerkit/07-jako.py" osa="vaihtoehdot"}
```

Taulukko vastaa kysymyksiin, jotka ratkaisevat suunnittelun:

- **Tasapiste** on 57 näytettä: sitä lyhyemmät kutsut kannattaa laskea
  ohjelmistolla. Keskeytys hallitsee pieniä kutsuja. Jos ajuri
  kyselee tilarekisteriä (200 ns) keskeytyksen sijaan, tasapiste
  putoaa kahdeksaan näytteeseen, mutta prosessori on varattu koko
  kiihdyttimen ajan.
- **Kaksoispuskurointi** parantaa suurten kutsujen nopeutusta 7,3:sta
  8,9:ään, koska laskenta piiloutuu siirtojen alle. Rajoittavaksi jää
  DMA: kiihdytin on muistirajoitteinen samassa mielessä kuin luvun 3
  roofline-mallissa.
- **Sovelluksen nopeutus** ratkaisee lopulta. Jos suodin on 60 %
  sovelluksen ajasta, mikään vaihtoehto ei anna yli 2,2-kertaista
  nopeutusta, ja parhaan ja huonoimman vaihtoehdon ero on 5 %. Jos tavoite
  on 3-kertainen nopeutus, kiihdyttimen hiominen ei auta, vaan
  kiihdytettävä on muitakin osia.

## Käytännössä

- **Laske kiinteät kulut.** Ajurin, keskeytyksen, välimuistin
  huuhtelun ja datan siirron kulut ovat usein suurempia kuin itse
  laskenta. Ne määräävät tasapisteen, ja pienet kutsut kannattaa
  koota suuremmiksi.
- **Amdahl koko sovellukselle.** Kiihdyttimen nopeutus ei ole
  sovelluksen nopeutus. Laske sovelluksen nopeutus profiilin
  osuuksista ennen kuin päätät.
- **Malli ja prototyyppi yhdessä.** Prototyyppi testaa ajurin ja
  rajapinnan ja tarkistaa mallin; malli käy vaihtoehdot läpi. Kun ne
  eroavat, selvitä syy ennen kuin luotat kumpaankaan.
- **Mallinna kilpailu, jos se on totta.** Jos suoritin tekee työtä
  kiihdyttimen rinnalla, jaetut väylät ja muistit on mallinnettava
  kilpailun kanssa.

## Itsearviointi

- Osaat arvioida profiilista, onko tehtävä hyvä kiihdytinehdokas.
- Osaat kirjoittaa kiihdyttimen ajan mallin kiinteistä ja muuttuvista
  kuluista ja laskea tasapisteen.
- Osaat rakentaa virtuaaliprototyypin, jossa prosessori ohjaa
  kiihdytintä rekistereillä ja kiihdytin käyttää muistia DMA:lla.
- Osaat laskea kiihdyttimen vaikutuksen koko sovellukseen Amdahlin
  lailla.
