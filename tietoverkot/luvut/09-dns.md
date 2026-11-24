# DNS ja mDNS

DNS (*Domain Name System*) muuntaa nimet osoitteiksi ja paljon muuta:
se kertoo sähköpostipalvelimet, palveluiden portit, varmentajat ja
todentaa sähköpostin lähettäjiä. Lähes jokainen yhteys alkaa
DNS-kyselyllä, ja moni katkos on DNS-ongelma. Vanha sanonta on
puoliksi vitsi: "It's always DNS."

## Nimiavaruus ja selvitys

Nimet muodostavat puun, jonka juuri on `.`. Juuripalvelimet tuntevat
ylätason (`fi`, `com`), ylätason palvelimet toisen tason (`esim.fi`), ja
niin edelleen. Jokaisella *vyöhykkeellä* (*zone*) on
**auktoritatiiviset** palvelimet, jotka tietävät sen nimet.

Kone ei kysy juurelta itse. Sen *stub-selvittäjä* (libc, systemd-
resolved) kysyy **rekursiiviselta selvittäjältä** (operaattorin,
yrityksen tai julkisen, esim. 1.1.1.1), joka kulkee puun läpi
juuresta alkaen ja tallentaa vastaukset välimuistiin tietueen
*TTL*-ajan. Siksi DNS-muutos näkyy viiveellä: vanha tietue on
välimuisteissa TTL:n loppuun asti.

Rekursiivinen selvittäjä kulkee puun läpi ja palauttaa vastauksen
stub-selvittäjälle (numerot kertovat järjestyksen):

```{.dot otsikko="Nimen www.esim.fi selvitys välimuistin ollessa tyhjä"}
digraph {
  rankdir=LR; nodesep=0.35;
  edge [fontsize=8];
  stub [label="sovellus ja\nstub-selvittäjä"];
  rek [label="rekursiivinen\nselvittäjä\n(välimuisti)"];
  juuri [label="juuripalvelin\n."];
  fi [label="fi-palvelin"];
  esim [label="esim.fi:n\nauktoritatiivinen"];
  stub -> rek [label="1 www.esim.fi A?"];
  rek -> juuri [label="2"];
  juuri -> rek [label="3 kysy fi:ltä", style=dashed];
  rek -> fi [label="4"];
  fi -> rek [label="5 kysy esim.fi:ltä", style=dashed];
  rek -> esim [label="6"];
  esim -> rek [label="7 A 192.0.2.80", style=dashed];
  rek -> stub [label="8 vastaus, TTL", style=dashed];
}
```

| Tietue | Sisältö |
|--------|---------|
| A, AAAA | IPv4- ja IPv6-osoite |
| CNAME | Alias toiselle nimelle |
| MX | Sähköpostipalvelin ja prioriteetti |
| TXT | Vapaa teksti: SPF, DKIM, varmennukset |
| NS | Vyöhykkeen nimipalvelimet |
| PTR | Käänteinen: osoitteesta nimi (`in-addr.arpa`, `ip6.arpa`) |
| SRV | Palvelun kone ja portti |
| CAA | Varmentajat, jotka saavat myöntää varmenteen |

## Viesti tavu tavulta

DNS-viesti kulkee tavallisesti UDP:llä porttiin 53. Otsakkeessa on
16-bittinen tunniste, liput ja osioiden lukumäärät. Nimi koodataan
osina, joiden edessä on pituustavu:

```{.python tiedosto="esimerkit/09-dns/dnsviesti.py" osa="koodaus"}
```

Vastauksessa sama nimi esiintyy monta kertaa. Tilan säästämiseksi
toistuva nimi korvataan *osoittimella* aiempaan kohtaan viestissä
(kaksi ylintä bittiä `11`). Purkajan on seurattava osoittimia ja
varottava silmukoita, joilla vihamielinen vastaus voisi jumittaa sen:

```{.python tiedosto="esimerkit/09-dns/dnsviesti.py" osa="purku"}
```

Vastauksen rakentaminen näyttää saman toisesta suunnasta. Tietueen
nimi on osoitin `0xC00C`, eli otsakkeen jälkeiseen kysymykseen:

```{.python tiedosto="esimerkit/09-dns/dnsviesti.py" osa="vastaus"}
```

```{.python tiedosto="esimerkit/09-dns/main.py" osa="esittely"}
```

```{.tuloste tiedosto="esimerkit/09-dns.odotettu"}
```

## Laboratorio: oma vyöhyke

Paikallinen nimipalvelin, joka vastaa vyöhykkeestä `koti.example`:

```{.bash tiedosto="esimerkit/09-nimipalvelu.sh" osa="palvelin"}
```

```{.bash tiedosto="esimerkit/09-nimipalvelu.sh" osa="kyselyt"}
```

Samat kyselyt voi tehdä omalla asiakkaalla. Asiakas hyväksyy
vastauksen vain, jos sen tunniste vastaa kyselyä:

```{.python tiedosto="esimerkit/09-dns/main.py" osa="kysy"}
```

```{.bash tiedosto="esimerkit/09-nimipalvelu.sh" osa="oma"}
```

```{.tuloste tiedosto="esimerkit/09-nimipalvelu.odotettu"}
```

`dig +short` näyttää vain arvot. Ilman sitä `dig` näyttää koko vastauksen:
otsakkeen liput (`aa` = auktoritatiivinen, `rd`/`ra` = rekursio), TTL:t
ja vastaavan palvelimen. Olematon nimi palauttaa koodin `NXDOMAIN`,
joka on eri asia kuin `SERVFAIL` (palvelin ei saanut vastausta
selvitettyä) tai aikakatkaisu (palvelin ei vastaa).

## mDNS: nimet ilman nimipalvelinta

Kotiverkon tulostimet, kaiuttimet ja IoT-laitteet löytyvät nimellä
`laite.local` ilman nimipalvelinta. Multicast DNS (RFC 6762) käyttää
DNS-viestejä, mutta kysely lähetetään ryhmälähetyksenä osoitteeseen
`224.0.0.251` porttiin 5353 (IPv6: `ff02::fb`), ja nimen omistaja
vastaa itse. DNS-SD (RFC 6763) ilmoittaa samalla tavalla palveluita
(`_ipp._tcp.local`). Toteutuksia ovat Avahi (Linux) ja Bonjour (Apple).

```{.python tiedosto="esimerkit/09-dns/main.py" osa="mdns"}
```

```{.bash tiedosto="esimerkit/09-mdns.sh" osa="reitti"}
```

```{.bash tiedosto="esimerkit/09-mdns.sh" osa="kysely"}
```

```{.tuloste tiedosto="esimerkit/09-mdns.odotettu"}
```

Ryhmään liittynyt kone vastaanottaa ryhmälähetykset; muut verkkokortit
suodattavat ne pois. `224.0.0.1` (kaikki koneet) on jokaisen jäsenyys.
mDNS ei ylitä reititintä, joten se toimii vain yhdessä aliverkossa.

## Koneen omat asetukset

Linux selvittää nimet tiedoston `/etc/nsswitch.conf` järjestyksessä:
yleensä ensin `/etc/hosts`, sitten mDNS (Avahi) ja DNS.
Nimipalvelimet ovat tiedostossa `/etc/resolv.conf`, jonka
systemd-resolved hallitsee usein itse (`resolvectl status`). Siksi
`dig` (kysyy suoraan DNS-palvelimelta) ja `getent hosts nimi` (käyttää
samaa reittiä kuin ohjelmat) voivat antaa eri vastauksen.

DNS:n tietoturva: perinteinen DNS kulkee salaamattomana ja on
väärennettävissä. DNSSEC allekirjoittaa vastaukset, ja DoT (DNS over
TLS) sekä DoH (DNS over HTTPS) salaavat yhteyden selvittäjään.

## Käytännössä

- **Laske TTL alas ennen muutosta.** Jos siirrät palvelun uuteen
  osoitteeseen, laske TTL esimerkiksi viiteen minuuttiin päivää ennen,
  jotta välimuistit päivittyvät nopeasti.
- **Älä välimuistita ikuisesti sovelluksessa.** Pitkäikäiset prosessit,
  kuten Javan vanhat oletusasetukset, ovat jääneet kiinni vanhaan
  osoitteeseen. Kunnioita TTL:ää.
- **Testaa kumpaakin reittiä**: `dig` näyttää, mitä DNS sanoo,
  `getent hosts` sen, mitä ohjelma näkee.
- **CNAME ei käy vyöhykkeen juureen** (`esim.fi`), koska samassa nimessä
  on oltava SOA- ja NS-tietueet. Palveluntarjoajat kiertävät tämän
  omilla ALIAS-tietueillaan.
- **Sisäverkon nimet** kuuluvat omaan aliverkkotunnukseen
  (`sisa.esim.fi`) tai varattuun `home.arpa`-tunnukseen. Itse keksitty
  `.local` törmää mDNS:ään ja `.dev` tai `.corp` oikeisiin
  ylätunnuksiin.

## Itsearviointi

- Osaat selittää rekursiivisen selvittäjän, auktoritatiivisen
  palvelimen ja TTL:n roolit sekä tavallisimmat tietuetyypit.
- Osaat koodata DNS-kyselyn ja purkaa vastauksen, myös pakatut nimet.
- Osaat tehdä kyselyitä `dig`-komennolla ja tulkita `NXDOMAIN`-,
  `SERVFAIL`- ja aikakatkaisutilanteet.
- Osaat kuvata mDNS:n toiminnan ja sen eron tavalliseen DNS:ään.
- Osaat selvittää, mistä kone hakee nimensä (`nsswitch.conf`,
  `resolv.conf`) ja miksi `dig` ja ohjelma voivat nähdä eri vastauksen.
