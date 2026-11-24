# Perintöjärjestelmän uudistaminen

Useimmat palveluarkkitehtuurit eivät synny tyhjästä vaan vanhan
järjestelmän tilalle. Vanha järjestelmä on *perintöjärjestelmä*
(*legacy*): se tuottaa rahaa, sen säännöt ovat koodissa eivätkä
dokumentaatiossa, ja kukaan ei uskalla muuttaa sitä. Kiusaus on kirjoittaa
kaikki uudelleen kerralla. Kokemus on tylyä: kokonaan uudelleen
kirjoittaminen (*big bang rewrite*) kestää vuosia, vanhan järjestelmän
on samaan aikaan pysyttävä hengissä ja kehittyttävä, ja uusi järjestelmä
toteuttaa harvoin kaikki vanhan unohtuneet säännöt. Turvallisempi tapa
on korvata vanha pala kerrallaan.

## Vanha järjestelmä

Esimerkin vanha asiakasrekisteri puhuu omaa kieltään: puolipisteillä
erotetut kentät, nimi isoilla kirjaimilla sukunimi ensin, tila
kirjainkoodina ja päivämäärä ilman erottimia:

```{.java tiedosto="esimerkit/uudistus/src/main/java/fi/tutoriaalit/palvelut/uudistus/vanha/Asiakasrekisteri.java"}
```

## Korruption estokerros

Uusi järjestelmä tarvitsee asiakastietoja jo ennen kuin ne on siirretty
pois vanhasta. Jos uusi koodi lukisi vanhan muotoa suoraan, vanhan
käsitteet (kirjainkoodit, merkkijonopäivämäärät) leviäisivät uuteen
koodiin, ja vanhan poistuminen vaatisi uuden koodin muuttamista
kaikkialla. *Korruption estokerros* (*anti-corruption layer*, ACL) on
ainoa paikka, joka tuntee vanhan muodon, ja se kääntää sen uuden
järjestelmän malliksi:

```{.java tiedosto="esimerkit/uudistus/src/main/java/fi/tutoriaalit/palvelut/uudistus/uusi/Korruptionestokerros.java" osa="acl"}
```

```{.java tiedosto="esimerkit/uudistus/src/test/java/fi/tutoriaalit/palvelut/uudistus/uusi/KorruptionestokerrosTest.java" osa="kaanna"}
```

Tuntematon tilakoodi on virhe, ei oletusarvo. Kerros on myös paikka,
josta löytyvät vanhan järjestelmän yllätykset: tyhjät kentät,
vanhentuneet koodit ja eri tavoin muotoillut päivämäärät. Niiden
käsittely kirjataan testeiksi, jotka dokumentoivat vanhan järjestelmän
käytöksen.

## Kuristajaviikuna

Martin Fowler nimesi mallin kuristajaviikunan (*strangler fig*)
mukaan: viikuna kasvaa isäntäpuun ympärille, kunnes isäntä kuolee ja
viikuna seisoo omillaan. Ohjelmistossa vanhan järjestelmän eteen
asetetaan *julkisivu*, jota kaikki asiakkaat kutsuvat. Aluksi julkisivu
välittää kaiken vanhalle. Sen jälkeen toiminnot siirretään uudelle
yksi kerrallaan, ja julkisivu ohjaa niiden reitit uudelle:

```{.java tiedosto="esimerkit/uudistus/src/main/java/fi/tutoriaalit/palvelut/uudistus/reunat/Kuristaja.java" osa="kasittele"}
```

Reitin siirto etenee kolmessa vaiheessa. Laskujen uudessa
toteutuksessa on aluksi bugi, ja rinnakkaisajo löytää sen ennen kuin
yksikään asiakas näkee väärän vastauksen:

```{.java tiedosto="esimerkit/uudistus/src/test/java/fi/tutoriaalit/palvelut/uudistus/reunat/KuristajaTest.java" osa="vaiheet"}
```

*Rinnakkaisajossa* (*parallel run*, *shadow traffic*) molemmat
järjestelmät käsittelevät samat pyynnöt, asiakas saa vanhan, luotetun
vastauksen, ja erot kirjataan. Uuden järjestelmän vika tai hitaus ei
näy asiakkaalle. Kun erojen lista pysyy tyhjänä riittävän kauan, reitti
siirretään. Rinnakkaisajo sopii lukuihin ja laskentaan; muuttavia
toimintoja ei voi ajaa kahdesti, joten niille käytetään pientä
liikenneosuutta uudelle (*kanarialintu*, *canary*) ja nopeaa
palautusta vanhalle.

## Abstraktiolla haarauttaminen

Kuristajaviikuna toimii järjestelmän reunalla. Jos korvattava osa on
syvällä vanhan järjestelmän sisällä, käytetään *abstraktiolla
haarauttamista* (*branch by abstraction*): korvattavan osan eteen
tehdään rajapinta, vanha toteutus siirretään sen taakse, uusi toteutus
rakennetaan rinnalle ja asetuksella valitaan, kumpi on käytössä. Kaikki
tapahtuu päähaarassa pienin muutoksin, eikä pitkäikäistä kehityshaaraa
tarvita.

## Tiedon siirto

Toiminnon siirto on helppo osa; tiedon siirto on vaikea. Vaihtoehdot:

| Tapa | Miten | Hinta |
|------|-------|-------|
| Lukeminen ACL:n kautta | uusi lukee vanhaa, kunnes data siirretään | vanha pysyy kriittisenä riippuvuutena |
| Kertasiirto | data siirretään katkon aikana | katko; paluu vanhaan vaikea |
| Muutostietojen kaappaus | vanhan tietokannan muutokset virtaavat uuteen (CDC) | infrastruktuuri; kaksisuuntaisuus vaikeaa |
| Kaksoiskirjoitus | sovellus kirjoittaa molempiin | epäjohdonmukaisuus, jos toinen kirjoitus epäonnistuu |

Yleinen järjestys: ensin uusi toiminto lukee vanhaa dataa ACL:n kautta,
sitten CDC pitää uuden kopion ajan tasalla, ja lopuksi kirjoitukset
käännetään uuteen ja vanhalle syötetään muutokset takaisin niin kauan
kuin jokin vanha toiminto niitä tarvitsee. Kaksoiskirjoitusta
sovelluksesta kannattaa välttää samasta syystä kuin suoraa lähetystä
outboxin sijaan (luku 10).

## Käytännössä

- **Korvaa pala kerrallaan, älä kirjoita kaikkea uudelleen.** Jokainen
  siirretty reitti tuottaa arvoa heti, ja virheen voi perua yhdellä
  asetuksella.
- **Julkisivu ensin.** Kun asiakkaat kutsuvat julkisivua, reitit voi
  siirtää ilman, että asiakkaiden tarvitsee muuttua.
- **Korruption estokerros on ainoa paikka, joka tuntee vanhan
  muodon.** Vanhan poistuessa poistuu yksi luokka.
- **Rinnakkaisajo ennen siirtoa** luku- ja laskentatoiminnoille,
  kanarialintu ja nopea paluu muuttaville.
- **Kirjaa vanhan järjestelmän käytös testeiksi.** Ne ovat usein ainoa
  dokumentaatio säännöistä, jotka uuden on toteutettava.
- **Hinnat:** siirtymäaikana ylläpidetään kahta järjestelmää ja
  julkisivua; tiedon siirto on projektin riskialttein osa; vanhaa ei saa
  unohtaa sammuttaa, muuten lopputulos on kaksi perintöjärjestelmää.

## Itsearviointi

- Osaat perustella, miksi kokonaan uudelleen kirjoittaminen on riskialtis
  ja miten kuristajaviikuna pienentää riskiä.
- Osaat toteuttaa korruption estokerroksen, joka kääntää vanhan muodon
  uuden järjestelmän malliksi.
- Osaat toteuttaa reitittävän julkisivun ja rinnakkaisajon ja kertoa,
  milloin rinnakkaisajo ei sovi.
- Osaat selittää abstraktiolla haarauttamisen ja valita tiedon
  siirtotavan.
