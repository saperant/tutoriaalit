# Toimituskyvyn mittarit

Edelliset luvut väittivät, että pienet ja tiheät julkaisut ovat sekä
nopeampia että turvallisempia kuin suuret ja harvat. Väitteen voi
tarkistaa omasta työstä mittaamalla. Tämä luku esittelee alan
tunnetuimmat mittarit, laskee ne Git-historiasta ja käsittelee sitä,
miten mittarit menevät pilalle.

## Neljä mittaria

Nicole Forsgrenin, Jez Humblen ja Gene Kimin kirja *Accelerate* (2018)
ja sen taustalla olevat DORA-tutkimusohjelman (*DevOps Research and
Assessment*) vuosittaiset State of DevOps -raportit ovat vakiinnuttaneet
neljä mittaria ohjelmistotoimituksen suorituskyvylle.

| Mittari | Mitä mittaa | Laji |
|------------------------|--------------------------------------|-----------|
| julkaisutiheys | kuinka usein tuotantoon viedään muutoksia | nopeus |
| muutoksen läpimenoaika | aika commitista siihen, että muutos on tuotannossa | nopeus |
| epäonnistuneiden muutosten osuus | kuinka suuri osa käyttöönotoista aiheuttaa häiriön tai vaatii korjauksen | vakaus |
| palautumisaika | kuinka kauan häiriöstä toipuminen kestää | vakaus |

Mittareiden nimet ja tarkat määritelmät ovat vaihdelleet raporttien
välillä, ja neljän rinnalle on myöhemmin tuotu muitakin. Rakenne on
pysynyt: kaksi mittaria nopeudelle ja kaksi vakaudelle.

Tutkimuksen tunnetuin tulos on, että nopeus ja vakaus eivät ole
vaihtokauppa. Aineistossa organisaatiot, jotka julkaisivat usein,
myös epäonnistuivat harvemmin ja toipuivat nopeammin. Tulos on
vastoin intuitiota, jonka mukaan varovaisuus tarkoittaa harvempia
julkaisuja, mutta se on linjassa tämän tutoriaalin mekanismien kanssa:
pieni erä on helpompi testata, sen vika on helpompi paikantaa ja
peruminen on pienempi.

Mittarit valittiin niin, että ne mittaavat *tulosta* eivätkä
*toimintaa*. Koodirivit, commitien määrä tai tehtyjen tehtävien määrä
kertovat, kuinka paljon tehtiin. Neljä mittaria kertovat, kuinka
sujuvasti ja luotettavasti muutos päätyy käyttäjälle.

## Mittarit Git-historiasta

Mittarit kannattaa laskea järjestelmistä, joihin tieto syntyy
itsestään: versionhallinnasta, putkesta ja häiriöiden kirjanpidosta.
Käsin täytetty taulukko vanhenee ja kaunistuu.

Malli tarvitsee jokaisesta julkaisusta kolme tietoa: milloin se
vietiin tuotantoon, mitkä commitit siihen kuuluivat ja milloin
mahdollinen häiriö korjattiin.

```{.python tiedosto="esimerkit/toimitus/dora.py" osa="mittarit"}
```

Esimerkki luo kaksi kuuden viikon historiaa oikeisiin
Git-repositorioihin. Kummassakin tehdään samat kaksi muutosta joka
arkipäivä. Toinen tiimi julkaisee perjantaisin ja toinen joka päivä.
Julkaisut ovat tageja, ja epäonnistuneen julkaisun korjaus on oma
taginsa. Historia luetaan Gitin komennoilla.

```{.python tiedosto="esimerkit/luku11/dora.py" osa="lue"}
```

```{.tuloste tiedosto="esimerkit/luku11/dora.odotettu"}
```

Kaksi ensimmäistä riviä näyttävät eron, jota mittareilla haetaan.
Viikoittain julkaiseva tiimi tekee saman työn, mutta sen muutokset
odottavat tuotantoon pääsyä mediaaniltaan 52 tuntia, kaksi kuudesta
julkaisusta vaati korjauksen ja korjaukset kestivät kauan. Päivittäin
julkaisevan tiimin luvut ovat kaikilla neljällä mittarilla paremmat.

Esimerkin historia on keksitty, joten se ei todista mitään. Häiriöiden
määrä ja kesto on annettu sille lähtötietona luvun 2 mekanismin
mukaisesti: viikon erästä syyn etsiminen on hitaampaa kuin päivän
erästä. Esimerkki näyttää, miten luvut lasketaan ja että ne voidaan
laskea ilman erillistä kirjanpitoa, kunhan julkaisut ja korjaukset
merkitään versionhallintaan.

## Mittarin pelaaminen

Kolmas rivi on luvun tärkein. Siinä viikoittain julkaiseva tiimi on
saanut tavoitteekseen nostaa julkaisutiheyden viiteen viikossa. Se
pilkkoo perjantain julkaisun viideksi peräkkäiseksi käyttöönotoksi
kymmenen minuutin välein. Julkaisutiheys viisinkertaistuu ja
epäonnistuneiden osuus putoaa kolmanneksesta seitsemään prosenttiin,
koska sama määrä häiriöitä jakautuu useammalle julkaisulle. Mikään ei
muuttunut: käyttäjä saa muutokset yhtä myöhään ja häiriöt kestävät
yhtä kauan.

Tämä on Goodhartin laki käytännössä: kun mittarista tehdään tavoite,
se lakkaa mittaamasta. Tulosteesta näkyy myös suoja sitä vastaan.
Läpimenoaika ja palautumisaika eivät liikkuneet. Neljä mittaria on
valittu luettaviksi **yhdessä**, koska yhtä on helppo parantaa toisen
kustannuksella tai määritelmää venyttämällä, mutta kaikkia neljää
yhtä aikaa on vaikea parantaa muuten kuin parantamalla toimitusta.

Tavallisia tapoja pilata mittarit:

- **Tavoite yksittäiselle mittarille.** "Julkaisutiheys kaksinkertaiseksi"
  tuottaa tyhjiä julkaisuja.
- **Tiimien vertailu.** Sulautettua laitetta, pankin
  taustajärjestelmää ja verkkokauppaa ei voi verrata keskenään.
  Vertailu johtaa määritelmien virittämiseen.
- **Henkilöiden mittaaminen.** Mittarit kuvaavat järjestelmää, johon
  kuuluvat putki, arkkitehtuuri ja organisaation rakenne. Yksilö ei
  hallitse niitä.
- **Sidonta palkitsemiseen.** Kun epäonnistuneiden muutosten osuus
  vaikuttaa palkkioon, häiriöitä lakataan kirjaamasta.
- **Määritelmä jätetään auki.** Onko peruttu lippu epäonnistunut
  muutos? Alkaako läpimenoaika ensimmäisestä commitista vai
  yhdistämisestä? Määritelmä on sovittava ja pidettävä samana, muuten
  trendi ei tarkoita mitään.

## Tulkinta ja tutkimuksen rajat

Mittareista on hyötyä, kun niitä käyttää tiimi itse oman työnsä
parantamiseen ja katsoo suuntaa eikä tasoa. Hyvä kysymys ei ole,
olemmeko "huipputasoa", vaan mikä hidastaa meitä juuri nyt ja
liikkuiko luku, kun korjasimme sen.

DORA-raportit luokittelevat vastaajat suoritustasoihin ja julkaisevat
tasojen rajat. Rajoja ei kannata käyttää tavoitteina. Ne ovat
kyselyaineistosta ryhmittelemällä saatuja kuvauksia, ja ne ovat
vaihdelleet vuodesta toiseen.

Tutkimusta itseään on myös luettava kriittisesti.

- **Aineisto on kyselyitä.** Vastaajat arvioivat itse oman
  organisaationsa julkaisutiheyden ja muut luvut. Niitä ei ole mitattu
  järjestelmistä.
- **Yhteys ei ole syy.** Tutkimus osoittaa, että tietyt käytännöt ja
  hyvä suorituskyky esiintyvät yhdessä. Se ei osoita, että käytännön
  käyttöönotto tuottaa suorituskyvyn missä tahansa organisaatiossa.
  Yhteinen taustasyy, kuten osaava ja hyvin johdettu organisaatio, voi
  selittää molemmat.
- **Vastaajat ovat valikoituneita.** Kyselyyn vastaavat ne, joita aihe
  kiinnostaa.

Tämä ei tee tuloksista arvottomia. Ne ovat alan laajin järjestelmällinen
aineisto, ja niiden suunta on sama kuin mekanismien, jotka voi
perustella erikseen. Varovaisuus koskee sitä, kuinka pitkälle
yksittäisestä luvusta tehdään päätelmiä.

Kaikki ei myöskään mahdu näihin mittareihin. Neljä mittaria kertovat,
kuinka hyvin muutokset kulkevat. Ne eivät kerro, olivatko muutokset
oikeita, eli saiko käyttäjä jotain hyödyllistä. Nopea ja vakaa
toimitus väärästä tuotteesta on nopeaa ja vakaata hukkaa. Tuotteen
suuntaa käsittelee *Ohjelmistoprojektin hallinta*.

## Putken omat mittarit

Neljä mittaria ovat lopputuloksia, ja ne liikkuvat hitaasti.
Päivittäiseen ohjaamiseen sopivat mittarit, jotka kertovat, missä
kohtaa putkea aika kuluu.

| Mittari | Mitä se paljastaa |
|----------------------------|------------------------------------------|
| commit-vaiheen kesto | palautteen hitaus; kasvaa huomaamatta |
| jonotusaika ennen ajoa | ajokoneiden vähyys |
| rungon punainen aika | kuinka kauan muut ovat estyneinä |
| uudelleenajojen osuus | epävakaat testit |
| haaran ikä yhdistettäessä | integraation todellinen tiheys |
| katselmoinnin odotusaika | pullonkaula ennen runkoa |
| aika yhdistämisestä tuotantoon | käyttöönoton ja hyväksyntöjen viive |

Läpimenoaika kannattaa purkaa osiin, koska osat korjataan eri
keinoin. Jos muutos odottaa katselmointia kaksi päivää ja putki
kestää kymmenen minuuttia, putken nopeuttaminen ei auta.

## Häiriöistä oppiminen

Palautumisaika ja epäonnistuneiden muutosten osuus paranevat vain, jos
häiriöistä opitaan. Vakiintunut käytäntö on syyllistämätön
jälkiarviointi (*blameless postmortem*): häiriön jälkeen kirjataan,
mitä tapahtui, miten se havaittiin, mikä hidasti korjaamista ja mitä
muutetaan. Lähtökohta on, että ihminen toimi sen tiedon varassa, joka
hänellä oli, ja kysymys on, miksi järjestelmä salli virheen päätyä
tuotantoon.

Jatkuvan toimituksen kannalta jälkiarvioinnin hyödyllisimmät kysymykset
ovat samat joka kerta.

- Miksi putki ei pysäyttänyt tätä? Lisätäänkö testi, ja mihin
  vaiheeseen?
- Miksi vika osui niin moneen käyttäjään? Olisiko asteittainen
  julkaisu rajannut sen?
- Miksi havaitseminen kesti? Mikä mittari olisi näyttänyt vian
  aiemmin?
- Miksi peruminen kesti? Oliko se harjoiteltu?

Jälkiarviointeja ja niiden edellyttämää luottamusta käsittelevät
*Ohjelmistoprojektin hallinta* ja *Tiimit ja organisaatiomallit*, ja
Googlen SRE-kirja kuvaa käytännön perusteellisesti.

## Käytännössä

- Laske mittarit järjestelmistä, älä kyselyistä tai taulukoista.
  Merkitse julkaisut ja korjaukset niin, että ne voi lukea koneella.
- Sovi määritelmät: mikä on julkaisu, mikä on epäonnistunut muutos,
  mistä läpimenoaika alkaa.
- Lue neljää mittaria yhdessä ja seuraa suuntaa.
- Älä aseta mittareita tavoitteiksi, älä vertaa tiimejä äläkä
  mittaa henkilöitä.
- Pura läpimenoaika osiin ja korjaa pisin odotus.
- Pidä jälkiarviointi jokaisesta merkittävästä häiriöstä ja kysy,
  mitä putken olisi pitänyt tehdä.

## Itsearviointi

- Osaat nimetä neljä toimituskyvyn mittaria ja kertoa, mitkä mittaavat
  nopeutta ja mitkä vakautta.
- Osaat laskea mittarit julkaisuhistoriasta ja kertoa, mitä tietoja
  laskenta vaatii.
- Osaat näyttää esimerkillä, miten yksittäistä mittaria voi parantaa
  muuttamatta mitään todellista, ja miksi mittareita luetaan yhdessä.
- Osaat arvioida kyselytutkimukseen perustuvan tuloksen rajat ja
  erottaa yhteyden syystä.
- Osaat valita putken mittareita, jotka kertovat, missä aika kuluu.
