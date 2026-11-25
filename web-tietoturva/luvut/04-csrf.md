# CSRF, SameSite ja clickjacking

Selain liittää evästeet jokaiseen pyyntöön, joka menee evästeen
asettaneelle palvelimelle, riippumatta siitä, mikä sivu pyynnön
aloitti. Kaksi hyökkäystä käyttää tätä hyväksi. CSRF (*cross-site
request forgery*) lähettää pyynnön käyttäjän nimissä toiselta
sivustolta. Clickjacking upottaa kohdesivun näkymättömään kehykseen ja
houkuttelee käyttäjän klikkaamaan sitä. Luvun lopussa käsitellään
kolme rajapintaa, joilla sovellus itse avaa alkuperien välistä rajaa:
CORS, `postMessage` ja WebSocket.

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

```{.dot otsikko="CSRF-hyökkäyksen kulku. Hyökkääjän sivu ei näe evästettä eikä vastausta; se saa vain uhrin selaimen lähettämään pyynnön (5), johon selain liittää evästeen itse."}
digraph {
  layout=neato; splines=false;
  node [shape=point, width=0.01, height=0.01, style=invis];
  edge [arrowsize=0.7];
  h0 [label="hyökkääjän sivu", shape=box, style="rounded,filled", width=0, height=0.3, pos="0.00,0!"];
  hL [pos="0.00,-2.56!"];
  h0 -> hL [arrowhead=none, style=dotted];
  s0 [label="uhrin selain", shape=box, style="rounded,filled", width=0, height=0.3, pos="2.35,0!"];
  sL [pos="2.35,-2.56!"];
  s0 -> sL [arrowhead=none, style=dotted];
  p0 [label="pankki", shape=box, style="rounded,filled", width=0, height=0.3, pos="4.70,0!"];
  pL [pos="4.70,-2.56!"];
  p0 -> pL [arrowhead=none, style=dotted];
  s1 [pos="2.35,-0.51!"]; p1_ [pos="4.70,-0.51!"];
  s1 -> p1_ [];
  t1 [shape=plain, style="", fontsize=9, label="1. kirjautuminen", pos="3.53,-0.41!"];
  p2 [pos="4.70,-0.87!"]; s2_ [pos="2.35,-0.87!"];
  p2 -> s2_ [];
  t2 [shape=plain, style="", fontsize=9, label="2. Set-Cookie: istunto", pos="3.53,-0.77!"];
  s3 [pos="2.35,-1.23!"]; h3_ [pos="0.00,-1.23!"];
  s3 -> h3_ [];
  t3 [shape=plain, style="", fontsize=9, label="3. uhri avaa sivun", pos="1.18,-1.13!"];
  h4 [pos="0.00,-1.59!"]; s4_ [pos="2.35,-1.59!"];
  h4 -> s4_ [];
  t4 [shape=plain, style="", fontsize=9, label="4. sivu, jossa näkymätön lomake", pos="1.18,-1.49!"];
  s5 [pos="2.35,-1.95!"]; p5_ [pos="4.70,-1.95!"];
  s5 -> p5_ [];
  t5 [shape=plain, style="", fontsize=9, label="5. POST /siirto + eväste", pos="3.53,-1.85!"];
  p6 [pos="4.70,-2.31!"]; s6_ [pos="2.35,-2.31!"];
  p6 -> s6_ [];
  t6 [shape=plain, style="", fontsize=9, label="6. 303: siirto tehty", pos="3.53,-2.21!"];
}
```

Hyökkääjän ei tarvitse murtaa mitään. Riittää, että kirjautunut
käyttäjä avaa sivun, eikä pankki erota selaimen lähettämää pyyntöä
käyttäjän omasta.

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

Testi lukee saldon pankin sivulta jokaisen vaiheen jälkeen. Viimeinen
rivi kuuluu seuraavan osion clickjacking-testiin:

```{.tuloste tiedosto="esimerkit/naytos/04-csrf.odotettu"}
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

## CORS väärin asetettuna

Saman alkuperän käytäntö estää hyökkääjän sivua lukemasta pankin
vastauksia. CORS (*cross-origin resource sharing*) on tapa, jolla
palvelin *löysää* tätä estoa nimetyille alkuperille. Tavallisin virhe
on löysätä se kaikille: palvelin kopioi pyynnön `Origin`-otsakkeen
vastaukseen ja sallii evästeet.

```{.typescript tiedosto="esimerkit/src/04-csrf/cors.ts" osa="haavoittuva"}
```

Tällöin hyökkääjän sivun skripti voi tehdä pyynnön uhrin evästeillä ja
lukea vastauksen: saldon, viestit tai CSRF-tunnisteen, jolloin myös
edellisen osion tunnistesuojaus kaatuu. Selain ei hyväksy yhdistelmää
`Access-Control-Allow-Origin: *` ja evästeet, ja juuri siksi
heijastukseen päädytään "korjauksena". Oikea korjaus on täsmällinen
luettelo:

```{.typescript tiedosto="esimerkit/src/04-csrf/cors.ts" osa="korjattu"}
```

```{.tuloste tiedosto="esimerkit/naytos/04-cors.odotettu"}
```

Alkuperä `null` tulee muun muassa eristetystä kehyksestä
(`sandbox`) ja `data:`-osoitteesta, joten hyökkääjä pystyy tuottamaan
sen; sitä ei lisätä luetteloon. Alkuosan tai säännöllisen lausekkeen
vertailu pettää samoin kuin OAuthin paluuosoitteessa (luku 8):
`https://app.example.hyokkaaja.example` alkaa oikein.

## Viestit ikkunoiden välillä ja WebSocket

Kaksi selaimen rajapintaa ohittaa saman alkuperän käytännön
tarkoituksella, ja kummassakin tarkistus jää sovellukselle:

- **`postMessage`** välittää viestin ikkunalta toiselle alkuperästä
  riippumatta. Vastaanottaja tarkistaa `event.origin`-arvon
  täsmälleen ennen kuin käyttää dataa, ja lähettäjä nimeää
  kohdealkuperän (`ikkuna.postMessage(data, "https://app.example")`,
  ei `"*"`), jottei viesti päädy väärälle sivulle.
- **WebSocket-kättely** on tavallinen HTTP-pyyntö, johon selain liittää
  evästeet, eikä saman alkuperän käytäntö rajoita sitä. Hyökkääjän sivu
  voi avata yhteyden uhrin istunnolla (*cross-site WebSocket
  hijacking*). Palvelin tarkistaa kättelyssä `Origin`-otsakkeen samoin
  kuin lomakepyynnöissä, tai yhteys tunnistetaan viestillä, jossa on
  istuntoon sidottu tunniste.

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
- **CORS-luettelo on täsmällinen.** Ei heijastusta, ei `null`-arvoa,
  ei alkuosia. Jos rajapintaa käyttää vain oma sivu samasta
  alkuperästä, CORS-otsakkeita ei tarvita lainkaan.

## Itsearviointi

- Osaat erottaa alkuperän ja sivuston ja kertoa, mitä saman
  alkuperän käytäntö estää ja mitä ei.
- Osaat valita evästeen `SameSite`-arvon käyttötapauksen mukaan.
- Osaat toteuttaa CSRF-tunnisteen ja `Origin`-tarkistuksen ja
  perustella, miksi niitä tarvitaan SameSite-evästeen lisäksi.
- Osaat estää sivun upottamisen kehykseen.
- Osaat selittää, miksi `Origin`-otsakkeen heijastava CORS-asetus
  avaa vastaukset hyökkääjän luettaviksi, ja korjata sen.
- Osaat nimetä tarkistuksen, jonka `postMessage`-vastaanottaja ja
  WebSocket-palvelin tekevät itse.
