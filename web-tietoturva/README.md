# Web-sovellusten tietoturva

Web-sovellusten hyökkäykset ja niiden torjunta: injektiot ja SSRF, XSS
ja CSP, CSRF ja clickjacking, istunnot, salasanat, monivaiheinen
tunnistus ja pääsyavaimet, OAuth 2.0 ja OpenID Connect, JWT,
valtuutus, tiedostot ja turvaotsakkeet sekä tietoturvatestaus.
Valmis dokumentti:
[web-tietoturva.pdf](https://saperant.github.io/tutoriaalit/materiaalit/web-tietoturva.pdf),
pikaopas:
[web-tietoturva-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/web-tietoturva-pikaopas.pdf).

Esitiedot: taidot *Tietoturvan perusteet* ja *Web-sovellukset*.

## Esimerkit

`esimerkit/` on yksi npm-projekti (Node.js, TypeScript 7, node:test ja
Playwright 1.63). Jokaisesta haavoittuvuudesta on haavoittuva ja
korjattu versio ja testi, joka ajaa saman hyökkäyksen kumpaakin
vastaan. Esimerkit ovat tarkoituksella haavoittuvia: niitä ei ajeta
julkisessa verkossa.

```text
cd esimerkit
make            # npm ci, tyyppitarkistus, node:test ja Playwright
```

## Rakentaminen

`make testaa` tarkistaa rakenteen ja ajaa esimerkkiprojektin testit,
`make pdf` rakentaa PDF:t.

Lisenssi: CC BY-SA 4.0.
