# Salasanat ja tunnusten arvailu

Salasana on edelleen yleisin tunnistustapa ja yleisin murron syy:
vuotaneet salasanat, uudelleenkäyttö ja arvailu. Tämä luku käy läpi
salasanojen tallennuksen, käytännön, vuotaneiden salasanojen
tarkistuksen ja kirjautumisen suojauksen arvailulta.

## Tallennus

Salasanasta tallennetaan **hidas, suolattu tiiviste**. Tavallinen
tiivistefunktio (SHA-256) ei kelpaa, koska se on suunniteltu nopeaksi:
näytönohjain laskee miljardeja SHA-256-tiivisteitä sekunnissa.
Salasanatiivisteet (Argon2id, scrypt, bcrypt, PBKDF2) ovat
tarkoituksella hitaita, ja Argon2id ja scrypt vaativat lisäksi
paljon muistia, mikä tekee rinnakkaisesta arvaamisesta kallista.

```{.typescript tiedosto="esimerkit/src/06-salasanat/salasanat.ts" osa="tiiviste"}
```

Esimerkki käyttää Noden sisäänrakennettua scryptiä. OWASP suosittaa
ensisijaisesti Argon2id:tä (esimerkiksi `@node-rs/argon2`-paketti);
algoritmeja verrataan tarkemmin taidossa *Kryptografia*. Parametrit
tallennetaan tiivisteen mukana, jotta niitä voi kasvattaa
laitteiston kehittyessä: kirjautumisen yhteydessä vanha tiiviste
lasketaan uudelleen uusilla parametreilla.

## Käytäntö

NIST:n ohje SP 800-63B (versio 4) muutti salasanakäytännöt
perusteellisesti, koska vanhat säännöt tuottivat ennustettavia
salasanoja (`Kesä2026!`):

```{.typescript tiedosto="esimerkit/src/06-salasanat/salasanat.ts" osa="kaytanto"}
```

| Vanha käytäntö | Nykyinen suositus |
|----------------|-------------------|
| 8 merkkiä, isot, pienet, numerot, erikoismerkit | vähintään 15 merkkiä (8, jos osa monivaiheista tunnistusta); ei merkkiluokkia |
| vaihto 90 päivän välein | vaihto vain, jos vuoto epäillään |
| salasanavihje, turvakysymykset | ei lainkaan |
| liittäminen estetty | salli liittäminen ja salasanamanagerit |
| enimmäispituus 16 | vähintään 64 merkkiä sallittava |
| — | vuotaneet ja yleiset salasanat estetään |

```{.typescript tiedosto="esimerkit/src/06-salasanat/salasanat.test.ts" osa="kaytanto-testi"}
```

## Vuotaneiden salasanojen tarkistus

Palvelu kuten *Have I Been Pwned* tuntee miljardeja vuotaneita
salasanoja. Salasanaa tai sen tiivistettä ei tietenkään lähetetä
ulkopuoliselle palvelulle. **k-anonymiteetti** ratkaisee ongelman:
asiakas lähettää tiivisteestä vain viisi ensimmäistä merkkiä, ja
palvelu palauttaa kaikki samalla etuliitteellä alkavat tiivisteet
(satoja). Vertailu tehdään asiakkaassa.

```{.typescript tiedosto="esimerkit/src/06-salasanat/salasanat.ts" osa="kanonymiteetti"}
```

## Käyttäjätunnusten arvailu

Kirjautuminen paljastaa usein, onko tunnus olemassa: eri
virheilmoitus ("tuntematon käyttäjä" / "väärä salasana") tai eri
vastausaika, kun tiivistettä ei lasketa tuntemattomalle tunnukselle.
Hyökkääjä kokoaa näin listan oikeista tunnuksista kohdennettua
kalastelua tai arvailua varten.

```{.typescript tiedosto="esimerkit/src/06-salasanat/kirjautuminen.ts" osa="haavoittuva"}
```

```{.typescript tiedosto="esimerkit/src/06-salasanat/kirjautuminen.ts" osa="korjattu"}
```

Sama koskee rekisteröitymistä ja salasanan palautusta: "Jos tunnus on
olemassa, lähetimme ohjeet sähköpostiin" kaikille syötteille.

## Nopeusrajoitus

Arvailua on kolmea lajia: yhden tilin salasanan arvaaminen
(*brute force*), yhden yleisen salasanan kokeilu tuhansille tileille
(*password spraying*) ja vuotaneiden tunnus–salasana-parien kokeilu
(*credential stuffing*). Rajoitus tarvitaan siksi sekä tiliä että
lähdeosoitetta kohden. Esimerkissä on merkkiämpäri:

```{.typescript tiedosto="esimerkit/src/06-salasanat/kirjautuminen.ts" osa="rajoitin"}
```

```{.typescript tiedosto="esimerkit/src/06-salasanat/salasanat.test.ts" osa="rajoitus"}
```

Tilin lukitseminen pysyvästi tietyn yritysmäärän jälkeen on huono
ratkaisu: hyökkääjä voi lukita minkä tahansa tilin
(palvelunestohyökkäys). Kasvava viive ja väliaikainen rajoitus ovat
parempia. Lisäksi monivaiheinen tunnistus (luku 7) tekee arvatusta
salasanasta lähes hyödyttömän.

## Käytännössä

- **Argon2id tai scrypt** kirjastolla, parametrit tiivisteen mukana.
  Ei omaa "suolaa ja SHA-256:ta".
- **Pituus, ei monimutkaisuus.** Estä yleiset ja vuotaneet salasanat,
  salli pitkät salalauseet ja salasanamanagerit.
- **Sama vastaus ja sama työ** kaikille epäonnistuneille
  kirjautumisille.
- **Rajoita tiliä ja lähdettä kohden**, mieluummin kasvavalla
  viiveellä kuin pysyvällä lukituksella. Kirjaa epäonnistuneet
  yritykset ja hälytä poikkeamista (*Tietoturvan perusteet*).
- **Hinta:** hidas tiiviste maksaa palvelimelle saman kuin
  hyökkääjälle, esimerkiksi 50 ms prosessoriaikaa ja 32 Mt muistia
  kirjautumista kohden. Parametrit mitoitetaan kirjautumisten
  huippukuorman mukaan, ja kirjautumisen nopeusrajoitus suojaa myös
  palvelinta.

## Itsearviointi

- Osaat tallentaa salasanan hitaalla, suolatulla tiivisteellä ja
  selittää, miksi SHA-256 ei kelpaa.
- Osaat perustella nykyiset salasanakäytännöt NIST:n ohjeen mukaan.
- Osaat selittää k-anonymiteettiin perustuvan vuototarkistuksen.
- Osaat estää käyttäjätunnusten arvailun viesteistä ja vastausajoista.
- Osaat toteuttaa nopeusrajoituksen tiliä ja lähdettä kohden.
