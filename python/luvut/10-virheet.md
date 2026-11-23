# Virheenkäsittely {.runko-virheet}

Pythonissa virheet ilmaistaan poikkeuksilla. Toisin kuin C++:ssa,
poikkeus on Pythonissa halpa ja tavallinen ohjausvuon keino:
standardikirjasto itse nostaa `KeyError`-, `StopIteration`- ja
`FileNotFoundError`-poikkeuksia tavallisissa tilanteissa. Tämä luku
käsittelee poikkeusten tyylin (EAFP), omat poikkeushierarkiat,
ketjutuksen ja poikkeusryhmät.

## EAFP ja LBYL

Kaksi tyyliä käsitellä tilannetta, jossa toiminto voi epäonnistua:

```{.python tiedosto="esimerkit/10-eafp.py" osa="lbyl"}
```

```{.python tiedosto="esimerkit/10-eafp.py" osa="eafp"}
```

*LBYL* (*look before you leap*) tarkistaa ensin ja toimii sitten.
*EAFP* (*easier to ask forgiveness than permission*) yrittää ja
käsittelee epäonnistumisen. Python suosii EAFP-tyyliä kolmesta
syystä:

1. **Ei kilpatilannetta.** Tarkistuksen ja toiminnon välissä maailma
   voi muuttua: tiedosto poistuu, avain poistetaan toisessa säikeessä.
   Tiedostojen kanssa LBYL on aina virhe (esimerkki alla).
2. **Yksi operaatio kahden sijaan.** `in` ja `[]` hakevat avaimen
   kahdesti.
3. **Halpa onnistuessa.** Python 3.11:stä alkaen `try`-lohkoon
   siirtyminen ei maksa mitään (*zero-cost exceptions*). Poikkeuksen
   nostaminen ja sieppaaminen maksaa mikrosekunnin luokkaa, mikä on
   Python-mittakaavassa sama kuin muutama funktiokutsu.

```{.python tiedosto="esimerkit/10-eafp.py" osa="tiedosto"}
```

```{.tuloste tiedosto="esimerkit/10-eafp.odotettu"}
```

C++:ssa sama tyyli olisi virhe, koska poikkeuksen heittäminen on siellä
satoja kertoja kalliimpaa kuin paluuarvo ja poikkeus on varattu
poikkeuksellisille tilanteille. Malli ei siirry kielestä toiseen.

EAFP ei tarkoita, että kaikki käärittäisiin `try`-lohkoon. Kun puuttuva
arvo on tavallinen tapaus, `dict.get(avain, oletus)` on selkein. Kun
epäonnistuminen on yleistä ja suorituskyky ratkaisee (miljoonia rivejä,
joista puolet virheellisiä), tarkistus voi olla nopeampi kuin
poikkeuksen nostaminen.

## Poikkeushierarkia

Kaikki tavalliset poikkeukset periytyvät `Exception`-luokasta.
`BaseException`-luokan suoria aliluokkia ovat `KeyboardInterrupt`,
`SystemExit` ja `GeneratorExit`, joita ei ole tarkoitus siepata.
Siksi `except Exception` on leveimmillään oikea muoto, ja paljas
`except:` on virhe.

Kirjasto tai sovellus määrittelee oman kantaluokan, jonka alle sen
virheet kootaan:

```{.python tiedosto="esimerkit/10-poikkeukset.py" osa="hierarkia"}
```

Kutsuja voi siepata kaikki sovelluksen virheet yhdellä
`except SovellusVirhe` -lauseella tai tietyn virheen tarkemmin.
Poikkeukselle kannattaa antaa kentät, joita kutsuja tarvitsee (tässä
`avain`), jotta viestiä ei tarvitse jäsentää.

## Ketjutus

Kun alemman tason poikkeus muunnetaan sovelluksen poikkeukseksi,
`raise ... from virhe` säilyttää alkuperäisen syyn `__cause__`-
attribuutissa. `from None` katkaisee ketjun, kun alkuperäinen virhe on
epäolennainen:

```{.python tiedosto="esimerkit/10-poikkeukset.py" osa="ketjutus"}
```

```{.python tiedosto="esimerkit/10-poikkeukset.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-poikkeukset.odotettu"}
```

`json.JSONDecodeError` on `ValueError`-luokan aliluokka, joten
virheellinen JSON päätyy samaan haaraan kuin virheellinen luku.
Puuttuva avain ei tarvitse syytä: `KeyError: 'portti'` ei kerro mitään,
mitä viesti ei jo kertoisi.

Käsittelemättömän ketjutetun poikkeuksen pinojälki näyttää molemmat
poikkeukset:

```{.python tiedosto="esimerkit/10-ketju.kaatuu.py"}
```

```{.tuloste tiedosto="esimerkit/10-ketju.virhe"}
```

Tulosteessa on pinojäljestä vain tarkistetut rivit; todellinen
tuloste sisältää lisäksi tiedostonimet ja rivinumerot. Ilman
`from`-osaa Python ketjuttaa poikkeukset silti, mutta viestillä
*During handling of the above exception, another exception occurred*,
joka antaa ymmärtää, että käsittelijässä oli bugi.

## try-lauseen osat

| Osa | Suoritetaan |
|-----|-------------|
| `try` | aina |
| `except T as e` | kun lohkossa nousee `T` tai sen aliluokka |
| `else` | kun `try` onnistui; koodi, jonka poikkeuksia ei haluta siepata |
| `finally` | aina, myös `return`-lauseen ja poikkeuksen jälkeen |

`try`-lohko pidetään mahdollisimman pienenä: siihen kuuluu vain rivi,
jonka poikkeus käsitellään. Muuten sama poikkeustyyppi toiselta riviltä
siepataan vahingossa. Siivoukseen käytetään ensisijaisesti
`with`-lausetta (luku 7), ei `finally`-lohkoa.

## Poikkeusryhmät

Python 3.11 toi `ExceptionGroup`-luokan useiden samanaikaisten virheiden
välittämiseen. Tyypillinen käyttö on validointi, jossa käyttäjälle
halutaan kertoa kaikki virheet kerralla, ja rinnakkaiset tehtävät
(`asyncio.TaskGroup`, luku 12). `except*` käsittelee ryhmästä
tietyntyyppiset poikkeukset, ja useampi `except*`-haara voi suorittua:

```{.python tiedosto="esimerkit/10-ryhmat.py" osa="ryhmat"}
```

```{.tuloste tiedosto="esimerkit/10-ryhmat.odotettu"}
```

Jokainen `except*`-haara saa osaryhmän, jonka `exceptions`-attribuutti
sisältää haaran tyyppiset poikkeukset. Käsittelemättömät poikkeukset
nostetaan uudelleen ryhmänä.

## Käytännössä

- **EAFP oletuksena** sanakirjoille, tiedostoille, tyyppimuunnoksille
  ja ulkoisille resursseille. Kilpatilanteiden vuoksi tiedostojen ja
  verkon kanssa se on ainoa oikea tapa.
- **Oma kantapoikkeus** jokaiselle kirjastolle tai sovellukselle.
  Kutsuja voi siepata kaikki kirjaston virheet sieppaamatta
  ohjelmointivirheitä.
- **Käännä poikkeus kerroksen rajalla** (*exception translation*):
  `KeyError` tietovaraston sisällä muuttuu `TuotettaEiLoydy`-
  poikkeukseksi rajapinnassa, ja `from` säilyttää syyn.
- **Sieppaa tarkasti.** Vain odotetut poikkeustyypit, vain siinä
  kohdassa, jossa niille voi tehdä jotain. Leveä `except Exception`
  kuuluu vain ohjelman ylimmälle tasolle (pyyntökäsittelijä, työjono),
  ja siellä virhe lokitetaan pinojälkineen (`logger.exception`).
- **Älä niele virheitä.** `except: pass` piilottaa bugit. Jos poikkeus
  todella ohitetaan, `contextlib.suppress(FileNotFoundError)` kertoo
  sen nimeltä.
- **Hinta:** `try` ilman poikkeusta on ilmainen (3.11+). Poikkeuksen
  nostaminen on muutaman funktiokutsun hintainen, mutta pinojäljen
  muotoilu on kallista; sitä ei tehdä kuumassa silmukassa.
- **Sudenkuopat:** liian iso `try`-lohko, `except Exception` ilman
  lokitusta, `assert` syötteen tarkistukseen (`python -O` poistaa
  kaikki `assert`-lauseet) ja `return` `finally`-lohkossa, joka nielee
  poikkeuksen.

## Itsearviointi

- Osaat selittää EAFP- ja LBYL-tyylien erot, miksi EAFP on Pythonissa
  idiomaattinen ja miksi sama tyyli ei sovi C++:aan.
- Osaat suunnitella sovellukselle poikkeushierarkian ja antaa
  poikkeuksille hyödylliset kentät.
- Osaat ketjuttaa poikkeukset `from`-osalla ja tiedät, milloin käyttää
  `from None`.
- Osaat käyttää `try`-lauseen `else`- ja `finally`-osia oikein ja
  pitää `try`-lohkon pienenä.
- Osaat koota useita virheitä `ExceptionGroup`-ryhmäksi ja käsitellä
  ne `except*`-haaroilla.
