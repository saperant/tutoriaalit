# Palveluarkkitehtuurit

Järjestelmän jakaminen palveluiksi ja palvelujen yhdistäminen:
monoliitti, modulaarinen monoliitti ja mikropalvelut, rajatut
kontekstit, synkroninen viestintä ja vikasietoisuus, hajautetun
monoliitin antimallit, viestinvälitys ja integraatiomallit, saga ja
outbox, API-yhdyskäytävä ja sopimustestaus sekä perintöjärjestelmän
uudistaminen. Valmis dokumentti:
[palveluarkkitehtuurit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palveluarkkitehtuurit.pdf), pikaopas:
[palveluarkkitehtuurit-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palveluarkkitehtuurit-pikaopas.pdf).

Esitiedot: taidot *Taustapalvelut* ja *Kontit ja pilvi-infrastruktuuri*.

## Sisältö

1. Johdanto – esimerkkijärjestelmä, pino, arkkitehtuuripäätökset
2. Monoliitti vai mikropalvelut – hinnat, hyödyt, Conwayn laki
3. Modulaarinen monoliitti – moduulirajat ArchUnit-testeinä,
   prosessinsisäiset tapahtumat
4. Rajatut kontekstit ja palvelujen jako – DDD:n strateginen
   suunnittelu, kontekstikartta, tiedon omistus
5. Synkroninen viestintä – RPC, harhaluulot, CORBA ja SOAP, REST,
   gRPC ja GraphQL, yhteensopiva kehitys
6. Vikasietoisuus – aikaraja, uudelleenyritys, katkaisija, laipio
7. Hajautettu monoliitti ja muut antimallit – kutsuketjujen viive ja
   saatavuus, jaettu tietokanta
8. Viestinvälitys – jonot ja aiheet, idempotentti vastaanottaja,
   kuolleiden kirjeiden jono, Kafka
9. Integraatiomallit – kääntäjä, pilkkoja, kokooja, reititin
10. Saga ja outbox – miksi ei 2PC:tä, orkestrointi ja koreografia,
    tilakone, kompensaatio
11. Yhdyskäytävä, palveluverkko ja sopimukset – palvelun löytäminen,
    API-yhdyskäytävä, BFF, sopimustestit
12. Perintöjärjestelmän uudistaminen – kuristajaviikuna, korruption
    estokerros, rinnakkaisajo
13. Lopuksi – nyrkkisäännöt, mallit, lähteet

## Esimerkit

`esimerkit/` on Maven-projekti (Java 21, Spring Boot 4.2), jossa on
neljä modulia: `modulaarinen`, `etakutsut`, `viestit` (upotettu ActiveMQ
Artemis) ja `uudistus`. Testit eivät tarvitse Dockeria eivätkä
ulkoverkkoa riippuvuuksien latauksen jälkeen.

```text
make -C esimerkit      # kaikki testit (./mvnw verify)
make testaa            # rakenteen tarkistus ja esimerkit
make pdf               # tutoriaali ja pikaopas
```

Luvun 10 tilakonekaavio (`esimerkit/kaaviot/saga-tilat.dot`) tuotetaan
orkestroijan lähdekoodista, ja `make -C esimerkit` tarkistaa, että se
vastaa koodia.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
