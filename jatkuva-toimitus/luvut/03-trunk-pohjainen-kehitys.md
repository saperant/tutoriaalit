# Trunk-pohjainen kehitys

Jatkuva integraatio kertoo, kuinka usein työ yhdistetään.
Trunk-pohjainen kehitys (*trunk-based development*) on haarautumismalli,
joka seuraa siitä: kaikki tekevät työnsä yhteen runkoon, ja muut haarat
ovat lyhytikäisiä tai niitä ei ole. Tutoriaali *Versionhallinta (Git)*
käyttää samasta asiasta nimeä runkopohjainen kehitys ja esittelee
työnkulun Gitin komentoina. Tässä luvussa kysymys on, miten päivittäin
voi yhdistää työtä, joka valmistuu vasta viikkojen päästä.

## Haarautumismallit

Haarautumismallit eroavat siinä, missä keskeneräinen työ odottaa ja
kuinka kauan.

```{.dot otsikko="Trunk-pohjainen kehitys: lyhyet haarat palaavat runkoon päivässä tai kahdessa, julkaisuhaara otetaan rungosta"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.32;
  node [shape=circle, label="", width=0.16, fixedsize=true];
  { node [group=runko]; m0; m1; m2; m3; m4; m5; m6; }
  { node [group=julk]; r1; r2; }
  rl [shape=plaintext, style="", label="runko", fixedsize=false,
      group=runko];
  jl [shape=plaintext, style="", label="julkaisuhaara", fixedsize=false,
      group=julk];
  m0 -> m1 -> m2 -> m3 -> m4 -> m5 -> m6;
  m6 -> rl [style=invis];
  m1 -> a1 -> m3;
  m3 -> b1 -> m5;
  m4 -> r1 -> r2;
  r2 -> jl [style=invis];
  m6 -> r2 [style=dashed, constraint=false];
}
```

Katkoviiva kuvaa korjausta, joka tehdään ensin runkoon ja poimitaan
sieltä julkaisuhaaraan.

```{.dot otsikko="GitFlow: työ kulkee ominaisuushaarasta kehityshaaran ja julkaisuhaaran kautta päähaaraan"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.32;
  node [shape=circle, label="", width=0.16, fixedsize=true];
  { node [group=om]; f1; f2; f3; f4; }
  { node [group=ke]; d0; d1; d2; d3; d4; d5; d6; }
  { node [group=ju]; r1; r2; }
  { node [group=pa]; p0; p1; }
  ol [shape=plaintext, style="", label="ominaisuushaara",
      fixedsize=false, group=om];
  kl [shape=plaintext, style="", label="kehityshaara", fixedsize=false,
      group=ke];
  jl [shape=plaintext, style="", label="julkaisuhaara", fixedsize=false,
      group=ju];
  pl [shape=plaintext, style="", label="päähaara", fixedsize=false,
      group=pa];
  p0 -> d0;
  d0 -> d1 -> d2 -> d3 -> d4 -> d5 -> d6;
  d0 -> f1 -> f2 -> f3 -> f4 -> d5;
  d5 -> r1 -> r2;
  r2 -> p1; r2 -> d6;
  p0 -> p1;
  f4 -> ol [style=invis]; d6 -> kl [style=invis];
  r2 -> jl [style=invis]; p1 -> pl [style=invis];
}
```

| Malli | Pitkäikäiset haarat | Missä työ odottaa | Sopii, kun |
|-----------------|-----------------|------------------|----------------------|
| trunk-pohjainen | runko, tarvittaessa julkaisuhaarat | ei missään: päivä tai kaksi | tiimi julkaisee usein ja testit ovat kattavat |
| lyhyet ominaisuushaarat ja yhdistämispyyntö | runko | katselmointijonossa | katselmointi vaaditaan ennen yhdistämistä |
| GitFlow | päähaara, kehityshaara, julkaisu- ja korjaushaarat | ominaisuushaaroissa ja kehityshaarassa | julkaisut ovat harvoja ja useaa versiota tuetaan rinnan |

Keskimmäinen rivi on käytännössä trunk-pohjaisen kehityksen muunnelma,
*jos* haarat todella ovat lyhyitä. Paul Hammantin ylläpitämä sivusto
trunkbaseddevelopment.com, joka on mallin perusteellisin kuvaus, pitää
rajana päivää tai kahta ja yhtä tekijää haaraa kohden. Viikon
ominaisuushaara ei ole trunk-pohjaista kehitystä, vaikka se
yhdistettäisiin suoraan runkoon.

GitFlow on Vincent Driessenin vuonna 2010 julkaisema malli. Se ratkaisee
todellisen ongelman: miten hallitaan ohjelmistoa, josta on asiakkailla
useita versioita ja jonka julkaisu on harvinainen ja raskas tapahtuma.
Jatkuvasti toimitettavaan verkkopalveluun se on tarpeettoman raskas,
ja Driessen on itse lisännyt artikkeliinsa myöhemmin huomautuksen, jossa
suosittelee sellaiseen yksinkertaisempaa työnkulkua. Mallia ei siis
kannata arvostella yleisesti, vaan kysyä, onko oma tilanne se, johon se
suunniteltiin.

## Säännöt

Trunk-pohjaisen kehityksen säännöt ovat lyhyet.

1. **Runko on aina julkaisukelpoinen.** Jokainen runkoon päätyvä
   commit on läpäissyt putken.
2. **Runkoon yhdistetään vähintään päivittäin.** Suoraan tai enintään
   päivän tai kahden ikäisen haaran kautta.
3. **Julkaisut tehdään rungosta.** Joko suoraan rungon commitista tai
   julkaisuhaarasta, joka otetaan rungosta juuri ennen julkaisua.
4. **Korjaukset tehdään runkoon.** Jos julkaisuhaara tarvitsee
   korjauksen, se tehdään ensin runkoon ja poimitaan sieltä
   (`git cherry-pick`). Näin korjaus ei voi unohtua seuraavasta
   julkaisusta.
5. **Julkaisuhaaroja ei yhdistetä takaisin.** Ne ovat päätepisteitä ja
   poistuvat, kun versiota ei enää tueta.

Sääntö 4 on se, jonka rikkominen aiheuttaa eniten vahinkoa. Kiireessä
julkaisuhaaraan tehty korjaus, joka jää viemättä runkoon, palaa vikana
seuraavassa julkaisussa.

## Keskeneräisen työn piilottaminen

Jos runko on aina julkaisukelpoinen ja siihen yhdistetään päivittäin,
keskeneräinen ominaisuus on rungossa ennen kuin se on valmis. Tämä on
mallin vaikein kohta, ja siihen on neljä tekniikkaa, jotka täydentävät
toisiaan.

**Pienet askelet, jotka eivät muuta käytöstä.** Suuri osa
ominaisuudesta on valmistelua: uusi funktio, uusi taulu, uusi luokka.
Niitä voi yhdistää runkoon heti, koska mikään ei vielä kutsu niitä.
Refaktorointi, joka tekee tilaa uudelle, on samalla tavalla
vaaraton, kun testit pitävät käytöksen ennallaan.

**Sisäänkäynti viimeisenä.** Uusi näkymä rakennetaan valmiiksi, ja
linkki tai valikon kohta lisätään vasta lopuksi. Uusi rajapinnan
päätepiste voi olla rungossa dokumentoimattomana, kunnes se on valmis.

**Ominaisuusliput.** Kun uutta ja vanhaa käytöstä tarvitaan rinnan,
valinta tehdään ajon aikana asetuksella. Luku 7 käsittelee liput
tarkemmin.

**Haarautuminen abstraktiolla** (*branch by abstraction*). Kun
vaihdettava asia on laaja, kuten kirjasto, tietokantakerros tai
laskentasääntö, vaihto tehdään koodin rakenteella eikä
versionhallinnan haaralla.

```{.dot otsikko="Haarautuminen abstraktiolla: vaihto tehdään neljässä askeleessa, joista jokainen on julkaisukelpoinen"}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.35;
  a [label="1. abstraktio\nvanhan eteen"];
  b [label="2. uusi toteutus\nrinnalle"];
  c [label="3. valinta\nuuteen"];
  d [label="4. vanha ja\nvalinta pois"];
  a -> b -> c -> d;
}
```

Esimerkissä hinnoittelusääntö vaihdetaan portaista liukuvaan
alennukseen. Rajapinta `Hinnoittelu` on abstraktio, `Portaat` vanha ja
`Liukuva` uusi toteutus.

```{.python tiedosto="esimerkit/luku03/abstraktio.py" osa="rajapinta"}
```

Uusi toteutus kasvaa rungossa commit kerrallaan. Koska se toteuttaa
saman rajapinnan, sille voidaan ajaa samat sopimustestit kuin vanhalle
koko kehityksen ajan, ja vaihto on lopulta yhden rivin muutos.

```{.python tiedosto="esimerkit/luku03/abstraktio.py" osa="sopimus"}
```

```{.tuloste tiedosto="esimerkit/luku03/abstraktio.odotettu"}
```

Tekniikalla on hintansa. Abstraktio on ylimääräistä rakennetta, ja
jos neljäs askel jää tekemättä, koodiin jää kaksi toteutusta ja
valintalogiikka. Toisaalta abstraktio, joka syntyy vaihtoa varten,
on usein juuri se sauma, jota koodi olisi tarvinnut testattavuuden
vuoksi muutenkin (ks. *Testivetoinen kehitys ja testisuunnittelu*,
testattava suunnittelu).

Sama ajatus toimii myös järjestelmien välillä. Tutoriaali
*Palveluarkkitehtuurit* esittelee kuristajaviikunan (*strangler fig*),
jossa vanha järjestelmä korvataan pala kerrallaan reitittämällä
liikennettä uuteen.

## Katselmointi

Yleisin vastaväite trunk-pohjaiselle kehitykselle on katselmointi: jos
muutos on katselmoitava ennen runkoa, se odottaa haarassa.
Vastaväite on aiheellinen, ja ratkaisuja on kolme.

**Pienet ja nopeat yhdistämispyynnöt.** Muutaman kymmenen rivin
muutos katselmoidaan minuuteissa. Jos tiimi sopii, että katselmointi
ohittaa oman työn ja vastausaika on tunteja eikä päiviä, haara pysyy
alle päivän ikäisenä. Pieni muutos katselmoidaan myös paremmin: suuren
muutoksen katselmointi rappeutuu helposti selailuksi.

**Parityö.** Kun kaksi ihmistä tekee muutoksen yhdessä, katselmointi
tapahtuu kirjoitettaessa eikä erillistä odotusta tarvita. Moni tiimi
hyväksyy parina tehdyn muutoksen suoraan runkoon.

**Katselmointi yhdistämisen jälkeen.** Kaikki muutokset eivät tarvitse
samaa menettelyä. Rouan Wilsenachin kuvaama jako *ship, show, ask*
erottaa kolme tapausta: rutiinimuutos yhdistetään suoraan,
kiinnostava muutos yhdistetään ja näytetään muille jälkikäteen, ja
vain epävarma tai riskialtis muutos jää odottamaan hyväksyntää.

Mikä näistä sopii, riippuu luottamuksesta ja vaatimuksista. Säännelty
ala voi vaatia toisen ihmisen hyväksynnän jokaiseen tuotantoon
menevään muutokseen. Silloin valitaan ensimmäinen tai toinen tapa, ja
hyväksynnän jälki tallentuu yhdistämispyyntöön tai commitin
tietoihin. Katselmoinnin sisältöä tietoturvan näkökulmasta käsittelee
*Tietoturva kehitystyössä*.

## Julkaisuhaarat ja tuetut versiot

Verkkopalvelulla on tuotannossa yksi versio, ja julkaisuhaaraa ei
tarvita: julkaisu on rungon commit. Asennettavalla ohjelmistolla,
kirjastolla tai laiteohjelmistolla on kentällä monta versiota yhtä
aikaa, ja niitä korjataan vuosia. Silloin jokaista tuettua versiota
varten on julkaisuhaara.

Trunk-pohjainen kehitys sopii tähänkin, kunhan säännöt 4 ja 5 pidetään.
Julkaisuhaaraan ei kehitetä mitään. Sinne poimitaan rungosta vain
korjauksia, ja jokainen tuettu haara ajaa oman putkensa. Tuettujen
versioiden määrä on kustannus, joka kannattaa pitää näkyvissä:
jokainen korjaus on poimittava ja testattava jokaiseen haaraan
erikseen.

## Milloin malli ei sovi

- **Avoimen lähdekoodin projekti.** Ulkopuolinen tekijä työskentelee
  omassa kopiossaan (*fork*) ja lähettää yhdistämispyynnön. Ylläpitäjät
  itse voivat silti työskennellä trunk-pohjaisesti.
- **Testit puuttuvat.** Malli nojaa siihen, että putki pysäyttää
  rikkinäisen muutoksen. Ilman testejä runko ei pysy
  julkaisukelpoisena.
- **Tiimi ei osaa pilkkoa työtä.** Tämä on tavallisin este, ja se
  korjautuu harjoittelemalla. Aloittaa voi lyhentämällä haarojen
  ikää asteittain.
- **Julkaisu on aidosti harvinainen ja kallis.** Laitteen mukana
  toimitettava ohjelmisto tai sertifioitava järjestelmä voi tarvita
  pitkän vakautusvaiheen. Kehitys voi silti olla trunk-pohjaista
  vakautushaaraan asti.

Accelerate-kirjan tutkimusaineistossa trunk-pohjainen kehitys (vähän
aktiivisia haaroja, haarojen ikä alle päivän, ei koodin jäädytyksiä)
oli yhteydessä parempaan toimituskykyyn. Tulos on kyselytutkimuksen
korrelaatio, ei koe, ja luku 11 palaa sen tulkintaan. Mekanismi on
kuitenkin se, jonka luku 2 näytti: lyhyt haara on pieni erä.

## Käytännössä

- Aseta haaran iälle raja ja mittaa sitä. Yhdestä kahteen päivää on
  hyvä tavoite, ja siihen pääsee asteittain.
- Opettele pilkkomaan: valmistelu ensin, käytöksen muutos viimeisenä,
  ja jokainen commit jättää testit vihreiksi.
- Käytä abstraktiota, kun vaihdat laajaa kokonaisuutta, ja kirjaa
  vanhan toteutuksen poisto tehtäväksi heti.
- Tee korjaukset runkoon ja poimi julkaisuhaaraan, ei toisin päin.
- Sovi katselmoinnille vastausaika. Odottava yhdistämispyyntö on
  keskeneräistä työtä.

## Itsearviointi

- Osaat verrata trunk-pohjaista kehitystä ja GitFlow'ta ja kertoa,
  millaiseen tilanteeseen kumpikin on suunniteltu.
- Osaat luetella trunk-pohjaisen kehityksen säännöt ja perustella,
  miksi korjaus tehdään ensin runkoon.
- Osaat pilkkoa ominaisuuden askeliin, joista jokainen on
  julkaisukelpoinen, ja valita piilotustekniikan.
- Osaat toteuttaa haarautumisen abstraktiolla ja kertoa sen neljä
  askelta.
- Osaat esittää kolme tapaa sovittaa katselmointi päivittäiseen
  yhdistämiseen.
