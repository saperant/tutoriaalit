# Ohjelmistoprojektin hallinta

Tiivis suomenkielinen tutoriaali siitä, miten ohjelmistotyö
suunnitellaan ja ohjataan: vaatimukset ja käyttäjätarinat,
prosessimallit vesiputouksesta ketteriin, Scrum ja Kanban, arviointi ja
ennustaminen, työn virtaus, riskit ja tekninen velka, viestintä sekä
sopimukset. Menetelmät esitetään perusteluineen ja rajoineen, ja
väitteet tehdään konkreettisiksi pienillä Python-simulaatioilla, jotka
lukija voi ajaa ja muuttaa.
Valmiit dokumentit:
[projektinhallinta.pdf](https://saperant.github.io/tutoriaalit/materiaalit/projektinhallinta.pdf)
ja pikaopas
[projektinhallinta-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/projektinhallinta-pikaopas.pdf).

Esitieto on *Versionhallinta (Git)*. Esimerkkien lukemiseen riittää
*Ohjelmoinnin perusteet (Python)*.

## Sisältö

1. Johdanto – miksi ohjelmistoprojekti on vaikea, projekti ja tuote,
   arvio on jakauma
2. Vaatimukset – sidosryhmät, käyttäjätarinat ja INVEST,
   hyväksymiskriteerit, tarinakartta, priorisointi (MoSCoW, WSJF),
   laajuus ja valmiin määritelmä
3. Prosessimallit – vesiputous ja Royce, V-malli, iteratiivinen
   kehitys, ketterä julistus, XP ja Lean, erän koon U-käyrä
4. Scrum ja Kanban – vastuut, tapahtumat ja tuotokset, sprintin
   sitoumus, väärinkäytökset, WIP-rajat ja veto, vertailu
5. Pilkkominen ja arviointi – epävarmuuskartio, pystysuorat viipaleet,
   tarinapisteet, kolmipistearvio, puskurit, kriittinen polku,
   suunnitteluharha
6. Ennustaminen historiasta – Monte Carlo -ennuste läpäisystä,
   takautuva testi, pisteet vastaan kappalemäärä
7. Virtaus – Littlen laki, keskeneräisen työn raja, kumulatiivinen
   virtauskaavio, kuormitusaste ja jonot, pullonkaula
8. Riskit, tekninen velka ja laatu – riskirekisteri ja varaus,
   pre-mortem, velan korkomalli, laadun hinta
9. Ihmiset ja viestintä – tilanneraportti, retrospektiivi,
   psykologinen turvallisuus, Brooksin laki, mittarit Git-historiasta
10. Sopimukset ja projektin päättäminen – sopimusmallit ja riskinjako,
    luovutus, jälkiarviointi
11. Lopuksi – nyrkkisäännöt, mallien rajat, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkkien tulosteet
make pdf      # projektinhallinta.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Esimerkit käyttävät vain Pythonin standardikirjastoa ja Gitiä.
Kehityskontissa (`.devcontainer/projektinhallinta`) työkalut ovat
valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).
