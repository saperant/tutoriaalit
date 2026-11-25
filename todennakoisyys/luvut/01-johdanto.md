# Johdanto {.runko-johdanto}

Insinöörin ja ohjelmoijan arki on täynnä satunnaisuutta: paketteja
häviää, anturin lukema kohisee, palvelimen vasteaika vaihtelee,
komponentti hajoaa ennen aikojaan ja käyttäjä klikkaa tai jättää
klikkaamatta. Todennäköisyyslaskenta on kieli, jolla tällaisia ilmiöitä
kuvataan, ja tilastotiede on menetelmä, jolla mittauksista päätellään
jotain luotettavaa.

Tämä tutoriaali käsittelee todennäköisyyttä ja tilastoja
käytännön näkökulmasta. Jokainen kaava lasketaan koodilla ja
tarkistetaan simuloimalla: teoria ja simulaatio tulostetaan rinnakkain.
Simulaatio ei korvaa kaavaa, mutta se paljastaa väärin sovelletun
kaavan nopeasti ja antaa vastauksen tilanteissa, joihin kaavaa ei ole.

## Esitiedot ja rajaus

Esitiedoksi tarvitaan taito *Diskreetti matematiikka*: joukot,
kombinatoriikka ja summamerkintä sekä sen esitietona Python-ohjelmointi.
Jatkuvien jakaumien kohdalla käytetään integraalia pinta-alan
merkityksessä; laskut tehdään koodilla, eikä integrointitekniikoita
tarvita. Niitä opettaa taito *Differentiaali- ja integraalilaskenta*,
joka käsittelee myös tiheysfunktion integraalina. Desibelit ja
logaritmit kerrataan taidossa *Matematiikan perusteet ohjelmallisesti*.

Tutoriaali valmistaa taitoihin *Digitaalinen tiedonsiirto* (kohina ja
bittivirhesuhde), *Säteenseuranta ja fysikaalinen valaistus* (Monte
Carlo -integrointi) ja *Arkkitehtuurin mallinnus ja suunnittelutilan
tutkiminen* (suorituskyvyn mallit). Rajauksen ulkopuolelle jäävät

- jonoteoria (taito *Tietoliikennetekniikka*)
- pienimmän neliösumman sovituksen laskenta matriiseilla, Markovin
  ketjut ja pääkomponenttianalyysi (taito *Lineaarialgebra*)
- usean selittäjän regressio, varianssianalyysi ja Bayes-päättely
  jakaumilla; niihin ohjaavat luvun *Lopuksi* lähteet
- kryptografinen satunnaisuus (taito *Kryptografia*).

| Luku | Kysymys | Käytännössä |
|------|---------|-------------|
| Tapahtumat | Kuinka todennäköistä? | törmäykset, nopat |
| Ehdollinen todennäköisyys | Mitä havainto kertoo? | testit, hälytykset, roskaposti |
| Diskreetit jakaumat | Montako kertaa? | pakettihäviö, uudelleenyritykset |
| Jatkuvat jakaumat | Kuinka kauan, kuinka paljon? | väliajat, mittausvirhe |
| Odotusarvo ja varianssi | Mitä keskimäärin, kuinka hajallaan? | toleranssit |
| Kaksi muuttujaa | Vaihtelevatko suureet yhdessä? | korrelaatio, regressio |
| Raja-arvolauseet | Miksi keskiarvo toimii? | mittausten keskiarvoistus |
| Kohina | Kuinka paljon signaalia? | SNR, differentiaalimittaus |
| Satunnaisluvut | Mistä satunnaisuus tulee? | simulaatiot, testit |
| Monte Carlo | Entä kun kaavaa ei ole? | integraalit, todennäköisyydet |
| Estimointi | Mitä mittauksista voi päätellä? | luottamusvälit |
| Hypoteesitestaus | Onko ero todellinen? | A/B-testit |
| Mittausten tulkinta | Mitä viive kertoo? | persentiilit, hännät |

## Työkalut ja esimerkit

Esimerkit ovat Python-ohjelmia hakemistossa `esimerkit/`. Tarkat
laskut tehdään standardikirjastolla (`math`, `fractions`) ja
simulaatiot NumPylla. Esimerkit tarkistetaan ruffilla ja mypyllä
tiukassa tilassa.

Simulaatio arpoo satunnaislukuja, mutta sen tuloste on silti joka
ajolla sama. Satunnaisluvut tuottaa *generaattori*, jonka lukujonon
määrää alkuarvo eli *siemen* (`default_rng(2026)`): sama siemen antaa
saman jonon. Näin tulostetta voidaan verrata talletettuun
tulosteeseen. Ensimmäinen esimerkki heittää neljää noppaa ja laskee,
kuinka usein mukana on vähintään yksi kutonen:

```{.python tiedosto="esimerkit/02-noppa.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/02-noppa.odotettu" rivit="5-"}
```

Mitä useammin koe toistetaan, sitä lähemmäs frekvenssi asettuu yhtä
lukua. Seuraava luku laskee tuon luvun tarkasti ja palaa siemeneen.
Kuvat piirretään Matplotlibilla skriptillä `kuvat/piirra.py`
(`make kuvat`) samoilla siemenillä kuin esimerkit.

Kehityskontissa (`.devcontainer/todennakoisyys`) on Python, NumPy ja
tarkistustyökalut. Esimerkki ajetaan komennolla
`python3 esimerkit/02-noppa.py`, ja kaikki tarkistetaan komennolla
`make testaa`.

## Merkinnät

$P(A)$ on tapahtuman $A$ todennäköisyys, $P(A \mid B)$ ehdollinen
todennäköisyys, $E[X]$ satunnaismuuttujan $X$ odotusarvo ja
$\operatorname{Var}(X)$ sen varianssi. Kreikkalainen $\mu$ on
odotusarvo, $\sigma$ keskihajonta ja $\lambda$ tapahtumien taajuus.
Merkintä $X \sim \mathrm{Bin}(n, p)$ tarkoittaa, että $X$ noudattaa
binomijakaumaa parametrein $n$ ja $p$. Koodissa tulosteet käyttävät
desimaalipistettä.
