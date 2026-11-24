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

## Kenelle ja mitä tarvitaan

Lukija osaa ohjelmoida Pythonilla ja tuntee diskreetin matematiikan
perusteet, erityisesti kombinatoriikan (taito *Diskreetti matematiikka*).
Derivaattoja ja integraaleja käytetään jatkuvien jakaumien kohdalla
kevyesti; laskut tehdään koodilla. Tutoriaali valmistaa taitoihin
*Tiedonsiirto* (kohina ja bittivirhesuhde), *Säteenseuranta* (Monte
Carlo -integrointi) ja *Arkkitehtuurin tutkiminen* (suorituskyvyn
mallit). Jonoteoria on käsitelty taidossa *Tietoliikennetekniikka*.

| Luku | Kysymys | Käytännössä |
|------|---------|-------------|
| Tapahtumat | Kuinka todennäköistä? | törmäykset, nopat |
| Ehdollinen todennäköisyys | Mitä havainto kertoo? | testit, hälytykset, roskaposti |
| Diskreetit jakaumat | Montako kertaa? | pakettihäviö, uudelleenyritykset |
| Jatkuvat jakaumat | Kuinka kauan, kuinka paljon? | väliajat, mittausvirhe |
| Odotusarvo ja varianssi | Mitä keskimäärin, kuinka hajallaan? | toleranssit |
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
simulaatiot NumPylla. Jokainen simulaatio käyttää kiinteää
satunnaissiementä, joten tuloste on joka ajolla sama ja voidaan
verrata talletettuun tulosteeseen. Esimerkit tarkistetaan ruffilla
ja mypyllä tiukassa tilassa.

Ensimmäinen esimerkki laskee kahden nopan summan todennäköisyydet
tarkasti murtolukuina ja vertaa komplementtisäännön tulosta
simulaation frekvensseihin:

```{.python tiedosto="esimerkit/02-noppa.py" osa="simulointi"}
```

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
