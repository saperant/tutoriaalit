# Törmäysmuodot

Taito *Peliohjelmointi* käsitteli törmäykset tasossa: laatikot,
ympyrät ja erottavan akselin lause. Kolmessa ulottuvuudessa muotoja on
enemmän ja testit pidempiä, mutta useimmat palautuvat yhteen
kysymykseen: mikä on muodon lähin piste annettuun pisteeseen? Tässä
luvussa rakennetaan pelin tavallisimmat muodot ja testit tämän
kysymyksen varaan.

## Muodot

```{.cpp tiedosto="esimerkit/yhteinen/tormays.hpp" osa="muodot"}
```

| Muoto | Mihin | Miksi |
|-------|-------|-------|
| pallo | ammukset, laukaisualueet, karkea ympärys | testi on yksi etäisyys; kierto ei vaikuta |
| akselien suuntainen laatikko (AABB) | laajan vaiheen ympärykset, staattiset laatikot | testi on kuusi vertailua |
| kapseli | hahmot | pyöreä pohja liukuu reunojen yli, eikä kapseli takerru kulmiin kääntyessään |
| kolmio | staattinen maailma | mikä tahansa pinta voidaan esittää kolmioina |

*Kapseli* on jana, jonka ympärillä on säteen levyinen vaippa, eli
sylinteri, jonka päät ovat puolipalloja. Se on hahmojen vakiomuoto.

Testin tulos ei ole pelkkä totuusarvo. Jotta päällekkäin joutuneet
muodot voidaan erottaa, tarvitaan *kosketus*: suunta, johon ensimmäistä
muotoa työnnetään, ja matka, jonka se on toisen sisällä.

## Lähin piste

Janan lähin piste saadaan projisoimalla piste janan suoralle ja
rajaamalla tulos janan päiden väliin. Laatikon lähin piste saadaan
rajaamalla jokainen koordinaatti erikseen.

```{.cpp tiedosto="esimerkit/yhteinen/tormays.hpp" osa="lahin"}
```

Kolmion lähin piste on joko pisteen kohtisuora projektio kolmion
tasolle, jos projektio osuu kolmion sisään, tai muuten lähin piste
jollakin kolmesta reunasta:

```{.cpp tiedosto="esimerkit/yhteinen/tormays.hpp" osa="lahin-kolmio"}
```

```{.cpp tiedosto="esimerkit/05-muodot.cpp" osa="lahin"}
```

```{.tuloste tiedosto="esimerkit/05-muodot.odotettu" rivit="1-4"}
```

Kolme pistettä osuvat kolmion kolmeen erilaiseen alueeseen: ensimmäisen
lähin piste on kolmion sisällä, toisen reunalla ja kolmannen kärjessä.

## Pallo ja kapseli lähimmän pisteen avulla

Pallo osuu muotoon, jos muodon lähin piste pallon keskipisteeseen on
sädettä lähempänä. Kosketuksen normaali on suunta lähimmästä pisteestä
keskipisteeseen ja syvyys säteen ja etäisyyden erotus. Sama ydin
palvelee kaikkia pallon ja kapselin testejä:

```{.cpp tiedosto="esimerkit/yhteinen/tormays.hpp" osa="pallotesti"}
```

Kapselin testit ovat pallon testejä, joissa pallon keskipisteeksi
valitaan se janan piste, joka on lähinnä toista muotoa. Kapseli ja
pallo tarvitsee janan lähimmän pisteen, kaksi kapselia kahden janan
lähimmät pisteet:

```{.cpp tiedosto="esimerkit/yhteinen/tormays.hpp" osa="lahin-janat"}
```

Kapselin ja kolmion testi tarvitsee janan ja kolmion lähimmät pisteet.
Jos jana lävistää kolmion, etäisyys on nolla. Muuten lähimmät pisteet
löytyvät joko janan päästä tai kolmion reunalta, ja ehdokkaita on
viisi:

```{.cpp tiedosto="esimerkit/yhteinen/tormays.hpp" osa="lahin-jana-kolmio"}
```

## Laatikot

Kaksi akselien suuntaista laatikkoa leikkaa, jos ne limittyvät
jokaisella kolmella akselilla. Pallon ja laatikon testi käyttää
lähintä pistettä. Jos pallon keskipiste on laatikon sisällä, lähin
piste on keskipiste itse eikä normaalia voi laskea, joten ulos
työnnetään lähimmän sivun kautta.

```{.cpp tiedosto="esimerkit/yhteinen/tormays.hpp" osa="laatikkotesti"}
```

Kierretyn laatikon (*OBB*) ja yleisen kuperan kappaleen testit
perustuvat erottavan akselin lauseeseen, jonka periaate on taidossa
*Peliohjelmointi*; kolmessa ulottuvuudessa kahdella laatikolla on 15
ehdokasakselia. Fysiikkamoottorit käyttävät kuperille kappaleille
yleistä GJK-algoritmia. Molemmat kuuluvat taitoon *Pelifysiikka*.

## Testit yhdessä

```{.cpp tiedosto="esimerkit/05-muodot.cpp" osa="muodot"}
```

```{.cpp tiedosto="esimerkit/05-muodot.cpp" osa="testit"}
```

```{.tuloste tiedosto="esimerkit/05-muodot.odotettu" rivit="6-12"}
```

![Esimerkin muodot ja kosketusten normaalit punaisina viivoina.
Tällainen vianetsintäkuva kannattaa rakentaa peliin heti: väärin päin
osoittava normaali näkyy kuvasta mutta ei
lukutaulukosta.](kuvat/muodot.png){width=75%}

Pallon ja laatikon normaali osoittaa laatikosta poispäin, pallon ja
lattian suoraan ylös. Pystyssä seisova hahmo on kymmenen senttiä
lattian sisällä, ja vaakasuora palkki painaa sitä vinosti ylhäältä.

## Ympärykset

Jokaiselle muodolle tarvitaan lisäksi akselien suuntainen
*ympäryslaatikko* laajaa vaihetta varten:

```{.cpp tiedosto="esimerkit/yhteinen/tormays.hpp" osa="ymparys"}
```

## Käytännössä

- **Törmäysmuoto ei ole piirrettävä verkko.** Hahmo on kapseli,
  tynnyri sylinteri tai kapseli ja talo muutama laatikko. Tarkkaa
  kolmioverkkoa käytetään vain staattiselle maailmalle.
- **Palauta kosketus, älä totuusarvoa.** Normaali ja syvyys tarvitaan
  heti, kun muotoja pitää erottaa.
- **Sovi normaalin suunta kerran.** Tässä normaali osoittaa toisesta
  muodosta ensimmäiseen. Puolet törmäysvirheistä on väärinpäin olevia
  normaaleja.
- **Käsittele nollaetäisyys.** Kun keskipisteet ovat samassa pisteessä
  tai jana lävistää kolmion, normaalia ei voi laskea jakamalla. Koodin
  on valittava jokin järkevä suunta eikä jaettava nollalla.
- **Piirrä törmäysmuodot.** Vianetsintäpiirto maksaa tunnin ja säästää
  päiviä.

## Itsearviointi

- Osaat valita pelin kappaleelle törmäysmuodon ja perustella valinnan.
- Osaat laskea janan, laatikon ja kolmion lähimmän pisteen ja rakentaa
  pallon ja kapselin testit niiden varaan.
- Osaat kertoa, mitä kosketuksen normaali ja syvyys tarkoittavat ja
  mihin niitä käytetään.
- Osaat nimetä tapaukset, joissa normaalia ei voi laskea suoraan, ja
  kertoa, miten ne käsitellään.
