# Nollaluottamus

Perinteinen verkko jaettiin ulko- ja sisäpuoleen. Palomuuri suojasi
reunaa, ja kaikkeen sisäverkosta tulevaan luotettiin. Malli toimii
vain, jos sisäpuolelle ei koskaan pääse kukaan väärä. Kokemus on
osoittanut toisin: tietomurroissa hyökkääjä liikkuu tyypillisesti
viikkoja sisäverkossa koneelta toiselle, koska kerran sisään päässyttä
ei enää tarkisteta.

Nollaluottamus (*zero trust*) luopuu oletuksesta, että verkon sijainti
kertoo jotain luotettavuudesta. Jokainen pyyntö todennetaan ja
valtuutetaan erikseen, riippumatta siitä, mistä se tulee.

## Sisäverkkoon luottava palvelu

Seuraava palvelu antaa asiakkaan maksutiedot laskutuspalvelulle. Se
tunnistaa kutsujan otsakkeesta, jonka "kaikki sisäverkon palvelut
asettavat oikein":

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/MtlsTest.java" osa="haavoittuva"}
```

Kun suosituspalvelu on murrettu, hyökkääjä voi kirjoittaa saman
otsakkeen itse:

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/MtlsTest.java" osa="hyokkays"}
```

Otsake, IP-osoite ja verkkosegmentti kertovat vain, mistä pyyntö
näyttää tulevan. Ne eivät todista mitään, koska hyökkääjä hallitsee
niitä kaikkia omalla koneellaan. Todiste on jotain, mitä vain oikea
kutsuja pystyy esittämään: yksityisellä avaimella tehty allekirjoitus.

## Periaatteet

NIST:n julkaisu SP 800-207 kuvaa nollaluottamuksen arkkitehtuurin.
Sen periaatteet tiivistettynä:

1. **Kaikki resurssit suojataan**, myös sisäiset palvelut,
   tietokannat ja hallintarajapinnat.
2. **Kaikki liikenne suojataan sijainnista riippumatta.** Sisäverkon
   liikenne salataan ja todennetaan samoin kuin internetin yli kulkeva.
3. **Pääsy myönnetään pyyntö kerrallaan** ja vähimmin oikeuksin.
   Kerran annettu pääsy ei kelpaa seuraavaan resurssiin.
4. **Päätös perustuu dynaamiseen käytäntöön:** kutsujan identiteetti,
   pyydetty resurssi ja tilanne, kuten laitteen kunto, aika ja
   käyttäytyminen.
5. **Laitteiden ja palvelujen tilaa valvotaan** jatkuvasti.
6. **Todennus ja valtuutus tehdään ennen pääsyä** ja uudelleen
   istunnon aikana.
7. **Tietoa kerätään** ja sitä käytetään suojauksen parantamiseen.

Arkkitehtuurissa on kolme roolia. **Päätöspiste** (*policy decision
point*, PDP) arvioi käytännön ja päättää. **Täytäntöönpanopiste**
(*policy enforcement point*, PEP) on se kohta, jonka läpi pyyntö
kulkee: palvelun suodatin, sivuvaunuvälityspalvelin tai
yhdyskäytävä. **Hallintapiste** (*policy administrator*) välittää
päätöksen täytäntöönpanopisteelle ja hallitsee istuntoja.

## Päätös pyyntö kerrallaan

Luvun 9 käytäntömoottori on päätöspiste. Seuraava käytäntö sallii
asiakkaalle hänen omat tiedostonsa, mutta vain hallitulta laitteelta
ja monivaiheisella tunnistuksella:

```{.json tiedosto="esimerkit/kaytannot/src/test/resources/kaytannot/asiakas.json"}
```

Sama käyttäjä saa eri vastauksen eri tilanteessa. Päätös tehdään
jokaiselle pyynnölle, ei kerran kirjautuessa:

```{.java tiedosto="esimerkit/kaytannot/src/test/java/fi/tutoriaalit/palveluturva/kaytannot/KaytannotTest.java" osa="nollaluottamus"}
```

## Mitä nollaluottamus ei ole

Nollaluottamus ei ole tuote, jonka voi ostaa, eikä se tarkoita, ettei
mihinkään luoteta. Se siirtää luottamuksen verkosta asioihin, jotka
voidaan todistaa: kryptografisiin identiteetteihin, allekirjoitettuihin
tokeneihin ja todennettuun laitteen tilaan. Varmentajaan,
avainpalveluun ja käytäntöjen päätöspisteeseen luotetaan, ja siksi ne
ovat kokonaisuuden arvokkaimmat kohteet.

Verkon segmentointi ei myöskään muutu tarpeettomaksi. Se on edelleen
hyödyllinen syvyyssuuntainen puolustus (luku 10), mutta se ei ole
enää ainoa este.

## Käytännössä

- **Aloita identiteeteistä.** Ilman luotettavaa tapaa tietää, kuka
  kutsuu, mitään muuta ei voi päättää oikein. Työkuormien
  identiteetit (luvut 3–4) ovat nollaluottamuksen perusta.
- **Älä luota otsakkeisiin, joita kutsuja voi asettaa.** `X-User`,
  `X-Forwarded-For` ja vastaavat ovat vain väitteitä, ellei niiden
  asettajaa ole todennettu ja vastaanottaja tarkista sitä.
- **Etene vaiheittain.** Kokonaisuutta ei muuteta kerralla. Tyypillinen
  järjestys on: palvelujen välinen mTLS, palvelukohtaiset oikeudet,
  käyttäjän identiteetin välitys palvelujen läpi ja lopuksi
  dynaamiset ehdot.
- **Mittaa vahinkoa.** Hyvä kysymys jokaiseen suunnitelmaan: jos tämä
  palvelu murretaan, mihin hyökkääjä pääsee? Vastauksen pitää olla
  lyhyt lista.

## Itsearviointi

- Osaat selittää, miksi sisäverkon sijainti tai otsake ei todista
  kutsujan identiteettiä.
- Osaat nimetä nollaluottamuksen periaatteet ja roolit PDP ja PEP.
- Osaat kuvata, miten pyyntökohtainen päätös eroaa kirjautumisen
  yhteydessä tehdystä päätöksestä.
- Osaat arvioida palvelukokonaisuudesta, mihin yhden palvelun murto
  johtaa.
