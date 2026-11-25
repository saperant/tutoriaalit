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

**Vastuulauseke.** Materiaali on tarkoitettu opetukseen ja oman
sovelluksen suojaamiseen. Käytä tekniikoita vain omiin sovelluksiisi ja
järjestelmiisi tai kohteisiin, joihin sinulla on kirjallinen lupa.
Luvaton tunkeutuminen ja tietojärjestelmän häirintä ovat rikoksia
(rikoslain 38. luku). Tekijät eivät vastaa materiaalin väärinkäytöstä.

## Esimerkit

`esimerkit/` on yksi npm-projekti (Node.js, TypeScript 7, node:test ja
Playwright 1.63). Jokaisesta haavoittuvuudesta on haavoittuva ja
korjattu versio ja testi, joka ajaa saman hyökkäyksen kumpaakin
vastaan. Näytösajot tulostavat kummankin version vastaukset
rinnakkain, ja tulosteet verrataan tallennettuihin
(`esimerkit/naytos/`). Esimerkit ovat tarkoituksella haavoittuvia:
palvelimet kuuntelevat vain osoitetta `127.0.0.1`, eikä niitä ajeta
julkisessa verkossa.

```text
cd esimerkit
make            # npm ci, tyyppitarkistus, node:test, näytösajot, Playwright
make naytos     # hyökkäysten tulokset tauluina
make kokeile    # luvun 3 keskustelupalsta omaan selaimeen
```

## Rakentaminen

`make testaa` tarkistaa rakenteen ja ajaa esimerkkiprojektin testit,
`make pdf` rakentaa PDF:t.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
