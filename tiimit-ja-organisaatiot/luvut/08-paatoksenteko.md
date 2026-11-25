# Päätöksenteko ja arkkitehtuurityö

Itsenäinen tiimi tekee päätöksiä itse. Jotkin päätökset koskevat
kuitenkin useaa tiimiä: yhteinen tapahtumamuoto, tunnistautuminen,
ohjelmointikielten kirjo. Tämä luku käsittelee, kuka tällaiset
päätökset tekee, kuinka kauan ne saavat kestää ja miten ne kirjataan.

## Autonomian ja yhtenäisyyden jännite

Täysi autonomia tuottaa kymmenen tapaa tehdä sama asia: jokainen
tiimi on nopea yksin, mutta ihmisten siirtyminen tiimistä toiseen,
yhteinen päivystys ja tietoturvan valvonta vaikeutuvat. Täysi
yhtenäisyys tuottaa keskitetyn päätöksentekijän, jonka jonossa kaikki
odottavat. Kumpikaan ääripää ei toimi, joten kysymys on, mitkä asiat
yhtenäistetään.

Hyödyllinen jako on päätöksen peruttavuus. Helposti peruttava päätös
(kirjasto yhden palvelun sisällä) kannattaa tehdä nopeasti lähellä
työtä. Vaikeasti peruttava (tietokanta, julkinen rajapinta,
tapahtumamuoto) ansaitsee laajemman harkinnan. Lisäksi yhtenäistetään
yleensä se, mikä näkyy tiimien välillä: rajapintojen tyyli, valvonta,
tunnistautuminen ja julkaisutapa. Tiimin sisäiset asiat jätetään
tiimille.

## Arkkitehdin rooli

Arkkitehdin asema vaihtelee organisaatiomallin mukaan.

| Malli | Kuka päättää | Vahvuus | Riski |
|-------------------|------------------|-----------------|--------------------|
| arkkitehtuuriryhmä hyväksyy | keskitetty ryhmä | yhtenäisyys | jono, etäisyys koodista |
| arkkitehti tiimissä | tiimi | päätös lähellä työtä | hajanaisuus |
| neuvonantoprosessi | tekijä, kuultuaan muita | nopeus ja laaja näkemys | vaatii kypsyyttä ja kirjaamista |

Brooks korosti jo 1975 **käsitteellistä eheyttä**: järjestelmä on
helpompi käyttää ja ylläpitää, kun se heijastaa yhtä suunnitteluajatusta.
Hänen ratkaisunsa oli pieni joukko arkkitehteja, jotka päättävät.
Vastaväite on, että koodista etääntynyt arkkitehti päättää
vanhentuneilla tiedoilla ja että päätökset, joita tekijät eivät
ymmärrä, kierretään. Gregor Hohpen vertaus on hissi: arkkitehdin työ
on kulkea johdon kerroksen ja konehuoneen väliä ja kääntää asioita
kumpaankin suuntaan, ei asettua yhteen kerrokseen.

## Keskitetyn hyväksynnän hinta

Kuvitellaan, että useaa tiimiä koskevia päätöksiä syntyy keskimäärin
kolme viikossa. Arkkitehtuuriryhmä kokoontuu määrävälein ja ehtii
käsitellä rajallisen määrän asioita kerralla:

```{.python tiedosto="esimerkit/08-paatokset.py" osa="ryhma"}
```

```{.tuloste tiedosto="esimerkit/08-paatokset.odotettu"}
```

Kahden viikon välein kokoontuva ryhmä, joka käsittelee viisi asiaa
kerralla, saa asioita hieman enemmän kuin ehtii käsitellä. Jono kasvaa
koko vuoden, ja päätöstä odotetaan keskimäärin neljä viikkoa. Sama
ryhmä kahdeksan asian kapasiteetilla pysyy tahdissa, mutta odotus on
silti keskimäärin viikko, koska asia odottaa seuraavaa kokousta. Tämä
on luvun 3 ottoväli päätöksiin sovellettuna: odotus tulee
kokoontumisvälistä ja kuormitusasteesta.

Viikoittainen kokous lyhentää odotuksen muutamaan päivään. Vielä
lyhyempi se on, jos päätöstä ei tarvitse viedä kokoukseen lainkaan.

## Neuvonantoprosessi

**Neuvonantoprosessissa** (*advice process*) kuka tahansa saa tehdä
päätöksen, kunhan hän ensin pyytää neuvoa kahdelta ryhmältä: niiltä,
joihin päätös vaikuttaa, ja niiltä, joilla on asiasta osaamista.
Neuvoa ei tarvitse noudattaa, mutta se on kuultava ja kirjattava.
Päätöksen tekijä vastaa päätöksestä. Frederic Laloux kuvasi käytännön
kirjassaan *Reinventing Organizations*, ja Andrew Harmel-Law on
soveltanut sitä ohjelmistoarkkitehtuuriin.

```{.dot otsikko="Neuvonantoprosessi: päätöksen tekee se, jota asia koskee, mutta vasta kuultuaan muita"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.4;
  tarve [label="tarve\npäätökselle"];
  luonnos [label="luonnos\n(ADR tai RFC)"];
  neuvo [label="neuvot:\nne, joihin vaikuttaa,\nja asiantuntijat"];
  paatos [label="tekijä päättää\nja kirjaa perustelut"];
  tarve -> luonnos -> neuvo -> paatos;
  neuvo -> luonnos [label="muutokset", style=dashed, constraint=false];
}
```

Edellisen esimerkin viimeinen rivi kuvaa tätä: jos kommentointiaika on
kolme työpäivää, jokainen päätös syntyy kolmessa päivässä eikä jonoa
ole, koska päätökset eivät kulje yhden ryhmän kautta.

Prosessin edut ovat nopeus ja se, että päätös tehdään siellä, missä
tieto on. Sen edellytykset on syytä sanoa ääneen.

- Päätökset kirjataan niin, että muut löytävät ne. Ilman kirjausta
  prosessi on vain ”jokainen tekee mitä haluaa”.
- Neuvon pyytäminen on velvollisuus, ei kohteliaisuus. Joku seuraa,
  että se tapahtuu.
- Arkkitehdit siirtyvät päättäjistä neuvonantajiksi, jotka pitävät
  yllä periaatteita ja kokonaiskuvaa. Rooli muuttuu, ei katoa.
- Tekijöiltä vaaditaan harkintaa tunnistaa, milloin päätös koskee
  muita. Kokematon organisaatio voi tarvita aluksi tiukempia rajoja.

Prosessi ei myöskään takaa yhtenäisyyttä. Siksi sen rinnalle sovitaan
yleensä muutama sitova periaate ja tuettu oletuspolku (luku 6).

## Päätösten kirjaaminen

Kaksi kevyttä muotoa on vakiintunut.

**Arkkitehtuuripäätöksen kirjaus** (*architecture decision record*,
ADR) on Michael Nygardin vuonna 2011 esittämä lyhyt dokumentti:
konteksti, päätös ja seuraukset, sekä tila (ehdotettu, hyväksytty,
korvattu). Kirjaukset säilytetään koodin vieressä versionhallinnassa.
Niiden arvo on perusteluissa: vuoden päästä joku kysyy, miksi näin
tehtiin, ja vastaus löytyy.

**Kommentointipyyntö** (*request for comments*, RFC) on ehdotus, joka
julkaistaan kommentoitavaksi ennen päätöstä. Nimi tulee internetin
standardointiprosessista, ja monet avoimen lähdekoodin projektit ja
yritykset käyttävät samaa mallia. RFC sopii neuvonantoprosessin
välineeksi: kommentointiaika on sovittu, ja lopuksi tekijä kirjaa
päätöksen.

Mallipohjat ja kirjoittaminen käsitellään taidossa *Tekninen
dokumentaatio*.

## Killat ja käytäntöyhteisöt

Kun osaajat on jaettu virtatiimeihin, saman alan ihmiset eivät enää
istu yhdessä. **Käytäntöyhteisö** (*community of practice*), jota
ohjelmistoyrityksissä kutsutaan usein killaksi, kokoaa heidät tiimien
yli: testaajat, tietokantaosaajat, käyttöliittymäkehittäjät. Etienne
Wengerin kuvaama käytäntöyhteisö on vapaaehtoinen ja perustuu yhteiseen
kiinnostukseen. Kilta jakaa osaamista, ylläpitää yhteisiä ohjeita ja
on luonteva paikka pyytää neuvoa.

Killan heikkous on sama kuin sen vahvuus. Vapaaehtoinen yhteisö
toimii niin kauan kuin joku jaksaa vetää sitä, eikä se voi päättää
kenenkään puolesta. Jos killalta odotetaan sitovia standardeja, sille
on annettava aikaa ja valtuudet.

## Käytännössä

- **Luokittele päätökset.** Peruttavat tiimille, vaikeasti peruttavat
  ja tiimien väliset laajempaan käsittelyyn. Kirjoita jako näkyviin.
- **Mittaa päätöksen läpimenoaika.** Jos tiimit odottavat hyväksyntää
  viikkoja, ne alkavat kiertää prosessia.
- **Kirjaa perustelut, älä vain lopputulosta.** ADR, jossa lukee
  ”käytämme PostgreSQL:ää”, on hyödytön. Hyödyllinen kertoo, mitä
  vaihtoehtoja oli ja miksi ne hylättiin.
- **Pidä sitovat periaatteet harvoina.** Kymmenen periaatetta
  muistetaan, sata ei.
- **Pidä arkkitehdit lähellä koodia.** Arkkitehti, joka ei ole
  nähnyt tuotantohäiriötä vuoteen, antaa huonompia neuvoja.

## Itsearviointi

- Osaat kuvata autonomian ja yhtenäisyyden jännitteen ja valita, mitkä
  asiat kannattaa yhtenäistää.
- Osaat verrata keskitettyä hyväksyntää, tiimin omaa päätösvaltaa ja
  neuvonantoprosessia.
- Osaat selittää, miksi määrävälein kokoontuva hyväksyntäryhmä
  tuottaa odotusta, ja arvioida sen suuruuden.
- Osaat kuvata neuvonantoprosessin vaiheet ja edellytykset.
- Osaat kertoa, mitä ADR ja RFC sisältävät ja mihin killat sopivat.
