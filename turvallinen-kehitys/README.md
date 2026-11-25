# Tietoturva kehitystyössä

Tiivis suomenkielinen tutoriaali tietoturvasta ohjelmistokehityksen
arkena: turvallinen kehitysprosessi, salaisuuksien hallinta,
kehitysympäristöt, toimitusketju, SBOM, allekirjoitukset, analyysi CI:ssä,
CI:n turvallisuus sekä katselmointi ja julkaisu. Esimerkit ovat Pythonia
ja Bashia ja toteuttavat pienessä mittakaavassa samat tarkistukset kuin
oikeat työkalut.

**Vastuulauseke.** Materiaali on tarkoitettu opetukseen ja oman
kehitysprosessin parantamiseen. Esimerkit ajetaan omalla koneella
tilapäisissä repositorioissa. Aja skannereita ja muita tarkistimia vain
omiin repositorioihisi ja järjestelmiisi tai sellaisiin, joiden
tarkastamiseen sinulla on omistajan lupa.

Valmiit dokumentit:
[turvallinen-kehitys.pdf](https://saperant.github.io/tutoriaalit/materiaalit/turvallinen-kehitys.pdf)
ja pikaopas
[turvallinen-kehitys-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/turvallinen-kehitys-pikaopas.pdf).

## Sisältö

1. Johdanto – esitiedot ja rajaus, esimerkit ja kolme periaatetta
2. Turvallinen kehitysprosessi – SSDLC, OWASP SAMM, NIST SSDF,
   uhkamallinnus rutiinina, valmiin määritelmä koodina
3. Salaisuuksien hallinta – vuotokanavat, salaisuusskanneri,
   commit-koukku, varastot, kierto ilman katkoa, vuodon käsittely
4. Kehitysympäristöt – kehityskontin asetukset, jaetut ympäristöt,
   tuotantodatan pseudonymisointi ja k-anonymiteetti
5. Riippuvuudet ja toimitusketju – lukitus ja tiivisteet,
   kirjoitusvirhepaketit, riippuvuussekaannus, asennusaikainen koodi
6. SBOM ja haavoittuvuustiedot – CycloneDX, pURL, OSV, skannauksen
   rajat ja VEX, oman tuotteen haavoittuvuuden käsittely
7. Allekirjoitukset ja toistettavat buildit – SSH-allekirjoitetut
   commitit, julkaisun allekirjoitus, Sigstore, toistettava pakkaus, SLSA
8. Analyysi CI:ssä – SAST, SCA, DAST, linterin tietoturvasäännöt,
   perustaso ja vanhenevat poikkeukset
9. CI:n turvallisuus – pull_request_target, skriptin injektio,
   kiinnitetyt toiminnot, oikeudet, OIDC-luottamusehdot
10. Katselmointi ja julkaisu – haarasuojaus, CODEOWNERS, kahden
    henkilön sääntö, turvallinen julkaisuprosessi
11. Lopuksi – nyrkkisäännöt, työkalut, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff (myös S-säännöt), mypy --strict,
              # ShellCheck ja kaikkien esimerkkien ajo
make pdf      # turvallinen-kehitys.pdf ja pikaopas
```

Esimerkit eivät käytä verkkoa. Git-esimerkit luovat tilapäisen
repositorion ja ohittavat käyttäjän omat git-asetukset. Tarvitaan
Python 3.12+, ruff, mypy, ShellCheck, git, OpenSSH (`ssh-keygen`) ja
pip (riippuvuussekaannuksen esimerkki). Kehityskontti:
`.devcontainer/turvallinen-kehitys`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
