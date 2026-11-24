---
title: Palveluarkkitehtuurit
subtitle: Pikaopas · Java 21 · Spring Boot 4.2 · ActiveMQ Artemis · Resilience4j
---

# Valinta

| | Monoliitti | Modulaarinen | Mikropalvelut |
|---|---|---|---|
| Julkaisu | yksi | yksi | palvelukohtainen |
| Transaktio | tavallinen | tavallinen | saga |
| Kutsu | ns | ns | ms, voi epäonnistua |
| Rajat | – | testit | prosessi |
| Operointi | pieni | pieni | suuri |

Erota palvelu vain syystä: **oma tiimi ja julkaisutahti**, **poikkeava
skaalaus**, **vikojen eristys**, **eri teknologia**. Kirjaa ADR.

**Conwayn laki:** järjestelmä jäljittelee organisaatiota. Yksi tiimi
omistaa palvelun kokonaan.

# Rajat

- Kyvykkyys ja kieli, ei kerros eikä taulu.
- Yksi transaktio = yksi aggregaatti.
- Tieto on yhden palvelun: **kysy**, **kopioi tapahtumista** tai
  **viittaa tunnisteella**. Ei jaettua skeemaa.

```{.java tiedosto="esimerkit/modulaarinen/src/test/java/fi/tutoriaalit/palvelut/kauppa/ModuulirajatTest.java" osa="saannot"}
```

# Synkroninen kutsu

| Muoto | Vahva | Heikko |
|-------|-------|--------|
| REST + JSON | julkiset, työkalut, välimuistit | puhelias, löysä skeema |
| gRPC | sisäinen, tehokas, suoratoisto | selain, välimuistit |
| GraphQL | monta näkymää | välimuisti, kustannusarvio |

Ketju: **viive = summa**, **saatavuus = tulo** ($0{,}99^5 \approx 0{,}95$).
Aikakatkaisun jälkeen lopputulos on **tuntematon** → idempotenssi.

Yhteensopivuus: lisää, älä muuta · suvaitsevainen lukija · laajenna ja
supista · versio vain rikkovalle muutokselle.

# Vikasietoisuus

| Suoja | Asetus |
|-------|--------|
| Aikaraja | yhteys ja vastaus erikseen, ketjun budjetista |
| Uudelleenyritys | ohimenevä virhe + idempotentti; 2^n · perus, satunnainen |
| Katkaisija | ikkuna, virheosuus, aika auki, puoliavoin koe |
| Laipio | samanaikaisuuden raja per riippuvuus |
| Kuorman pudotus | 503 + `Retry-After` |
| Varavastaus | välimuisti, oletus, heikennetty toiminto |

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/myynti/Katkaisijat.java" osa="katkaisija"}
```

# Viestit

| Laji | Nimi | Kanava | Vastaanottajia |
|------|------|--------|----------------|
| Komento | käsky: `VARAA` | jono | 1 |
| Tapahtuma | mennyt: `TilausVahvistettu` | aihe | 0..n |
| Vastaus | `VARATTU` | jono | 1 (pyytäjä) |

Toimitus on **vähintään kerran** → idempotentti vastaanottaja
(saapuneet-taulu, `viestiId` pääavaimena). Myrkkyviesti → DLQ
(enintään 3 yritystä). Järjestys vain avaimen sisällä.

| | Artemis, RabbitMQ | Kafka |
|---|---|---|
| Luettu viesti | poistuu | säilyy |
| Rinnakkaisuus | kuluttajat | osiot |
| Historia uudelle | ei | kyllä |

# Saga ja outbox

1. Kompensoitavat vaiheet (varaa) → 2. käännekohta (veloita) →
3. uudelleenyritettävät (toimita, laskuta).

- **Orkestrointi** kriittiselle polulle, **koreografia** reaktioille.
- Tilakone ohittaa vastaukset, jotka eivät sovi tilaan.
- Eristyksen puute: semanttinen lukko (`ALOITETTU`), vaihdannaiset
  päivitykset.

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/myynti/Lahtevat.java" osa="lahtevat"}
```

Outbox: tila ja viesti samaan transaktioon; välittäjä tai CDC
(Debezium) lähettää.

# Integraatiomallit

| Malli | Tekee |
|-------|-------|
| Kääntäjä | vieras muoto kanoniseksi |
| Pilkkoja / kokooja | osiin / takaisin korrelaatiotunnuksella |
| Sisältöreititin | kanava sisällön mukaan |
| Suodatin | pudottaa tarpeettomat |
| Kuolleiden kirjeiden kanava | rikkinäinen ei pysäytä muita |
| Lunastuskuitti | iso runko erikseen, viestissä viite |
| Hajauta ja kokoa | kysely monelle, kooste |

# Reuna ja sopimukset

- **Yhdyskäytävä**: todennus, rajoitus (merkkiämpäri), reititys,
  korrelaatiotunnus, aikaraja (502/504). Ei liiketoimintalogiikkaa.
- **BFF**: käyttöliittymäkohtainen kooste, käyttöliittymätiimin oma.
- **Palveluverkko**: mTLS, uudelleenyritykset ja mittarit sivuvaunussa.
- **Kuluttajavetoinen sopimus**: kuluttaja kirjaa käyttämänsä kentät;
  tuottaja ajaa ne joka käännöksessä (Pact, `can-i-deploy`).

# Uudistaminen

| Vaihe | Malli |
|-------|-------|
| 1 | julkisivu vanhan eteen, kaikki vanhalle |
| 2 | uusi lukee vanhaa korruption estokerroksen kautta |
| 3 | rinnakkaisajo: vanha vastaa, erot kirjataan |
| 4 | reitti uudelle (kanarialintu muuttaville) |
| 5 | data: CDC, lopuksi kirjoitukset uuteen |
| 6 | vanha sammutetaan |

# Hinnat

| Valinta | Hinta |
|---------|-------|
| Palveluksi erottaminen | verkko, sagat, putki, valvonta, päivystys |
| Synkroninen riippuvuus | viive + saatavuus |
| Viestinvälitys | eventual consistency, välittäjän operointi |
| Saga | välitilat näkyvät, kompensaatiot |
| Tapahtumista kopioitu data | viive, muotojen hallinta |
| Palveluverkko | viive, infrastruktuuri |
