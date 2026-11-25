# Tiimit ja organisaatiomallit

Tiivis suomenkielinen tutoriaali siitä, miten organisaation rakenne
muovaa ohjelmistoa: Conwayn laki, perinteiset organisaatiomallit ja
luovutusten hinta, Team Topologies, kognitiivinen kuorma, omistajuus ja
alustat, DevOps ja SRE, päätöksenteko, skaalausmallit sekä hajautetut
tiimit. Mallit esitetään perusteluineen, rajoineen ja kritiikkeineen,
ja väitteet tehdään konkreettisiksi pienillä Python-ohjelmilla, jotka
laskevat, simuloivat ja lukevat Git-historiaa.
Valmiit dokumentit:
[tiimit-ja-organisaatiot.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tiimit-ja-organisaatiot.pdf)
ja pikaopas
[tiimit-ja-organisaatiot-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tiimit-ja-organisaatiot-pikaopas.pdf).

Esitieto on *Ohjelmistoprojektin hallinta*. Esimerkkien lukemiseen
riittävät *Ohjelmoinnin perusteet (Python)* ja *Versionhallinta (Git)*.

## Sisältö

1. Johdanto – tiimiraja on rajapinta, esimerkkiyritys ja kaksi
   tiimijakoa
2. Conwayn laki – alkuperäinen väite, peilaushypoteesin näyttö,
   käänteinen Conway-liike, riippuvuudet ja yhdessä muuttuvat tiedostot
   Git-historiasta
3. Organisaatiomallit ja luovutukset – funktionaalinen, projekti-,
   matriisi- ja tuoteorganisaatio, komponentti- ja ominaisuustiimit,
   luovutuksen hinta jonomallilla, siilot
4. Team Topologies – neljä tiimityyppiä, kolme vuorovaikutustapaa,
   tiimin rajapinta, murtumatasot, kritiikki
5. Kognitiivinen kuorma ja tiimin koko – viestintäpolut, Dunbarin
   luvut varauksin, pitkäikäiset tiimit, kuorman arviointi
6. Omistajuus, alustat ja sisäiset tuotteet – omistajuusmallit,
   CODEOWNERS, bussikerroin, ”tee se, aja se”, alusta tuotteena,
   InnerSource
7. DevOps, SRE ja vastuunjako – kehityksen ja ylläpidon muuri,
   vääristymät, virhebudjetti ja raadanta, päivystys, jälkiselvitys,
   Westrumin kulttuurityypit
8. Päätöksenteko ja arkkitehtuurityö – autonomia ja yhtenäisyys,
   arkkitehdin rooli, neuvonantoprosessi, ADR ja RFC, killat
9. Skaalausmallit – riippuvuuksien hinta, Scrum of Scrums, SAFe, LeSS,
   Spotify-kuvaus, näyttö
10. Hajautetut tiimit ja organisaation muuttaminen – etäisyys,
    aikavyöhykkeet, asynkroninen viestintä, muutos pienin askelin
11. Lopuksi – nyrkkisäännöt, mallien rajat, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkkien tulosteet
make pdf      # tiimit-ja-organisaatiot.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Esimerkit käyttävät vain Pythonin standardikirjastoa ja Gitiä.
Kehityskontissa (`.devcontainer/tiimit-ja-organisaatiot`) työkalut ovat
valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).
