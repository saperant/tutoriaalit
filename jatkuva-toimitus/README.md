# Jatkuva integraatio ja toimitus

Tiivis suomenkielinen tutoriaali siitä, miten muutos viedään kehittäjän
koneelta käyttäjälle: jatkuva integraatio ja trunk-pohjainen kehitys,
toimitusputki, artefaktit ja ympäristöt, putki koodina,
ominaisuusliput, julkaisustrategiat, tietokantamuutokset,
infrastruktuuri koodina ja GitOps sekä toimituskyvyn mittarit.
Periaatteet esitetään ensin ja työkalut esimerkkeinä, ja käytännöistä
kerrotaan perustelut, edellytykset ja rajat. Väitteet tehdään
konkreettisiksi oikealla Gitillä ja pienillä Python-malleilla, jotka
lukija voi ajaa ja muuttaa.
Valmiit dokumentit:
[jatkuva-toimitus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/jatkuva-toimitus.pdf)
ja pikaopas
[jatkuva-toimitus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/jatkuva-toimitus-pikaopas.pdf).

Esitiedot ovat *Testivetoinen kehitys ja testisuunnittelu* ja *Kontit
ja pilvi-infrastruktuuri*. Esimerkkien lukemiseen riittää
*Ohjelmoinnin perusteet (Python)* ja *Versionhallinta (Git)*.

## Sisältö

1. Johdanto – kolme käsitettä, palautesilmukka, esimerkit ja mallit,
   rajaus
2. Jatkuva integraatio – semanttinen ristiriita, haaran ikä, erän
   koko, käytännön vaatimukset, rikkinäinen runko
3. Trunk-pohjainen kehitys – haarautumismallit, säännöt, keskeneräisen
   työn piilottaminen, haarautuminen abstraktiolla, katselmointi
4. Toimitusputki – vaiheet, putki riippuvuusverkkona, nopea palaute,
   epävakaat testit, yksi tie tuotantoon
5. Artefaktit, versiointi ja ympäristöt – rakenna kerran, toistettava
   rakennus, edistäminen, konfiguraatio, ympäristöjen erot
6. Putki koodina – yhteiset käsitteet, ohut putki, putken testaaminen,
   muutoksiin perustuva testaus, välimuistit, tapaus: tämän aineiston
   putki
7. Ominaisuusliput – käyttöönotto ja julkaisu, lippujen lajit,
   asteittainen avaaminen, hätäkatkaisu, lippuvelka
8. Julkaisustrategiat – jatkuva toimitus ja käyttöönotto, rullaava,
   sinivihreä ja kanarialintu, peruminen, julkaisun seuranta
9. Tietokantamuutokset – migraatiot, laajenna–supista, peruminen,
   suuret taulut
10. Infrastruktuuri koodina ja GitOps – deklaratiivinen malli,
    ajautuma, täsmäytys, repositorion rakenne, rajat
11. Toimituskyvyn mittarit – neljä mittaria, laskenta Git-historiasta,
    mittarin pelaaminen, tutkimuksen rajat
12. Lopuksi – nyrkkisäännöt, mistä aloittaa, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, yamllint, pytest ja tulosteet
make pdf      # jatkuva-toimitus.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Esimerkit käyttävät Pythonin standardikirjastoa ja Gitiä sekä
tarkistimia ruff, mypy, pytest, yamllint ja check-jsonschema.
Kehityskontissa (`.devcontainer/jatkuva-toimitus`) työkalut ovat
valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).
