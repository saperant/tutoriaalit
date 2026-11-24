# Lokitus, havaitseminen ja poikkeamat

Kaikkia hyökkäyksiä ei voi estää. Siksi tietoturvassa on kolme
tehtävää: **estää** mitä voi, **havaita** mitä ei voinut estää, ja
**toipua** nopeasti. Havaitsemisen viive ratkaisee usein vahingon koon:
hyökkääjä, joka huomataan tunnissa, ehtii vähemmän kuin se, joka
huomataan kuukausien päästä ulkopuolisen ilmoituksesta.

## Mitä lokitetaan

Turvallisuuslokin tarkoitus on vastata jälkikäteen kysymyksiin kuka,
mitä, milloin, mistä ja onnistuiko. Vähintään nämä tapahtumat
lokitetaan:

- todennus: onnistuneet ja epäonnistuneet kirjautumiset, MFA:n ja
  salasanan muutokset, istuntojen päättymiset,
- valtuutus: kielletyt pääsyt ja oikeuksien muutokset,
- arvokkaan datan käsittely: viennit, massahaut, poistot,
- ylläpito: asetusten muutokset, käyttäjien luonti, palvelun
  käynnistys ja pysäytys,
- syötteen hylkäykset, jotka viittaavat hyökkäykseen.

Lokeihin ei kirjoiteta salasanoja, tunnisteita eikä tarpeettomia
henkilötietoja (luku *Salaisuudet ja tunnistetietojen vuodot*). Aika
kirjataan UTC:nä ja kellot synkronoidaan, muuten eri järjestelmien
tapahtumia ei voi asettaa järjestykseen.

**Rakenteiset lokit** (esimerkiksi JSON-rivit) ovat koneellisesti
haettavia, eikä syötteeseen upotettu rivinvaihto voi väärentää uutta
lokiriviä. Lokit lähetetään keskitettyyn palveluun, johon
sovelluspalvelimella ei ole poisto-oikeutta: hyökkääjä pyrkii
poistamaan jälkensä.

## Lokin eheys

Kun lokit säilytetään paikallisesti, muokkauksen voi tehdä
havaittavaksi **tiivisteketjulla**: jokainen rivi sisältää edellisen
rivin tiivisteen, joten rivin poistaminen tai muuttaminen katkaisee
ketjun:

```{.python tiedosto="esimerkit/11-lokiketju.py" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/11-lokiketju.odotettu"}
```

Ketju havaitsee muutokset, mutta ei estä hyökkääjää kirjoittamasta
koko lokia uudelleen alusta. Siksi viimeisimmän rivin tiiviste
tallennetaan säännöllisesti erilliseen paikkaan tai lokit lähetetään
reaaliajassa muualle. Sama periaate on versionhallinnan ja
lohkoketjujen perustana.

## Hyökkäysten tunnistaminen

Lokeista tunnistetaan tyypillisiä hyökkäyskuvioita säännöillä.
Kirjautumislokista löytyvät esimerkiksi arvaushyökkäys yhteen tiliin,
salasanaruiskutus moneen tiliin ja onnistunut kirjautuminen virheiden
jälkeen:

```{.python tiedosto="esimerkit/11-kirjautumiset.py" osa="tunnistus"}
```

```{.tuloste tiedosto="esimerkit/11-kirjautumiset.odotettu"}
```

Kriittisin hälytys on onnistuminen useiden virheiden jälkeen:
arvaushyökkäys on todennäköisesti onnistunut. Salasanaruiskutus ei
laukaise tilikohtaista hälytystä lainkaan, koska jokaiseen tiliin tulee
vain yksi virhe; se näkyy vain, kun tapahtumia tarkastellaan
osoitteittain. Tuotannossa sääntöjä ajetaan keskitetyssä
lokienhallinnassa (SIEM, *security information and event
management*), ja ne kuvataan usein MITRE ATT&CK -luokituksen
tekniikoina. Säännöt vaativat jatkuvaa säätöä: liian herkkä sääntö
hukuttaa oikeat hälytykset vääriin.

## Poikkeamien käsittely

**Tietoturvapoikkeama** (*incident*) on tapahtuma, joka vaarantaa
tietojen tai palvelujen luottamuksellisuuden, eheyden tai saatavuuden.
NISTin ohje SP 800-61 (versio 3, 2025) jäsentää käsittelyn osaksi
organisaation riskienhallintaa. Käytännön vaiheet ovat vakiintuneet:

1. **Valmistautuminen**: yhteystiedot, roolit, lokit ja varmuuskopiot
   ovat kunnossa ennen poikkeamaa. Toimintaohje on harjoiteltu.
2. **Havaitseminen ja analyysi**: onko kyse poikkeamasta, mitä on
   vaarantunut, kuinka laajasti. Aikajana kootaan heti.
3. **Rajaaminen**: leviäminen pysäytetään, esimerkiksi eristämällä kone
   verkosta tai mitätöimällä tunnukset. Todisteet säilytetään: kone
   eristetään, ei sammuteta, koska muistin sisältö katoaa.
4. **Poistaminen ja palautus**: hyökkääjän jalansija poistetaan,
   haavoittuvuus korjataan, ja palvelut palautetaan puhtaista
   varmuuskopioista. Kaikki salaisuudet, joihin hyökkääjä on voinut
   päästä, vaihdetaan.
5. **Jälkitarkastelu**: mitä tapahtui, miksi se oli mahdollista, miten
   havaitseminen ja vaste paranevat. Syyttelemätön (*blameless*)
   tarkastelu tuottaa rehellisempää tietoa.

Ilmoitusvelvollisuuksilla on tiukat määräajat (luku *Lainsäädäntö ja
etiikka*), joten oikeudellinen arvio aloitetaan heti analyysivaiheessa.

## Käytännössä

- **Lokita turvallisuustapahtumat rakenteisesti.** Kuka, mitä,
  milloin (UTC), mistä, tulos. Ei salaisuuksia.
- **Lokit pois hyökkääjän ulottuvilta.** Keskitetty tallennus, johon
  sovelluksella on vain kirjoitusoikeus, ja säilytysaika, joka riittää
  tutkintaan.
- **Hälytä toimenpiteitä vaativista asioista.** Hälytys, johon kukaan
  ei reagoi, on melua. Jokaisella säännöllä on omistaja ja
  toimintaohje.
- **Varmuuskopiot ovat viimeinen puolustuslinja.** Kiristyshaittaohjelma
  salaa myös verkkolevyt, joten vähintään yksi kopio on erillään
  verkosta tai muuttumattomana, ja palautus testataan.
- **Harjoittele.** Pöytäharjoitus, jossa käydään läpi kuviteltu
  poikkeama, paljastaa puuttuvat yhteystiedot ja oikeudet ennen
  todellista tilannetta.

## Itsearviointi

- Osaat luetella turvallisuustapahtumat, jotka sovelluksen on
  lokitettava, ja tiedot, joita lokeihin ei kirjoiteta.
- Osaat tunnistaa lokista arvaushyökkäyksen, salasanaruiskutuksen ja
  onnistuneen murron merkit.
- Osaat tehdä lokin muokkauksen havaittavaksi tiivisteketjulla ja
  kertoa sen rajat.
- Osaat kuvata poikkeaman käsittelyn vaiheet ja kertoa, miksi todisteet
  säilytetään ennen palautusta.
