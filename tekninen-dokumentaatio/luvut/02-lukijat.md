# Lukijat ja dokumenttityypit

Dokumentin kirjoittaminen alkaa kahdesta kysymyksestä: kuka lukee ja
mitä hän yrittää tehdä. Vastaus määrää sisällön, järjestyksen ja jopa
sen, kirjoitetaanko dokumenttia lainkaan.

## Lukija ja hänen tehtävänsä

Lukija ei lue dokumentaatiota huvikseen. Hänellä on tehtävä kesken, ja
dokumentaatio on keskeytys. Tyypillisiä lukijoita ja heidän
kysymyksiään:

| Lukija | Kysymys | Mistä vastaus löytyy |
|------------------|--------------------------------|---------------------|
| arvioija | Sopiiko tämä tarpeeseeni? | README:n alku |
| uusi käyttäjä | Miten pääsen alkuun? | opas |
| kokenut käyttäjä | Miten teen asian X? | ohje |
| integroija | Mitä tämä funktio tarkalleen tekee? | viite |
| ylläpitäjä yöllä | Hälytys soi, mitä teen? | toimintaohje |
| uusi kehittäjä | Miksi tämä on tehty näin? | selitys, päätösloki |
| päivittäjä | Mikä muuttui ja hajoaako jokin? | muutosloki |

Sama ihminen on eri hetkinä eri lukija. Dokumentti, joka yrittää
palvella kaikkia kerralla, ei palvele ketään.

## Neljä dokumenttityyppiä

Daniele Procidan *Diátaxis*-malli jakaa dokumentaation neljään
tyyppiin kahden kysymyksen mukaan: opiskeleeko lukija vai tekeekö hän
työtä, ja tarvitseeko hän käytännön askeleita vai tietoa.

| Tyyppi | Lukija haluaa | Muoto | Kirjoittajan lupaus |
|----------|-----------------|-----------------------|--------------------------|
| opas (*tutorial*) | oppia | yksi valmis polku alusta loppuun | onnistut varmasti |
| ohje (*how-to*) | ratkaista ongelman | askeleet yhteen tavoitteeseen | pääset perille |
| viite (*reference*) | tarkistaa faktan | kattava, tasalaatuinen luettelo | tämä pitää paikkansa |
| selitys (*explanation*) | ymmärtää | perustelu, tausta, vaihtoehdot | tiedät miksi |

Tyypit eroavat sävyltäänkin. Opas ei selitä vaihtoehtoja, koska
aloittelija ei osaa valita. Ohje ei opeta perusteita, koska lukija
osaa ne. Viite ei perustele, koska lukija haluaa vain tarkistaa.
Selitys ei anna komentoja, koska sitä ei lueta näppäimistö käden alla.

Esimerkkikirjaston dokumentaation etusivu ohjaa lukijan oikeaan
tyyppiin hänen tilanteensa mukaan:

```{.rst tiedosto="esimerkit/sphinx/index.rst"}
```

## Mitä sekoittamisesta seuraa

Tavallisin dokumentaatiovika ei ole puuttuva tieto vaan väärässä
paikassa oleva tieto. Seuraava ohje on kirjoitettu yhdeltä istumalta,
ja siinä ovat kaikki neljä tyyppiä sekaisin:

```{.markdown tiedosto="esimerkit/naytteet/sekava-ohje.md"}
```

Ensimmäinen kappale on historiaa, eli selitystä, ja se on asennusta
etsivän lukijan tiellä. Toinen kappale on ohje, jossa ei ole askeleita,
viite ja linkki häiriötilanteeseen. Kolmas lupaa helppoutta eikä kerro
mitään. Korjaus ei ole kirjoittaa paremmin vaan jakaa: historia
selitykseen, asennus ohjeeksi, asetusten kentät viitteeseen ja
häiriötilanne omaan toimintaohjeeseensa. Kun jokainen sivu on yhtä
tyyppiä, lukija tietää mitä odottaa ja kirjoittaja tietää, mitä jättää
pois.

## Projektin vakiodokumentit

Joillakin dokumenteilla on vakiintunut nimi ja paikka repositorion
juuressa. Lukija etsii ne sieltä kysymättä.

**README** on projektin etuovi. Sen lukija päättää minuutissa, jatkaako
hän. Hyvä README vastaa järjestyksessä: mikä tämä on ja kenelle, miten
sitä kokeillaan, mistä löytyy lisää, ja millä ehdoilla sitä saa
käyttää.

```{.markdown tiedosto="esimerkit/dokumentit/README.md"}
```

README ei ole käsikirja. Kun se kasvaa yli parin ruudullisen, sisältö
siirretään varsinaiseen dokumentaatioon ja README:hen jää linkki.

**CONTRIBUTING** kertoo, miten muutos tehdään: miten ympäristö
pystytetään, mitkä tarkistukset ajetaan ja mitä katselmoija odottaa.
Se säästää ylläpitäjän aikaa enemmän kuin mikään muu dokumentti.

**CHANGELOG** eli muutosloki kertoo ihmiselle, mikä versioiden välillä
muuttui. Se ei ole commit-historia: historia kertoo, mitä koodille
tehtiin, muutosloki kertoo, mitä käyttäjän pitää tietää. *Keep a
Changelog* -käytännössä uusin versio on ylimpänä, jokaisella versiolla
on päivämäärä ja muutokset ryhmitellään tyypin mukaan:

```{.markdown tiedosto="esimerkit/dokumentit/CHANGELOG.md"}
```

Osio *Julkaisematon* kerää muutokset sitä mukaa kuin ne tehdään, joten
julkaisupäivänä lokia ei tarvitse kaivaa historiasta. Ryhmä
*Vanhentunut* on semanttisen versioinnin kannalta tärkein: se kertoo
etukäteen, mikä seuraavassa pääversiossa hajoaa. Versionumeroiden
merkitys on käsitelty taidossa *Versionhallinta (Git)*. Esimerkkien
tarkistin `tyokalut/muutosloki.py` varmistaa rakenteen ja sen, että
lokin uusin versio on sama kuin paketin versio.

**Toimintaohje** (*runbook*) on ohje häiriötilanteeseen. Sen lukija on
väsynyt ja kiireinen, joten rakenne on aina sama: mistä hälytys
tulee, miten tilanne tarkistetaan, miten se korjataan, miten korjaus
varmistetaan ja kenelle soitetaan, jos ohje ei auta.

```{.markdown tiedosto="esimerkit/dokumentit/kayttoohjeet/levy-taynna.md"}
```

Komennot ovat kopioitavissa sellaisinaan, ja vaarallinen toimenpide on
kielletty erikseen. Toimintaohje, jota ei ole koskaan kokeiltu, on
arvaus: se ajetaan läpi harjoituksessa ja päivitetään jokaisen oikean
häiriön jälkeen.

## Käytännössä

- **Kirjoita lukijan kysymys sivun alkuun, vaikka poistaisit sen
  lopuksi.** Jos kysymystä ei osaa sanoa, sivulla ei ole tehtävää.
- **Yksi sivu, yksi tyyppi.** Kun oppaaseen tekee mieli lisätä
  taustaa, lisää linkki selitykseen.
- **Viite generoidaan, muut kirjoitetaan.** Viitteen pitää olla
  kattava ja ajan tasalla, mihin kone pystyy. Opasta, ohjetta ja
  selitystä kone ei osaa kirjoittaa, koska ne vaativat valintoja.
- **Älä dokumentoi sitä, minkä voi korjata.** Jos asennus vaatii
  kymmenen askeleen ohjeen, parempi dokumentaatio on skripti.
- **Opas on kallein ylläpitää.** Sen jokaisen askeleen on toimittava
  jokaisessa versiossa, joten pidä se lyhyenä ja aja se testinä
  (luku 5).
- **Muutosloki kirjoitetaan muutoksen yhteydessä.** Julkaisupäivänä
  kukaan ei muista, miksi muutos tehtiin.

## Itsearviointi

- Osaat nimetä dokumentin lukijan ja kysymyksen, johon se vastaa.
- Osaat luokitella sivun oppaaksi, ohjeeksi, viitteeksi tai
  selitykseksi ja kertoa, mikä siihen ei kuulu.
- Osaat jakaa sekavan dokumentin tyyppien mukaisiin osiin.
- Osaat kirjoittaa README:n, muutoslokin ja toimintaohjeen
  vakiintuneella rakenteella.
