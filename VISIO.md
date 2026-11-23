# Visio

Tutoriaalit on avoin, suomenkielinen oppimateriaalikokonaisuus
tekniikan osaajille. Se kokoaa ohjelmistojen, laitteistojen ja
järjestelmien osaamisen yhdeksi taitopuuksi, jonka jokaiseen taitoon on
tiivis, testattu ja heti käyttövalmis oppimateriaali.

## Miksi

**Oma ymmärrys ratkaisee.** Tekoälytyökalut tekevät yhä enemmän työtä
ihmisen puolesta. Jos oma osaaminen ei samalla kehity, ihmisen rooliksi
jää välittää pyyntöjä koneelle ja hyväksyä sen tuotoksia: hänestä tulee
pelkkä ihmisen ja koneen välinen rajapinta. Projektin tavoite on
osaaminen, jolla tekoälyä käytetään työkaluna eikä ajattelun
korvikkeena.

**Oppimisen kynnys on usein muualla kuin asiassa.** Aloittaminen
kaatuu helposti kehitysympäristön pystyttämiseen, hajanaiseen
aineistoon tai tuntien mittaisiin videokursseihin, joista olennainen on
kaivettava esiin itse.

**Suomenkielistä syventävää aineistoa on vähän.** Englanniksi
materiaalia on runsaasti. Suomeksi kirjoitettu, ajantasainen ja
syvälle menevä aineisto puuttuu useimmilta tekniikan alueilta.

## Kolme kokonaisuutta

| Kokonaisuus | Vastaa kysymykseen | Toteutus |
|--------------|------------------------------|------------------------------|
| Taitopuu | Mikä mahdollistaa minkäkin, ja mitä pitää hallita ennen seuraavaa? | [`opintopolut/taitopuu.toml`](opintopolut/taitopuu.toml) ja tarkistin |
| Roolit | Mitä tietyssä tehtävässä pitää osata? | roolit taitopuussa, roolipolut [opintopolut.pdf](opintopolut/opintopolut.pdf):ssä ja taitopuukartalla |
| Tutoriaalipaketit | Miten taidon oppii? | yksi hakemisto taitoa kohti: PDF, esimerkit ja kehityskontti |

**Taitopuu** on projektin runko. Jokainen taito on yksi rajattu
kokonaisuus, ja sille on merkitty taidot, jotka on hallittava ensin.
Taitopuusta näkee, mitä kukin taito vaatii ja mitä se avaa.

**Roolit** ovat näkymiä taitopuuhun. Rooli, kuten laitteistoarkkitehti
tai sulautettujen ohjelmistojen kehittäjä, määritellään muutamana
tavoitetaitona. Roolin osaamisvaatimukset ovat näiden tavoitteiden ja
kaikkien niiden esitietojen joukko. Valinnaiset syvennykset kertovat,
mihin osaamista voi laajentaa. Roolit eivät tuo uutta sisältöä, vaan
rajaavat taitopuusta tehtävän kannalta olennaisen osan.

**Tutoriaalipaketti** on yhden taidon oppimateriaali. Jokainen paketti
on oma kokonaisuutensa:

- **PDF**, jonka voi lukea alusta loppuun omaan tahtiin,
- **esimerkit**, jotka on käännetty, ajettu ja tarkistettu
  automaattisesti, sekä
- **kehityskontti**, jossa kaikki tarvittavat työkalut ovat valmiina:
  paikallisesti, GitHub Codespacesissa tai ladattavana pakettina.

Ohjelmointikieliä opettavat paketit noudattavat yhteistä runkoa
([`yhteiset/KIELIPAKETTI.md`](yhteiset/KIELIPAKETTI.md)), ja osaaminen
jakautuu niissä kolmeen tasoon: **perusteet**, **kokeneen kehittäjän
materiaali** (oma luku, pikaopas ja itsearvioinnit) sekä
**erityistarpeet**, kuten kehykset, kielten yhteiskäyttö ja
kielikohtainen suorituskyky, jotka ovat taitopuussa omia taitojaan.

## Kenelle

| Kohderyhmä | Tarve | Miten materiaali palvelee |
|----------------|----------------------|------------------------------------------|
| Opiskelijat ja harrastajat | Osaamisen rakentaminen alusta | Taitopuun ensimmäiset tasot eivät vaadi esitietoja. Polku etenee aina tunnetulta pohjalta, ja työkalut ovat valmiina. |
| Ammattilaiset | Uralla eteneminen, itsensä haastaminen ja osaamisen uudelleensuuntaaminen | Taitoon voi siirtyä suoraan. Kielipaketeissa on oma luku ja pikaopas kokeneelle, ja itsearvioinnit kertovat, mitkä luvut voi ohittaa. Roolipolut näyttävät, mitä uusi suunta vaatii. |
| Tiiminvetäjät | Alaisten osaamisen kehittäminen | Roolien osaamisvaatimukset antavat yhteisen kielen kehityskeskusteluihin. Polun voi jakaa linkkinä, ja laajuusarviot auttavat ajan suunnittelussa. |

## Periaatteet

1. **Matala kynnys, nouseva polku.** Jokaiseen taitoon pääsee
   esitietojen kautta, eikä mikään paketti oleta asioita, joita sen
   esitiedoissa ei opeteta. Kehitysympäristö on valmiina, joten
   ensimmäinen esimerkki on ajettavissa minuuteissa.
2. **Tiivis ja tehokas.** Ei tuntien videoita eikä täytetekstiä.
   Materiaali on ytimekästä tekstiä ja toimivia esimerkkejä, jotka voi
   käydä läpi omaan tahtiin. Yksi paketti on laajuudeltaan 2–5
   opintopistettä.
3. **Oikeita taitoja, ei "Hello, World" -materiaalia.** Esimerkit
   ratkaisevat tunnistettavia tehtäviä ja on kirjoitettu kuin
   tuotantokoodi. Jokainen luku kertoo, mitä malleja ja käytäntöjä
   ammattilaiset käyttävät ja miksi, sekä mitä asiat maksavat juuri
   tässä kielessä: samat mallit eivät siirry kielestä toiseen, kun
   esimerkiksi poikkeuksen hinta on täysin eri.
4. **Yksi jaottelu, ei toistoa.** Kukin asia opetetaan yhdessä
   paketissa. Muut paketit viittaavat siihen esitietona eivätkä toista
   sitä. Taitopuun tarkistin valvoo, ettei rakenteeseen synny syklejä
   eikä päällekkäisiä riippuvuuksia.
5. **Testattu.** Kaikki koodi käännetään ja ajetaan automaattisesti,
   ja tekstissä näkyvät tulosteet on todennettu. Työkalut ovat avointa
   lähdekoodia, jotta kuka tahansa voi toistaa testit.
6. **Suomeksi ja avoimesti.** Materiaali kirjoitetaan suomeksi.
   Vakiintuneet englanninkieliset termit mainitaan, jotta lukija löytää
   myös kansainvälisen aineiston. Kaikki on lisensoitu CC BY-SA 4.0
   -lisenssillä, ja lähteinä käytetään vain lisenssiltään yhteensopivaa
   aineistoa.
7. **Tekoäly tuottaa rakennetta ja todennettavaa sisältöä.** Tekoälyä
   käytetään tiiviin, ajantasaisen ja testatun materiaalin tuottamiseen:
   rakenteeseen, esimerkkeihin, testeihin ja tarkistuksiin, ei proosan
   paisuttamiseen. Ihmisen ja tekoälyn välistä työnjakoa voidaan
   muuttaa projektin resurssien mukaan.

## Rajaukset

- **Ei videokurssi.** Materiaali on luettavaa ja ajettavaa.
- **Ei hakuteos.** Paketit opettavat olennaisen ja viittaavat
  yksityiskohdissa alkuperäisiin lähteisiin, kuten standardeihin ja
  dokumentaatioon.
- **Ei käännös.** Englanninkielistä aineistoa käytetään lähteenä
  lisenssin salliessa, mutta sisältö kirjoitetaan alusta.
- **Ei tutkintoa.** Laajuudet on mitoitettu opintopisteinä
  vertailtavuuden vuoksi, mutta materiaali ei korvaa koulutusta eikä
  myönnä todistuksia.

## Kehityssuuntia

- Oman osaamisen merkitseminen taitopuukartalle: mitkä taidot ovat
  hallussa ja mitkä työn alla.
- Tiiminvetäjän näkymä, jossa tiimin osaaminen ja kehityspolut näkyvät
  rinnakkain.
- Harjoitustehtävät ja itsearviointi pakettien loppuun.
