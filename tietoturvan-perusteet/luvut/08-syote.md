# Syöte, polut ja sarjallistus

Kaikki luottamusrajan yli tuleva data on hyökkääjän hallinnassa:
lomakkeet, otsakkeet, evästeet, ladatut tiedostot, toisten palvelujen
vastaukset ja tiedostojärjestelmän nimet. Tämä luku käsittelee kolmea
virheluokkaa, jotka syntyvät, kun tällaiseen dataan luotetaan:
polkujen ohitus, turvaton deserialisointi ja vahvistamaton syöte.
Lopuksi luodaan yleiskatsaus muistivirheisiin, joita Pythonissa ei
synny mutta jotka ovat C- ja C++-ohjelmien vakavin virheluokka.

## Polkujen ohitus

Palvelu antaa ladata tiedostoja hakemistosta, ja tiedoston nimi tulee
pyynnöstä:

```{.python tiedosto="esimerkit/08-polku.py" osa="haavoittuva"}
```

Nimi `../salaisuudet.env` osoittaa hakemiston ulkopuolelle, ja
absoluuttinen polku korvaa juuren kokonaan, koska `Path("/a") /
"/etc/passwd"` on `/etc/passwd`. Korjauksessa polku ensin
**kanonisoidaan** (`resolve` purkaa `..`-osat ja symboliset linkit) ja
vasta sitten tarkistetaan, että tulos on sallitun hakemiston sisällä:

```{.python tiedosto="esimerkit/08-polku.py" osa="korjattu"}
```

```{.tuloste tiedosto="esimerkit/08-polku.odotettu"}
```

Järjestys on olennainen: merkkijonon tarkistaminen ennen kanonisointia
(`".." not in nimi`) jättää aukkoja, kuten URL-koodatut `%2e%2e`,
symboliset linkit ja Windowsin `..\`. Vielä turvallisempaa on olla
käyttämättä käyttäjän nimeä polkuna lainkaan: tiedostot tallennetaan
satunnaisella tunnisteella, ja alkuperäinen nimi pidetään tietokannassa.

## Turvaton deserialisointi

Sarjallistus (*serialization*) muuttaa olion tavuiksi tallennusta tai
siirtoa varten. Monet sarjallistusmuodot, kuten Pythonin `pickle`,
Javan sarjallistus ja YAML:n täysi muoto, voivat kuvata olion lisäksi
sen, *miten* olio rakennetaan, eli mitä funktiota kutsutaan
latauksessa. Hyökkääjän tekemä data suorittaa silloin hyökkääjän
koodia:

```{.python tiedosto="esimerkit/08-sarjallistus.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/08-sarjallistus.odotettu"}
```

Tuloste syntyy jo `pickle.loads`-kutsussa, ennen kuin ohjelma ehtii
tarkistaa mitään. Esimerkki kutsuu harmitonta `print`-funktiota; oikea
hyökkäys kutsuisi esimerkiksi `os.system`. Korjaus on käyttää
luottamuksellisen datan siirtoon muotoa, joka kuvaa vain dataa (JSON),
ja tarkistaa rakenne ennen käyttöä:

```{.python tiedosto="esimerkit/08-sarjallistus.py" osa="korjattu"}
```

`pickle` on turvallinen vain datalle, jonka oma ohjelma on itse
kirjoittanut paikkaan, johon kenelläkään muulla ei ole
kirjoitusoikeutta. Evästeet, välimuistit, viestijonot ja ladatut
tiedostot eivät täytä tätä ehtoa. YAML luetaan funktiolla
`yaml.safe_load`, ei `yaml.load`.

## Syöte jäsennetään reunalla

Syötteen käsittelyn kestävin malli on **jäsentää, ei vain validoida**
(*parse, don't validate*): ohjelman reunalla raakasyöte muutetaan
tyypitetyksi arvoksi, joka on olemassa vain, jos kaikki ehdot
täyttyvät. Sisempi koodi käsittelee vain `Tilausrivi`-olioita eikä
koskaan raakoja sanakirjoja, joten se ei voi unohtaa tarkistusta:

```{.python tiedosto="esimerkit/08-validointi.py" osa="jasennys"}
```

```{.tuloste tiedosto="esimerkit/08-validointi.odotettu"}
```

Esimerkissä näkyy viisi tapaa, joilla tarkistus usein pettää:

1. **Koko ensin.** Raja tarkistetaan ennen jäsennystä. Muuten
   hyökkääjä voi syöttää valtavan tai syvästi sisäkkäisen rakenteen,
   jonka käsittely kuluttaa muistin tai suoritinajan (palvelunesto).
2. **Sallitut arvot, ei kielletyt.** Tuotekoodi tarkistetaan
   säännöllisellä lausekkeella, joka kuvaa kelvollisen muodon
   kokonaan (`fullmatch`, ei `match`, joka hyväksyisi loppuun
   mitä tahansa).
3. **Arvoalueet.** Negatiivinen määrä on klassinen
   liiketoimintalogiikan virhe: se voi kääntää hyvityksen
   veloitukseksi.
4. **Tyyppien yllätykset.** JSONin `true` on Pythonissa `True`, joka on
   `int`:n alityyppi. Ilman erillistä tarkistusta se hyväksyttäisiin
   määräksi 1.
5. **Ylimääräiset kentät hylätään.** Asiakkaan lähettämä `hinta`
   ei saa päätyä tilaukseen. Tämä torjuu *mass assignment*
   -haavoittuvuuden, jossa hyökkääjä asettaa kenttiä, joita lomakkeella
   ei ole, kuten `rooli` tai `hinta`.

Virheilmoitus on käyttäjälle hyödyllinen mutta lyhyt: se ei toista
pitkää syötettä kokonaan (`!r:.20`) eikä paljasta sisäistä rakennetta,
kuten pinojälkeä tai SQL-lausetta.

## Muistiturvallisuus lyhyesti

Tämän tutoriaalin esimerkit ovat Pythonia, jossa yksi vakava
virheluokka ei voi syntyä: muistivirheet. C:ssä ja C++:ssa ohjelma
käsittelee muistia suoraan, eikä kieli tarkista, pysyykö käsittely
varatun alueen sisällä.

| Virhe | Mitä tapahtuu | Seuraus |
|-------|---------------|---------|
| puskurin ylivuoto (*buffer overflow*) | syöte on pidempi kuin sille varattu tila, ja kirjoitus jatkuu viereiseen muistiin | viereinen data tai paluuosoite muuttuu |
| luku rajojen ulkopuolelta | ohjelma lukee enemmän kuin puskurissa on | muistissa olleet salaisuudet vuotavat (Heartbleed 2014) |
| käyttö vapautuksen jälkeen (*use after free*) | osoitin viittaa muistiin, joka on jo annettu toiseen käyttöön | hyökkääjän data tulkitaan ohjelman omaksi rakenteeksi |

Kaikissa syy on sama kuin tämän luvun muissa virheissä: syötteen
pituuteen tai sisältöön luotetaan tarkistamatta. Seuraus on vakavampi,
koska hyökkääjä voi pahimmillaan ohjata ohjelman suorituksen
haluamaansa koodiin. Microsoft ja Chromium-projekti ovat kumpikin
raportoineet, että noin 70 prosenttia niiden vakavista
haavoittuvuuksista on ollut muistivirheitä.

**Muistiturvallinen kieli** poistaa koko luokan. Python, Java, Go ja
C# tarkistavat jokaisen taulukkoviittauksen rajat ja vapauttavat
muistin roskienkeruulla; Rust tekee saman käännösaikaisilla
omistussäännöillä ilman roskienkeruuta. Siksi viranomaisohjeet (muun
muassa Yhdysvaltain CISA) suosittelevat uuteen koodiin
muistiturvallista kieltä. Sama Python-rivi, joka C:ssä kirjoittaisi
puskurin yli, päättyy poikkeukseen `IndexError`.

Suoja ei ulotu C:llä kirjoitettuihin osiin: kuvankäsittely-,
pakkaus- ja jäsennyskirjastot Python-ohjelman alla ovat usein C:tä, ja
niiden haavoittuvuudet ovat myös Python-palvelun haavoittuvuuksia.
Kirjastot pidetään ajan tasalla (taito *Tietoturva kehitystyössä*).
Kun C:tä tai C++:aa on kirjoitettava itse, virheitä torjutaan
kääntäjän varoituksilla, sanitoijilla, fuzzauksella ja käyttöjärjestelmän
suojauksilla. Ne opetetaan taidossa *Haavoittuvuuksien analyysi ja
torjunta*.

## Käytännössä

- **Kaikki luottamusrajan yli tuleva on syötettä.** Myös otsakkeet,
  evästeet, tiedostonimet, toisten palvelujen vastaukset ja
  tietokannasta luettu data, jonka joku muu on kirjoittanut.
- **Jäsennä reunalla tyypitetyksi arvoksi.** Yksi paikka, jossa
  tarkistus tehdään, ja tyypit, jotka pakottavat käyttämään sitä.
- **Kanonisoi ennen tarkistusta.** Polut, URL-osoitteet ja Unicode
  normalisoidaan ensin, ja vasta lopputulos tarkistetaan.
- **Ei koodia suorittavia sarjallistusmuotoja ulkoiselle datalle.**
  JSON tai protokollapuskurit; `pickle` ja vastaavat vain omalle,
  suojatulle datalle.
- **Rajoita kokoa, syvyyttä ja määrää.** Pyynnön koko, listan pituus,
  sisäkkäisyys, ladatun tiedoston koko ja pakatun tiedoston purettu
  koko.
- **Validointi selaimessa on käytettävyyttä.** Tietoturvatarkistus
  tehdään aina palvelimella.

## Itsearviointi

- Osaat torjua polkujen ohituksen kanonisoimalla polun ennen
  tarkistusta.
- Osaat selittää, miksi `pickle`-datan lataaminen ulkoisesta lähteestä
  on koodin suoritusta, ja valita turvallisen sarjallistusmuodon.
- Osaat kirjoittaa jäsentimen, joka hylkää liian suuret, väärän
  tyyppiset ja ylimääräisiä kenttiä sisältävät syötteet.
- Osaat perustella, miksi sallittujen arvojen lista on parempi kuin
  kiellettyjen lista.
- Osaat selittää, mitä puskurin ylivuoto ja käyttö vapautuksen jälkeen
  ovat ja miksi muistiturvallinen kieli poistaa ne.
