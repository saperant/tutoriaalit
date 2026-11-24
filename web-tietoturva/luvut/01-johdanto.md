# Johdanto {.runko-johdanto}

Web-sovellus on internetin näkyvin hyökkäyspinta. Se on kaikkien
saatavilla, se käsittelee tunnistetietoja ja henkilötietoja, ja sen
jokainen syöte – osoiterivi, lomake, eväste, otsake ja ladattu tiedosto
– on hyökkääjän hallussa. Tämä tutoriaali käy läpi yleisimmät
hyökkäykset ja niiden torjunnan sekä käyttäjien tunnistuksen ja
valtuutuksen: salasanat, monivaiheisen tunnistuksen, pääsyavaimet,
OAuth 2.0:n ja OpenID Connectin sekä JWT:n.

Esitietoina ovat taidot *Tietoturvan perusteet* ja *Web-sovellukset*.
Uhkamallinnus, CIA-kolmio, pääsynhallintamallit ja injektioiden
perusajatus sekä XSS:n, CSP:n ja CORSin perusteet oletetaan. Tämä
tutoriaali menee niissä syvemmälle ja lisää aiheet, joita perusteissa
ei käsitelty.

## OWASP Top 10

OWASP (*Open Worldwide Application Security Project*) kokoaa
tietoturvapoikkeamien aineistosta listan web-sovellusten yleisimmistä
riskiluokista. Vuoden 2025 lista on suunnilleen tämä:

| Luokka | Esimerkki | Luku |
|--------|-----------|------|
| Rikkinäinen pääsynhallinta | toisen käyttäjän tilaus osoitetta muuttamalla, SSRF | 2, 10 |
| Väärät asetukset | puuttuvat turvaotsakkeet, oletustunnukset | 11 |
| Toimitusketjun puutteet | haavoittuva tai kaapattu riippuvuus | *Tietoturva kehitystyössä* |
| Kryptografiset virheet | salasana ilman hidasta tiivistettä | 6, *Kryptografia* |
| Injektiot | SQL, komennot, XSS | 2, 3 |
| Turvaton suunnittelu | luottaminen asiakkaan tarkistukseen | kaikki |
| Tunnistuksen virheet | arvattava istunto, rajoittamaton arvailu | 5–9 |
| Ohjelmiston ja datan eheys | allekirjoittamaton päivitys, deserialisointi | *Tietoturvan perusteet* |
| Lokituksen ja valvonnan puutteet | hyökkäystä ei huomata | *Tietoturvan perusteet* |
| Poikkeusten väärä käsittely | virheilmoitus paljastaa sisäisen tilan | 11 |

Rajapinnoille on oma listansa (*OWASP API Security Top 10*), jonka
kärjessä ovat objekti-, ominaisuus- ja funktiotason valtuutusvirheet
(luku 10). Listat ovat tarkistuslistoja eivätkä menetelmä:
uhkamallinnus kertoo, mitkä luokat juuri tätä sovellusta koskevat.

## Hyökkäysten luokat

Lähes kaikki tämän tutoriaalin hyökkäykset kuuluvat johonkin
neljästä perheestä:

- **Data tulkitaan koodina.** Injektiot ja XSS: syöte päätyy SQL-
  lauseeseen, komentotulkkiin tai HTML-sivulle rakenteena eikä arvona.
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

```{.make tiedosto="esimerkit/Makefile"}
```

Opetusesimerkit kirjoittavat monia tarkistuksia auki: CBOR-jäsentimen,
JWT:n tarkistuksen ja OpenID Connect -tarjoajan. Tuotannossa käytetään
kypsiä kirjastoja (`jose`, SimpleWebAuthn, `openid-client`), koska
pieni unohdus näissä on tietoturva-aukko. Esimerkkien tarkoitus on,
että lukija ymmärtää, mitä kirjasto tarkistaa ja miksi.

> Esimerkit ovat haavoittuvia tarkoituksella. Niitä ei ajeta
> julkisessa verkossa, ja hyökkäyksiä harjoitellaan vain omiin
> järjestelmiin tai luvan kanssa.
