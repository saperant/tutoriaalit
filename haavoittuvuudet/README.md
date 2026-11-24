# Haavoittuvuuksien analyysi ja torjunta

Tiivis suomenkielinen tutoriaali muistiturvallisuusvirheiden
löytämisestä, arvioinnista ja korjaamisesta omassa C-koodissa (Linux,
x86-64). Aiheina turvallinen ohjelmointi C:llä, pinon ja keon
ylivuodot, käyttö vapautuksen jälkeen, muotoilumerkkijonovirheet,
käännöksen ja käyttöjärjestelmän suojaukset (ASLR, NX, pinokanari,
RELRO, FORTIFY_SOURCE, CFI, CET, PAC), fuzzaus (libFuzzer, AFL++),
juurisyyanalyysi, tapaustutkimukset tunnetuista haavoittuvuuksista sekä
vastuullinen ilmoittaminen (CVSS, CVE, `security.txt`).

Näkökulma on puolustava: esimerkit ovat paketin omia, tarkoituksella
haavoittuvia pieniä ohjelmia, jotka ajetaan paikallisesti sanitoijien,
debuggerin ja fuzzerien kanssa. Toimivia hyökkäyksiä ei rakenneta.

**Vastuulauseke.** Materiaali on tarkoitettu opetukseen ja oman koodin
parantamiseen. Käytä tekniikoita vain omiin ohjelmiisi ja
järjestelmiisi tai kohteisiin, joihin sinulla on kirjallinen lupa.
Luvaton tunkeutuminen ja tietojärjestelmän häirintä ovat rikoksia
(rikoslain 38. luku). Tekijät eivät vastaa materiaalin väärinkäytöstä.
Laillisia harjoitusympäristöjä on lueteltu luvussa 12.

Valmis dokumentti:
[haavoittuvuudet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/haavoittuvuudet.pdf),
pikaopas
[haavoittuvuudet-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/haavoittuvuudet-pikaopas.pdf).

## Sisältö

1. Johdanto – vastuulauseke, ensimmäinen löydös sanitoijalla
2. Turvallinen ohjelmointi C:llä – koon laskenta, etumerkit,
   rajapinnat, varoitukset ja staattinen analyysi
3. Pinon ylivuoto – kehyksen asettelu, pinokanari
4. Kekovirheet – ylivuoto, käyttö vapautuksen jälkeen,
   kaksoisvapautus
5. Muotoilumerkkijonovirheet – tietovuoto, `%n`, FORTIFY_SOURCE
6. Suojaukset – ASLR, PIE, NX, RELRO, FORTIFY_SOURCE, tarkistustyökalu
7. Ohjausvuon eheys – ROP periaatteena, Clangin CFI, CET, PAC ja BTI
8. Fuzzaus – libFuzzer, korpus, minimointi, regressiotestit, AFL++
9. Juurisyy, arviointi ja korjaus – raportin lukeminen,
   hyödynnettävyyden arviointi, variaatioanalyysi
10. Tapaustutkimuksia – Morrisin mato, Debianin OpenSSL, Heartbleed,
    goto fail, Cloudbleed, Baron Samedit, xz-utils
11. Vastuullinen ilmoittaminen – CVSS, CWE, CVE, `security.txt`,
    bug bounty, CRA
12. Lopuksi – nyrkkisäännöt, laillinen harjoittelu, lähteet

## Rakentaminen

```text
make testaa   # kääntää esimerkit, ajaa analyysit ja vertaa tulosteet
make pdf      # rakentaa haavoittuvuudet.pdf:n ja pikaoppaan
```

Esimerkit tarvitsevat GCC 14:n, Clang 20:n (clang-tidy ja lld),
gdb:n, binutilsin, AFL++:n, AArch64-ristikääntäjän, Pythonin (`ruff`,
`mypy`) ja ShellCheckin. Jokainen esimerkki on hakemisto
`esimerkit/NN-nimi/`, jossa on ohjelmat ja `aja.sh`;
`esimerkit/testaa.sh` ajaa ne ja vertaa tulosteita tiedostoihin
`odotettu`. Kehityskontti on hakemistossa
`.devcontainer/haavoittuvuudet`.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.
Luvun 10 lyhyet koodiotteet ovat lainauksia alkuperäisten projektien
korjauksista tai niitä kuvaavaa pseudokoodia.
