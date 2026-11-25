# Skaalausmallit

Kun samaa tuotetta tekee kymmenen tai sata tiimiä, tiimien työ on
sovitettava yhteen. Tähän on tarjolla nimettyjä malleja, joista
tunnetuimmat ovat Scrum of Scrums, SAFe, LeSS ja niin sanottu
Spotify-malli. Tämä luku kertoo, mitä ongelmaa kukin ratkaisee, mitä
se maksaa ja mitä malleista tiedetään.

## Ongelma: riippuvuudet

Skaalausmallien ydinongelma on tiimien välinen riippuvuus. Jos
ominaisuus vaatii usean tiimin työn, se valmistuu vasta, kun
viimeinenkin tiimi on valmis. Oletetaan, että kukin tiimi saa osuutensa
valmiiksi sovitussa ajassa toisista riippumatta todennäköisyydellä $p$:

```{.python tiedosto="esimerkit/09-riippuvuudet.py" osa="todennakoisyys"}
```

```{.tuloste tiedosto="esimerkit/09-riippuvuudet.odotettu"}
```

Vaikka jokainen tiimi pitäisi aikataulunsa neljä kertaa viidestä,
viiden tiimin ominaisuus valmistuu ajallaan vain joka kolmannella
kerralla. Malli on yksinkertaistus, sillä todellisuudessa myöhästymiset
korreloivat ja tiimit auttavat toisiaan, mutta suunta pätee:
riippuvuuksien määrä tuhoaa ennustettavuuden nopeammin kuin
yksittäisen tiimin epävarmuus.

Tästä seuraa kaksi strategiaa. Riippuvuuksia voi **hallita**:
suunnitellaan yhdessä ja synkronoidaan aikataulut. Tai niitä voi
**poistaa**: muutetaan tiimien rajoja ja
arkkitehtuuria niin, että useimmat ominaisuudet mahtuvat yhteen
tiimiin (luvut 2–4). Skaalausmallit eroavat siinä, kumpaa ne painottavat.

## Scrum of Scrums

Kevyin malli on Jeff Sutherlandin 1990-luvulla kuvaama **Scrum of
Scrums**: jokaisesta tiimistä yksi edustaja osallistuu säännölliseen
lyhyeen kokoukseen, jossa käydään läpi tiimien väliset esteet ja
riippuvuudet. Malli ei muuta organisaatiota eikä vaadi uusia rooleja.
Se toimii muutamalle tiimille, joiden riippuvuudet ovat satunnaisia.
Kun tiimejä on paljon, kokous paisuu tilannekatsaukseksi, ja joka
viikko toistuvat riippuvuudet pitäisi poistaa eikä raportoida.

## SAFe

**Scaled Agile Framework** (Dean Leffingwell, 2011) on laajin ja
yritysmaailmassa käytetyin malli. Sen perusyksikkö on julkaisujuna
(*Agile Release Train*): 50–125 hengen joukko tiimejä, jotka
suunnittelevat ja toimittavat samassa tahdissa. Tahdin määrää
suunnittelujakso (*PI*), tyypillisesti 8–12 viikkoa. Jakson alussa
koko juna kokoontuu kahden päivän PI-suunnitteluun, jossa tiimit
sopivat tavoitteista ja tekevät riippuvuudet näkyviksi. Mallissa on
omat roolinsa sekä laajennukset suurten ratkaisujen ja portfolion
hallintaan.

SAFe valitsee riippuvuuksien hallinnan. Sen vahvuus on, että se antaa
suurelle organisaatiolle tutun näköisen rakenteen, yhteisen rytmin ja
tavan nähdä riippuvuudet etukäteen. Se sopii tilanteisiin, joissa
riippuvuuksia ei voi poistaa: laite ja ohjelmisto valmistuvat yhdessä,
tai sääntely vaatii koordinoidun julkaisun.

Kritiikki kohdistuu samaan asiaan. Malli on raskas: rooleja, tasoja
ja seremonioita on paljon, ja neljännesvuoden suunnittelujakso on
pitkä palautesilmukka verrattuna jatkuvaan toimitukseen. Monet ketterän
kehityksen varhaiset tekijät pitävät sitä vanhan ohjausrakenteen
uudelleennimeämisenä. Lisäksi malli tekee riippuvuuksista siedettäviä,
mikä vähentää painetta poistaa niitä.

## LeSS

**Large-Scale Scrum** (Craig Larman ja Bas Vodde) lähtee
vastakkaisesta suunnasta. Se on Scrum usealle tiimille: yksi
tuoteomistaja, yksi tuotejono, yhteinen sprintti ja yksi yhteinen
lisäys. Perusmuoto on tarkoitettu enintään noin kahdeksalle tiimille,
ja suuremmille on vaatimusalueisiin jaettu LeSS Huge. Tiimit ovat
ominaisuustiimejä (luku 3), jotka tekevät muutoksen koko koodikannan
läpi.

LeSS valitsee riippuvuuksien poistamisen. Koordinointirooleja ei
lisätä, vaan organisaatiota yksinkertaistetaan, ja tiimit sopivat
asioista keskenään. Hinta on,
että malli vaatii perustavia muutoksia: komponenttitiimit puretaan,
koodin omistajuus muuttuu yhteiseksi ja väliportaan rooleja poistuu.
Larman on itse todennut, että organisaatiot pyrkivät säilyttämään
nykyiset asemat ja valtarakenteet uusilla nimillä. Siksi LeSS on
helppo kuvata ja vaikea ottaa käyttöön.

## Spotify-malli

Henrik Kniberg ja Anders Ivarsson kuvasivat vuonna 2012, miten
Spotifyn kehitysorganisaatio oli silloin järjestetty. Kuvauksen
käsitteet levisivät laajalle:

| Käsite | Mitä tarkoittaa |
|----------|-----------------------------------------------------|
| squad | pieni itseohjautuva tiimi, jolla on oma tehtävä; vastaa virtatiimiä |
| tribe | samaan alueeseen liittyvien squadien joukko, alle sata henkeä |
| chapter | saman alan osaajat triben sisällä; chapterin vetäjä on heidän esihenkilönsä |
| guild | vapaaehtoinen käytäntöyhteisö koko yrityksen yli (luku 8) |

Rakenne on matriisi (luku 3), jossa painopiste on tuoteakselilla:
squad päättää, mitä tehdään, ja chapter huolehtii osaamisesta.

”Spotify-mallista” on hyvä tietää kolme asiaa. Kirjoittajat
korostivat itse, että kyse oli tilannekuvasta eikä mallista, ja että
rakenne muuttui jatkuvasti. Spotifyn entiset työntekijät ovat
sittemmin kertoneet, ettei yritys itsekään koskaan toiminut täysin
kuvauksen mukaan ja että erityisesti tiimien välinen yhteistyö ja
matriisin vastuunjako tuottivat ongelmia. Ja kuvaus on kirjoitettu
nopeasti kasvavan kuluttajatuotteen oloissa, joissa tiimien autonomia
oli tärkeämpää kuin yhtenäisyys. Nimien kopioiminen ei tuo mukanaan
edellytyksiä, joiden varassa alkuperäinen toimi.

## Vertailu

| Malli | Riippuvuudet | Uudet roolit | Vaatii organisaatiolta |
|--------------|----------------|----------------|-----------------------------|
| Scrum of Scrums | raportoidaan | ei | ei juuri mitään |
| SAFe | hallitaan yhteisellä suunnittelulla | paljon | sitoutumista prosessiin |
| LeSS | poistetaan rakenteella | ei, rooleja vähennetään | rakenteen purkamista |
| Spotify-kuvaus | vältetään autonomialla | chapterit, tribet | vahvaa kulttuuria |

## Mitä näytöstä tiedetään

Skaalausmallien vertailevaa tutkimusta on vähän. Dikertin,
Paasivaaran ja Lasseniuksen kirjallisuuskatsaus (2016) suurista
ketteristä muutoksista totesi, että valtaosa julkaistusta aineistosta
oli kokemusraportteja. Toistuvia haasteita olivat muutosvastarinta,
puuttuva koulutus ja mallin soveltaminen omiin oloihin. Mallien
toimittajien menestystarinat eivät ole riippumatonta näyttöä.

Vankin tulos on epäsuora. Toimituskyvyn tutkimus (*Accelerate*)
yhdistää hyvän suorituskyvyn löyhästi kytkettyyn arkkitehtuuriin ja
tiimeihin, jotka voivat testata ja julkaista työnsä muista
riippumatta. Tämä puoltaa riippuvuuksien poistamista aina, kun se on
mahdollista.

## Käytännössä

- **Älä skaalaa, jos ei ole pakko.** Kysy ensin, voiko tuotteen jakaa
  niin, että tiimit eivät tarvitse toisiaan.
- **Laske riippuvuudet.** Kuinka moni ominaisuus vaatii usean tiimin?
  Jos useimmat, ongelma on rakenteessa.
- **Mittaa lopputulosta.** Läpimenoaika ja julkaisutiheys ennen ja
  jälkeen kertovat, auttoiko malli. Koulutettujen määrä ei kerro.

## Itsearviointi

- Osaat laskea, miten usean tiimin riippuvuus heikentää
  ennustettavuutta.
- Osaat kuvata SAFen ja LeSSin periaatteet ja suhteen riippuvuuksiin.
- Osaat selittää Spotify-kuvauksen käsitteet ja arvioida mallien
  näytön.
