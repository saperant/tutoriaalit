# Uhkamallinnus ja riskit

Uhkamallinnus (*threat modeling*) on järjestelmällinen tapa löytää
suunnitelman heikkoudet ennen kuin hyökkääjä löytää ne toteutuksesta.
Adam Shostack tiivistää sen neljään kysymykseen:

1. Mitä olemme rakentamassa?
2. Mikä voi mennä pieleen?
3. Mitä teemme asialle?
4. Teimmekö riittävän hyvää työtä?

Uhkamallinnus tehdään suunnitteluvaiheessa ja päivitetään, kun
arkkitehtuuri muuttuu. Se ei vaadi raskasta prosessia: tunnin
keskustelu valkotaulun ääressä löytää usein vakavimmat ongelmat.

## Tietovuokaavio ja luottamusrajat

Ensimmäiseen kysymykseen vastataan piirtämällä **tietovuokaavio**
(*data flow diagram*, DFD). Siinä on neljä elementtityyppiä:

| Elementti | Tarkoittaa | Esimerkki |
|-----------|-----------|-----------|
| ulkoinen toimija | järjestelmän ulkopuolinen käyttäjä tai palvelu | asiakkaan selain |
| prosessi | koodi, joka käsittelee dataa | verkkokaupan API |
| tietovarasto | paikka, jossa data on levossa | tietokanta, lokit |
| tietovirta | datan siirtymä elementtien välillä | HTTPS-pyyntö |

**Luottamusraja** (*trust boundary*) erottaa osat, joilla on eri
luottamustaso: internet ja oma palvelin, käyttäjän laite ja
taustapalvelu, oma ja kumppanin järjestelmä. Rajan ylittävät
tietovirrat ovat hyökkääjän helpoimpia kohteita, koska niissä hän voi
lähettää mitä tahansa. Jokainen rajan ylittävä syöte on tarkistettava.

Luvun esimerkkinä on verkkokauppa. Asiakkaan selain lähettää tilauksen
kaupan API:lle, API tallentaa sen tietokantaan ja pyytää maksun
maksupalvelulta, ja maksupalvelu ilmoittaa onnistuneesta maksusta
takaisin API:lle. Kun elementit, niiden vyöhykkeet ja tietovirrat
kirjoitetaan datana, luottamusrajan ylitys seuraa mallista: virta
ylittää rajan, jos sen päät ovat eri vyöhykkeissä.

```{.python tiedosto="esimerkit/03-stride.py" osa="malli"}
```

Samasta mallista piirretään kaavio. Esimerkki `03-tietovuokaavio.py`
lukee mallin ja tulostaa sen Graphvizin DOT-kielellä:

```{.python tiedosto="esimerkit/03-tietovuokaavio.py" osa="kaavio"}
```

Toimija on suorakulmio, prosessi ellipsi ja tietovarasto lieriö.
Katkoviiva rajaa luottamusvyöhykkeen, ja rajan ylittävät virrat on
piirretty paksulla viivalla:

```{.dot tiedosto="esimerkit/03-tietovuokaavio.odotettu" otsikko="Verkkokaupan tietovuokaavio ja luottamusrajat ohjelman tulosteesta piirrettynä."}
```

Valkotaululla kaavio piirretään käsin, ja se riittää. Datana
esitetystä mallista on hyötyä, kun kaavio halutaan pitää
versionhallinnassa koodin vieressä ja siitä halutaan johtaa muuta,
kuten seuraavan osion uhkaluettelo.

## STRIDE

Toiseen kysymykseen vastataan käymällä kaavio läpi uhkaluokittain.
Microsoftin **STRIDE**-malli jakaa uhat kuuteen luokkaan, ja kukin
luokka rikkoo jotakin tietoturvan ominaisuutta:

| Luokka | Rikkoo | Torjunta |
|--------|--------|----------|
| **S**poofing, väärä henkilöllisyys | aitous | todennus |
| **T**ampering, peukalointi | eheys | eheyssuojaus, pääsynhallinta |
| **R**epudiation, kiistäminen | kiistämättömyys | lokit, allekirjoitukset |
| **I**nformation disclosure, tietovuoto | luottamuksellisuus | salaus, pääsynhallinta |
| **D**enial of service, palvelunesto | saatavuus | rajoitukset, kapasiteetti |
| **E**levation of privilege, oikeuksien korotus | valtuutus | vähimmät oikeudet, eristys |

Kaikki luokat eivät koske kaikkia elementtejä. Tietovirtaa ei voi
"korottaa oikeuksiltaan", eikä ulkoista toimijaa voi peukaloida
järjestelmän sisältä. *STRIDE per element* -taulukko kertoo, mitkä
luokat kuuluvat millekin elementille:

```{.python tiedosto="esimerkit/03-stride.py" osa="taulukko"}
```

Uhkaluettelo saadaan käymällä verkkokaupan malli läpi taulukon avulla.
Luottamusrajan ylittävät virrat tulostetaan ensin, koska niistä
kannattaa aloittaa:

```{.tuloste tiedosto="esimerkit/03-stride.odotettu"}
```

Lista ei ole vastaus vaan kysymyslista. Jokaisesta rivistä kysytään:
voiko tämä tapahtua meidän järjestelmässämme, ja jos voi, mikä sen
estää? Esimerkiksi "Maksupalvelu → Verkkokauppa-API: maksuilmoitus,
peukalointi" johtaa kysymykseen, tarkistammeko ilmoituksen aitouden vai
merkitsemmekö tilauksen maksetuksi minkä tahansa viestin perusteella.
Luku *Kryptografia käyttäjän näkökulmasta* näyttää tarkistuksen
HMAC:lla.

## Hyökkäyspuut

**Hyökkäyspuu** (*attack tree*) kuvaa hyökkääjän tavoitteen ja tavat
saavuttaa se. Juuri on tavoite, lehdet konkreettisia toimia. Sisäsolmu
on joko TAI (yksi lapsista riittää) tai JA (kaikki tarvitaan). Kun
lehdille annetaan hinta, vaikeus tai todennäköisyys, puusta voi laskea
hyökkääjän halvimman reitin:

```{.python tiedosto="esimerkit/03-hyokkayspuu.py" osa="puu"}
```

```{.python tiedosto="esimerkit/03-hyokkayspuu.py" osa="esimerkki"}
```

```{.tuloste tiedosto="esimerkit/03-hyokkayspuu.odotettu"}
```

Puu on helpompi lukea kuvana. Piirtofunktio käy puun läpi samalla
rekursiolla kuin `halvin` ja merkitsee halvimman reitin solmut ja
kaaret paksulla viivalla:

```{.python tiedosto="esimerkit/03-hyokkayspuu-kaavio.py" osa="piirto"}
```

```{.dot tiedosto="esimerkit/03-hyokkayspuu-kaavio.odotettu" otsikko="Hyökkäyspuu ennen korjausta. Sisäsolmussa näkyy sen tyyppi ja halvimman alipuun hinta."}
```

Puu opettaa kaksi asiaa. Ensinnäkin hyökkääjä valitsee halvimman
reitin, ei sitä, jota puolustaja on miettinyt eniten: kallis
SQL-injektion torjunta ei auta, jos varmuuskopio on julkisesti
luettavissa. Toiseksi korjaus siirtää hyökkääjän seuraavaksi
halvimpaan reittiin, joten puuta tarkastellaan uudelleen jokaisen
korjauksen jälkeen. Tässä seuraava reitti on tunnusten kalastelu ja
monivaiheisen tunnistuksen väsytys, jonka torjuu kalastelua kestävä
tunnistus (luku *Todennus*).

## Riskien arviointi

Kolmanteen kysymykseen vastataan priorisoimalla. Yksinkertaisin tapa
on arvioida jokaiselle uhalle todennäköisyys ja vaikutus asteikolla
1–5. Riskitaso on niiden tulo, ja riskit sijoitetaan
**riskimatriisiin**:

```{.python tiedosto="esimerkit/03-riskit.py" osa="rekisteri"}
```

```{.tuloste tiedosto="esimerkit/03-riskit.odotettu"}
```

Riskille on neljä vaihtoehtoista käsittelytapaa:

- **pienentäminen**: suojaus, joka laskee todennäköisyyttä tai
  vaikutusta (useimmiten),
- **välttäminen**: riskialtis ominaisuus jätetään pois,
- **siirtäminen**: vakuutus tai sopimus kumppanin kanssa (vastuu
  siirtyy, vahinko ei),
- **hyväksyminen**: tietoinen ja dokumentoitu päätös, jonka tekee
  riskin omistaja, ei kehittäjä yksin.

Numeerinen asteikko näyttää tarkalta, mutta arviot ovat karkeita.
Matriisin arvo on keskustelussa: miksi tämä on 4 eikä 2? Haavoittuvuuksien
vakavuuden standardoitu mittari on **CVSS** (*Common Vulnerability
Scoring System*), jota käytetään julkaistuissa
haavoittuvuustiedotteissa (CVE). Uusin versio on 4.0 (2023), mutta moni
haavoittuvuustietokanta ilmoittaa pisteet yhä versiolla 3.1, joten
tiedotteesta kannattaa katsoa, kumpaa se käyttää. CVSS kuvaa
haavoittuvuuden teknistä vakavuutta, ei riskiä juuri sinun
ympäristössäsi. Pisteiden laskenta vektorista käydään läpi taidossa
*Haavoittuvuuksien analyysi ja torjunta*.

## Käytännössä

- **Mallinna aikaisin ja usein.** Kevyt uhkamallinnus jokaisen
  merkittävän suunnittelumuutoksen yhteydessä on arvokkaampi kuin
  raskas kerran vuodessa.
- **Aloita luottamusrajoilta.** Rajan ylittävät tietovirrat ja niitä
  käsittelevät prosessit tuottavat suurimman osan vakavista uhista.
- **Kirjaa päätökset.** Uhkalista, valitut suojaukset ja hyväksytyt
  riskit kuuluvat projektin dokumentaatioon. Seuraava kehittäjä
  tarvitsee tiedon siitä, miksi jokin on tehty niin kuin on.
- **Ajattele halvinta reittiä.** Hyökkääjä ei kunnioita
  arkkitehtuurikaavion rajoja: kalastelu, varmuuskopiot ja
  kolmansien osapuolten tunnukset ovat usein helpompia kuin koodin
  haavoittuvuudet.
- **Riskin omistaa liiketoiminta.** Kehittäjä arvioi ja ehdottaa, mutta
  riskin hyväksymisestä päättää se, joka vastaa vahingosta.
- **Käytä yhteistä kieltä.** STRIDE, CWE-luokat (*Common Weakness
  Enumeration*) ja CVSS tekevät keskustelusta täsmällistä.

## Itsearviointi

- Osaat piirtää palvelusta tietovuokaavion ja merkitä siihen
  luottamusrajat.
- Osaat käydä kaavion läpi STRIDE-luokittain ja muotoilla uhista
  tarkistettavia kysymyksiä.
- Osaat rakentaa hyökkäyspuun ja päätellä siitä hyökkääjän halvimman
  reitin.
- Osaat priorisoida riskit todennäköisyyden ja vaikutuksen perusteella
  ja valita niille käsittelytavan.
