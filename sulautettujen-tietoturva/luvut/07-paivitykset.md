# Laiteohjelmiston päivitykset

Jokaisessa ohjelmistossa on haavoittuvuuksia, joten laite, jota ei voi
päivittää, on ajan myötä haavoittuva. EU:n kyberkestävyyssäädös
vaatii tietoturvapäivitykset koko tukiajan (luku 11). Päivitys on
kuitenkin myös laitteen riskialttein hetki: kesken jäänyt kirjoitus
voi tehdä laitteesta toimimattoman, ja päivityskanava on hyökkääjälle
suora tie laitteeseen. Turvallinen päivitys täyttää kolme vaatimusta:

1. **Aitous**: laite asentaa vain valmistajan allekirjoittamia
   kuvia, jotka on tarkoitettu juuri sille.
2. **Ajantasaisuus**: vanhaa kuvaa ei voi asentaa uudelleen (luku 4).
3. **Kestävyys**: sähkökatko tai viallinen versio ei riko laitetta.

## Kestävyys sähkökatkoa vastaan

Flash kirjoitetaan lohko kerrallaan, ja katko voi tulla minkä tahansa
kirjoituksen jälkeen. Yksinkertaisin menetelmä pyyhkii vanhan kuvan
ja kirjoittaa uuden sen tilalle:

```{.python tiedosto="esimerkit/07-ab-paivitys.py" osa="paikallaan"}
```

A/B-menetelmässä on kaksi paikkaa. Uusi kuva kirjoitetaan
passiiviseen paikkaan, ja vasta kun se on kokonaan kirjoitettu ja
tarkistettu, se merkitään yhdellä atomisella kirjoituksella
kokeiltavaksi:

```{.python tiedosto="esimerkit/07-ab-paivitys.py" osa="ab"}
```

Käynnistin käynnistää kokeilukuvan rajallisen määrän kertoja. Jos
sovellus ei vahvista itseään toimivaksi, esimerkiksi koska se
kaatuu ennen yhteyttä palvelimeen, käynnistin palaa vanhaan kuvaan:

```{.python tiedosto="esimerkit/07-ab-paivitys.py" osa="kaynnistin"}
```

Ohjelma kokeilee katkoa jokaisen kirjoituksen jälkeen ja kertoo, mikä
versio käynnistyy (viiva: laite ei käynnisty):

```{.tuloste tiedosto="esimerkit/07-ab-paivitys.odotettu"}
```

Paikallaan päivittävä laite rikkoutuu viidessä katkokohdassa
seitsemästä, ja viallinen versio rikkoo sen pysyvästi. A/B-laite
käynnistyy aina. Hinta on kaksinkertainen flash. Pienissä laitteissa
käytetään vaihtoehtoa, jossa uusi kuva ladataan varapaikkaan ja
käynnistin vaihtaa paikkojen sisällön lohko kerrallaan niin, että
vaihdon voi jatkaa katkon jälkeen (MCUbootin *swap*-tila).

Myös QEMU-käynnistin valitsee kahdesta kelvollisesta kuvasta
uudemman:

```{.tuloste tiedosto="esimerkit/laite/testit/ab-paivitys.odotettu"}
```

## Manifesti

Laitteen ei pidä ladata megatavua dataa vain todetakseen, että päivitys
ei ole sille. **Manifesti** on pieni allekirjoitettu kuvaus
päivityksestä: kenelle se on, mikä sen järjestysnumero on ja mikä
hyötykuorman tiiviste on. IETF:n SUIT-malli (*Software Updates for
Internet of Things*, RFC 9019 ja RFC 9124) määrittelee tällaisen
manifestin rakenteen. Esimerkissä on sama logiikka JSON-muodossa:

```{.python tiedosto="esimerkit/07-manifesti.py" osa="tee"}
```

Laite tarkistaa manifestin ennen latausta ja hyötykuorman tiivisteen
latauksen jälkeen:

```{.python tiedosto="esimerkit/07-manifesti.py" osa="tarkista"}
```

```{.tuloste tiedosto="esimerkit/07-manifesti.odotettu"}
```

Laitemallin tarkistus on helppo unohtaa. Aito ja oikein allekirjoitettu
kuva toiselle laitemallille voi rikkoa laitteen, joten manifesti sitoo
kuvan laitemalliin. Latausosoite kuuluu allekirjoituksen piiriin,
mutta laite ei luota osoitteeseen vaan tiivisteeseen: hyötykuorman voi
ladata mistä tahansa välimuistista.

## Delta-päivitykset

Radiolinkki voi olla hidas ja maksullinen, ja akku rajallinen.
**Delta-päivitys** lähettää vain erot asennettuun versioon:

```{.python tiedosto="esimerkit/07-delta.py" osa="delta"}
```

```{.tuloste tiedosto="esimerkit/07-delta.odotettu"}
```

Delta-päivitys tekee laitteesta riippuvaisen siitä, että sen nykyinen
kuva on täsmälleen odotettu. Siksi rakennettu tulos tarkistetaan aina
manifestin tiivistettä vasten, ja väärästä pohjasta rakennettu kuva
hylätään. Tuotannossa erot lasketaan bsdiffin tai detoolsin kaltaisella
työkalulla, joka pakkaa myös siirtyneen koodin, ja deltan pohjan
tiiviste on manifestissa.

## Käytännössä

- **A/B tai varmistettu vaihto** aina, kun laite päivitetään kentällä.
  Paikallaan päivitys sopii vain laitteeseen, joka voidaan
  ohjelmoida uudelleen huollossa.
- **Kokeilukäynnistys ja vahvistus.** Uusi versio vahvistaa itsensä
  vasta, kun se on todennut toimivansa (esim. yhteys palvelimeen
  onnistui). Vasta sitten nostetaan versionpalautuksen laskuri.
- **Manifesti ensin.** Tarkista allekirjoitus, laitemalli,
  järjestysnumero ja koko ennen latausta.
- **Vaiheita julkaisuun.** Lähetä päivitys ensin pienelle osalle
  laitteista ja seuraa vahvistusten määrää ennen kuin jatkat.
- **Päivityspalvelu on osa tuotetta.** Sen tunnukset, allekirjoitusputki
  ja jakelukanava tarvitsevat saman suojauksen kuin laitteet; ks.
  *Tietoturva kehitystyössä*.

## Itsearviointi

- Osaat perustella A/B-päivityksen ja kokeilukäynnistyksen
  sähkökatkon ja viallisen version kannalta.
- Osaat suunnitella päivitysmanifestin ja luetella tarkistukset,
  jotka laite tekee ennen latausta ja sen jälkeen.
- Osaat selittää, miksi delta-päivityksen tulos tarkistetaan
  manifestin tiivistettä vasten.
