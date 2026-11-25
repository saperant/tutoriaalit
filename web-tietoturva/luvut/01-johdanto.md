# Johdanto {.runko-johdanto}

Web-sovellus on internetin näkyvin hyökkäyspinta. Se on kaikkien
saatavilla, se käsittelee tunnistetietoja ja henkilötietoja, ja sen
jokainen syöte – osoiterivi, lomake, eväste, otsake ja ladattu tiedosto
– on hyökkääjän hallussa. Tämä tutoriaali käy läpi yleisimmät
hyökkäykset ja niiden torjunnan sekä käyttäjien tunnistuksen ja
valtuutuksen: salasanat, monivaiheisen tunnistuksen, pääsyavaimet,
OAuth 2.0:n ja OpenID Connectin sekä JWT:n.

## Esitiedot ja rajaus

Esitietoina ovat taidot *Tietoturvan perusteet* ja *Web-sovellukset*.
Uhkamallinnus, CIA-kolmio, pääsynhallintamallit ja injektioiden
perusajatus sekä XSS:n, CSP:n ja CORSin perusteet oletetaan. Tämä
tutoriaali menee niissä syvemmälle ja lisää aiheet, joita perusteissa
ei käsitelty. Kun sama aihe on jo esitiedoissa (TOTP, istunnot,
salasanakäytäntö, IDOR), luku kertaa periaatteen lyhyesti ja siirtyy
siihen, mitä web-sovelluksen toteutus vaatii lisää.

Luvun 2 esimerkeissä on SQL-kyselyjä. Ne ovat yhden taulun
`SELECT`-lauseita, ja niiden lukemiseen riittää tieto, että `WHERE`
rajaa rivit ja `ORDER BY` järjestää ne; kieli itse on taidossa *SQL ja
relaatiotietokannat*.

Tutoriaali rajautuu yhteen sovellukseen ja sen käyttäjiin. Muualla
käsitellään:

- palvelujen välinen tunnistus, salaisuudet tuotannossa ja
  nollaluottamus: *Palveluarkkitehtuurin tietoturva*
- riippuvuudet, toimitusketju ja tietoturva kehitysprosessissa:
  *Tietoturva kehitystyössä*
- algoritmit salasanatiivisteiden, TLS:n ja allekirjoitusten takana:
  *Kryptografia*
- saman toteutus Spring Securityllä: *Taustapalvelut*

## Vastuulauseke

Materiaali on tarkoitettu opetukseen ja oman sovelluksen suojaamiseen.

- **Käytä tekniikoita vain omiin sovelluksiisi ja järjestelmiisi tai
  kohteisiin, joihin sinulla on kirjallinen lupa.** Lupa hankitaan
  ennen testausta, ja siinä rajataan kohteet, ajankohta ja menetelmät.
- **Luvaton tunkeutuminen on rikos.** Suomen rikoslain 38. luku
  säätää rangaistavaksi muun muassa tietomurron ja tietojärjestelmän
  häirinnän; myös yritys voi olla rangaistava. Tämä on yleiskuvaus,
  ei oikeudellinen neuvo.
- **Tekijät eivät vastaa materiaalin väärinkäytöstä.** Esimerkit ovat
  paketin omia, tarkoituksella haavoittuvia pieniä palvelimia. Ne
  käynnistyvät testin sisällä omalle koneelle osoitteeseen `127.0.0.1`
  ja sammuvat testin lopussa. Niitä ei ajeta julkisessa verkossa, eikä
  paketissa ole työkaluja vieraiden palvelujen tutkimiseen.

Oman sovelluksen testaaminen näillä hyökkäyksillä on juuri se, mihin
tutoriaali kannustaa: virhe löytyy ennen kuin joku muu löytää sen.
Luvussa 13 on luettelo laillisista harjoitusympäristöistä, joissa
kohteet on tehty harjoittelua varten.

## OWASP Top 10

OWASP (*Open Worldwide Application Security Project*) kokoaa
tietoturvapoikkeamien aineistosta listan web-sovellusten yleisimmistä
riskiluokista. Vuoden 2025 lista:

| Nro | Luokka | Esimerkki | Luku |
|-----|--------|-----------|------|
| A01 | Rikkinäinen pääsynhallinta | toisen käyttäjän tilaus osoitetta muuttamalla, SSRF | 2, 10 |
| A02 | Väärät asetukset | puuttuvat turvaotsakkeet, oletustunnukset | 11 |
| A03 | Toimitusketjun puutteet | haavoittuva tai kaapattu riippuvuus | 3, *Tietoturva kehitystyössä* |
| A04 | Kryptografiset virheet | salasana ilman hidasta tiivistettä | 6, *Kryptografia* |
| A05 | Injektiot | SQL, komennot, XSS | 2, 3 |
| A06 | Turvaton suunnittelu | luottaminen asiakkaan tarkistukseen | kaikki |
| A07 | Tunnistuksen virheet | arvattava istunto, rajoittamaton arvailu | 5–9 |
| A08 | Ohjelmiston ja datan eheys | allekirjoittamaton päivitys, deserialisointi | *Tietoturvan perusteet* |
| A09 | Lokituksen ja hälytysten puutteet | hyökkäystä ei huomata | *Tietoturvan perusteet* |
| A10 | Poikkeustilanteiden väärä käsittely | virheilmoitus paljastaa sisäisen tilan | 11 |

Rajapinnoille on oma listansa (*OWASP API Security Top 10*), jonka
kärjessä ovat objekti-, ominaisuus- ja funktiotason valtuutusvirheet
(luku 10). Listat ovat tarkistuslistoja eivätkä menetelmä:
uhkamallinnus kertoo, mitkä luokat juuri tätä sovellusta koskevat.

## Hyökkäysten luokat

Lähes kaikki tämän tutoriaalin hyökkäykset kuuluvat johonkin
neljästä perheestä:

- **Data tulkitaan koodina.** Injektiot ja XSS: syöte päätyy
  SQL-lauseeseen, komentotulkkiin tai HTML-sivulle rakenteena eikä arvona.
  Torjunta on erottaa koodi ja data rakenteellisesti (parametrit,
  kontekstin mukainen koodaus), ei suodattaa vaarallisia merkkejä.
- **Selain lähettää valtuutuksen automaattisesti.** CSRF ja
  clickjacking käyttävät hyväksi sitä, että eväste kulkee pyynnön
  mukana, vaikka pyynnön aloittaisi toinen sivusto.
- **Palvelin luottaa asiakkaaseen.** Valtuutus tarkistetaan
  käyttöliittymässä, tunnus tulee osoitteesta tai rooli JSONista.
- **Tunnistus pettää.** Arvattavat istunnot, rajoittamaton arvailu,
  hukatut tokenit ja huolimaton tokenien tarkistus.

## Esimerkkien rakenne

Esimerkit ovat yksi npm-projekti (`esimerkit/`): Node.js:n
HTTP-palvelimia TypeScriptillä, Node ajaa tiedostot suoraan.
Riippuvuuksia on vain kolme: TypeScript, Noden tyyppimäärittelyt ja
Playwright. Kaikki muu on Noden vakiokirjastoa, jotta jokainen
tietoturvapäätös näkyy esimerkin omassa koodissa eikä katoa kehyksen
sisään.

Jokaisesta haavoittuvuudesta on **haavoittuva ja korjattu versio
rinnakkain** ja testi, joka ajaa saman hyökkäyksen kumpaakin vastaan.
Hyökkäyksen pitää onnistua ensimmäistä ja epäonnistua jälkimmäistä
vastaan. Testi todistaa siis kaksi asiaa: hyökkäys on todellinen, ja
korjaus pitää. Palvelimen testit ajetaan Noden omalla testiajurilla
(`node:test`), selaimen toimintaa vaativat testit Playwrightilla
Chromiumissa.

Palvelimet käyttävät pientä apukehystä (`src/http.ts`), joka jäsentää
pyynnön ja evästeet ja käynnistää palvelimen vapaaseen porttiin:

```{.typescript tiedosto="esimerkit/src/http.ts" osa="evasteet"}
```

Testi kertoo, pitääkö väite. Se ei näytä, mitä palvelin hyökkäykseen
vastasi. Siksi jokaisesta hyökkäyksestä on myös **näytösajo**, joka
tekee saman pyynnön haavoittuvalle ja korjatulle versiolle ja tulostaa
vastaukset rinnakkain. Lukujen tulostelohkot ovat näiden ajojen
tulosteita, ja `make` vertaa ne tallennettuihin joka kerta:

```{.make tiedosto="esimerkit/Makefile" osa="naytos"}
```

Komennot hakemistossa `esimerkit`:

| Komento | Tekee |
|---------|-------|
| `make` | asentaa riippuvuudet ja ajaa tyyppitarkistuksen, testit, näytösajot ja selaintestit |
| `make naytos` | ajaa näytösajot ja vertaa tulosteet tallennettuihin |
| `node src/naytos.ts 02-sql` | tulostaa yhden näytösajon (luettelo: `--lista`) |
| `make kokeile` | käynnistää luvun 3 keskustelupalstan omaan selaimeen osoitteeseen `127.0.0.1` |

Kehityskontin käyttö on kuvattu taidossa *Kehitysympäristöt ja Dev
Containers*.

Opetusesimerkit kirjoittavat monia tarkistuksia auki: CBOR-jäsentimen,
JWT:n tarkistuksen ja OpenID Connect -tarjoajan. Tuotannossa käytetään
kypsiä kirjastoja (`jose`, SimpleWebAuthn, `openid-client`), koska
pieni unohdus näissä on tietoturva-aukko. Esimerkkien tarkoitus on,
että lukija ymmärtää, mitä kirjasto tarkistaa ja miksi.

## Lukujen järjestys

Luvut 2–4 käsittelevät hyökkäyksiä, joissa syöte tai selaimen
toiminta käännetään sovellusta vastaan: injektiot, XSS ja CSRF. Luvut
5–9 seuraavat käyttäjän tunnistusta kirjautumisesta eteenpäin:
istunnot, salasanat, monivaiheinen tunnistus, OAuth 2.0 ja OpenID
Connect sekä JWT. Luku 10 käsittelee valtuutusta, luku 11 tiedostoja,
uudelleenohjauksia ja turvaotsakkeita ja luku 12 sitä, miten kaikki
tämä pidetään testattuna. Luku 13 kokoaa nyrkkisäännöt ja lähteet.
