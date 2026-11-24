# CSRF, SameSite ja clickjacking

Selain liittää evästeet jokaiseen pyyntöön, joka menee evästeen
asettaneelle palvelimelle, riippumatta siitä, mikä sivu pyynnön
aloitti. Kaksi hyökkäystä käyttää tätä hyväksi. CSRF (*cross-site
request forgery*) lähettää pyynnön käyttäjän nimissä toiselta
sivustolta. Clickjacking upottaa kohdesivun näkymättömään kehykseen ja
houkuttelee käyttäjän klikkaamaan sitä.

## Sivusto ja alkuperä

Kaksi käsitettä määräävät, mitä selain sallii:

| Käsite | Määritelmä | Esimerkki: `https://app.pankki.fi:443` |
|--------|------------|----------------------------------------|
| Alkuperä (*origin*) | skeema + isäntä + portti | sama kuin `https://app.pankki.fi`, eri kuin `https://www.pankki.fi` |
| Sivusto (*site*) | skeema + rekisteröitävä verkkotunnus | sama kuin `https://www.pankki.fi`, eri kuin `https://pankki-kirjaudu.fi` |

Saman alkuperän käytäntö (*same-origin policy*) estää toista
alkuperää *lukemasta* vastauksia, mutta ei *lähettämästä* pyyntöjä.
Lomakkeen voi lähettää mihin tahansa. CSRF:n torjunta perustuu siksi
siihen, että palvelin tunnistaa pyynnön, joka ei tullut sen omalta
sivulta.

## Hyökkäys

Esimerkin pankki tunnistaa käyttäjän pelkästä istuntoevästeestä.
Hyökkääjän sivu on toisella sivustolla (testissä pankki on osoitteessa
`localhost` ja hyökkääjä osoitteessa `127.0.0.1`), ja se lähettää
tilisiirron heti, kun uhri avaa sivun:

```{.typescript tiedosto="esimerkit/src/04-csrf/pankki.ts" osa="hyokkaaja"}
```

## Kolme puolustusta

**SameSite-eväste.** Evästeen `SameSite`-attribuutti kertoo, kulkeeko
eväste toisen sivuston aloittamissa pyynnöissä:

| Arvo | Toisen sivuston pyynnöt | Käyttö |
|------|-------------------------|--------|
| `Strict` | ei koskaan | pankki, hallintaliittymät; linkki toiselta sivustolta näyttää uloskirjautuneelta |
| `Lax` | vain ylimmän tason GET-navigoinnissa (linkit) | tavallisen istunnon oletus |
| `None` | aina (vaatii `Secure`) | upotettavat palvelut, kolmannen osapuolen kirjautuminen |

Chromium käyttää oletuksena `Lax`-arvoa, jos attribuutti puuttuu,
mutta ei kaikkialla ja poikkeuksin. Esimerkiksi tuoreen evästeen
ylimmän tason POST sallitaan kahden minuutin ajan. Attribuutti
asetetaan siksi aina itse.

```{.typescript tiedosto="esimerkit/src/04-csrf/pankki.ts" osa="eväste"}
```

**CSRF-tunniste.** Lomakkeeseen lisätään piilokenttä, jonka arvo on
sidottu istuntoon ja jota toinen sivusto ei voi lukea
(*synchronizer token*). Vaihtoehto ilman palvelimen tilaa on
*double submit* -malli: sama satunnaisarvo evästeessä ja kentässä,
mieluiten allekirjoitettuna istunnon tunnisteella.

**Alkuperän tarkistus.** Selaimet lähettävät tilaa muuttavissa
pyynnöissä `Origin`-otsakkeen, jota sivun skripti ei voi väärentää.
Uudemmat selaimet lähettävät myös `Sec-Fetch-Site`-otsakkeen
(`same-origin`, `same-site`, `cross-site`), joka tekee tarkistuksesta
vielä suoraviivaisemman.

```{.typescript tiedosto="esimerkit/src/04-csrf/pankki.ts" osa="tarkistus"}
```

```{.typescript tiedosto="esimerkit/e2e/csrf.spec.ts" osa="csrf"}
```

`SameSite=Lax` yksinään torjuu esimerkin hyökkäyksen. Tunniste ja
alkuperän tarkistus ovat silti tarpeen: `SameSite` ei suojaa saman
sivuston muilta aliverkkotunnuksilta (`kayttajasivut.pankki.fi`
on sama sivusto kuin `app.pankki.fi`), eikä tilaa muuttavia
GET-pyyntöjä, jotka ovat virhe joka tapauksessa.

## Clickjacking

Hyökkääjän sivu upottaa kohdesivun läpinäkyvään kehykseen ja asettaa
sen houkuttelevan painikkeen päälle. Käyttäjä luulee painavansa
"Lunasta palkinto" ja painaa pankin "Vahvista"-painiketta. Torjunta
on kieltää upottaminen:

```{.typescript tiedosto="esimerkit/src/04-csrf/pankki.ts" osa="kehys"}
```

`frame-ancestors` on CSP:n moderni direktiivi; `X-Frame-Options` on
sen vanhempi edeltäjä, jota vanhat selaimet ymmärtävät. Jos upotus
on tarpeen, `frame-ancestors` luettelee sallitut sivustot.

```{.typescript tiedosto="esimerkit/e2e/csrf.spec.ts" osa="clickjacking"}
```

## Käytännössä

- **Kolme kerrosta:** `SameSite=Lax` (tai `Strict`), CSRF-tunniste
  lomakkeissa ja `Origin`- tai `Sec-Fetch-Site`-tarkistus. Kehykset
  (Spring Security, Django, Rails) tekevät kaksi jälkimmäistä
  oletuksena; älä kytke niitä pois.
- **GET ei muuta tilaa.** Muuten pelkkä kuva
  `<img src="/siirto?…">` riittää hyökkäykseen.
- **Rajapinnat Bearer-tokenilla** eivät ole alttiita CSRF:lle, koska
  selain ei lähetä otsaketta automaattisesti. Kun token siirretään
  evästeeseen (BFF, luku 8), CSRF-suojaus tulee taas tarpeelliseksi.
- **`frame-ancestors 'none'`** kaikille sivuille, joita ei ole tarkoitus
  upottaa. Hinta on nolla.
- **CORS ei ole CSRF-suojaus.** CORS säätelee, saako toisen
  alkuperän skripti *lukea* vastauksen. Pyyntö on jo lähetetty ja
  käsitelty, kun selain tarkistaa CORS-otsakkeet.

## Itsearviointi

- Osaat erottaa alkuperän ja sivuston ja kertoa, mitä saman
  alkuperän käytäntö estää ja mitä ei.
- Osaat valita evästeen `SameSite`-arvon käyttötapauksen mukaan.
- Osaat toteuttaa CSRF-tunnisteen ja `Origin`-tarkistuksen ja
  perustella, miksi niitä tarvitaan SameSite-evästeen lisäksi.
- Osaat estää sivun upottamisen kehykseen.
