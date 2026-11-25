---
title: Ohjelmistoprojektin hallinta
subtitle: Pikaopas · vaatimukset, arviot, virtaus, riskit
---

# Vaatimukset

| Asia | Muistisääntö |
|----------------|--------------------------------------------------|
| tarina | roolina X haluan Y, jotta Z; kortti, keskustelu, vahvistus |
| INVEST | itsenäinen, neuvoteltava, arvokas, arvioitava, pieni, testattava |
| kriteeri | oletetaan – kun – niin; myös virhetilanteet |
| laatuvaatimus | mitattava ja testattava (ISO/IEC 25010 muistilistana) |
| MoSCoW | must, should, could, won't; pakollisia alle puolet |
| WSJF | viivästymisen hinta / kesto, suurin ensin |
| valmiin määritelmä | sama kaikille töille; ei tingitä kiireessä |

# Prosessimallit

| Malli | Sopii, kun |
|----------------|--------------------------------------------------|
| vaiheittainen | vaatimukset vakaat ja tunnetut |
| V-malli | sääntely vaatii jäljitettävyyden |
| iteratiivinen | vaatimukset epävarmat, palaute saatavilla |
| Scrum | tuotekehitys tavoite kerrallaan; sprintti ≤ 1 kk |
| Kanban | jatkuva työvirta; WIP-rajat ja veto |

Scrum: tuoteomistaja, Scrum master, kehittäjät · suunnittelu,
päivittäinen Scrum, katselmus, retrospektiivi · tuotejono, sprintin
tehtävälista, lisäys. Sitoudu tavoitteeseen, älä listaan.

# Arviointi

| Asia | Sääntö |
|----------------|--------------------------------------------------|
| arvio | väli tai jakauma, ei luku; kirjaa oletukset |
| epävarmuuskartio | idea 0,25–4×; vaatimukset valmiit 0,67–1,5× |
| PERT | $E = (o + 4m + p)/6$, $\sigma = (p - o)/6$ |
| summa | odotusarvot yhteen; hajonta $\sqrt{\sum \sigma^2}$ |
| 85 %:n varmuus | $E + 1{,}04\,\sigma$ (normaalijakauma) |
| puskuri | yksi yhteinen projektin lopussa, ei tehtäväkohtaisia |
| kriittinen polku | pisin polku; pelivara = myöhäisin − aikaisin loppu |
| pilkkominen | pystysuorat viipaleet; työ enintään muutama päivä |
| sprintti | keskinopeus pitää noin joka toisella kerralla |

# Ennustaminen

```{.python tiedosto="esimerkit/ennuste.py" osa="ennuste"}
```

| Kysymys | Vastaus jakaumasta |
|----------------|--------------------------------------------------|
| milloin valmis | yläpää: 85 %:n persentiili viikoista |
| montako ehtii | alapää: 15 %:n persentiili määristä |
| pitääkö ennuste | takautuva testi omalla historialla |
| oletus | tuleva muistuttaa historiaa; työt samankokoisia |

# Virtaus

| Asia | Kaava tai sääntö |
|----------------|--------------------------------------------------|
| Littlen laki | kiertoaika = WIP / läpäisy |
| WIP-raja | noin yksi työ henkeä kohden; säädä mittareista |
| kuormitus | läpimenoaika = kesto / (1 − kuormitusaste) |
| pullonkaula | läpäisy = hitain vaihe; vahvista sitä, rajaa jonoa |
| erä | pienennä, kun palautekierros halpenee |
| palvelulupaus | 85 %:n persentiili läpimenoajoista |
| työn ikä | vanhin keskeneräinen ensin |

# Riskit ja velka

| Asia | Sääntö |
|----------------|--------------------------------------------------|
| altistus | todennäköisyys × vaikutus; järjestää riskit |
| toimintatapa | vältä, pienennä, siirrä tai hyväksy |
| varaus | jakauman 85–95 %:n taso, ei altistusten summa |
| torjunta | kannattaa, jos altistuksen lasku > hinta |
| pre-mortem | ”projekti epäonnistui; miksi?” ennen sitoutumista |
| velka | kirjaa päätös, korko ja takaisinmaksu; kallein ensin |
| laadun hinta | ehkäisy < arviointi < sisäinen virhe < ulkoinen virhe |

# Ihmiset ja sopimukset

| Asia | Sääntö |
|----------------|--------------------------------------------------|
| raportti | johtopäätös ensin; toimiva ohjelmisto, ennuste, riskit |
| retrospektiivi | yksi kokeilu, omistaja, tarkistus seuraavalla kerralla |
| viestintäpolut | $n(n-1)/2$; tiimi enintään noin kymmenen |
| Brooksin laki | lisäväki ajoissa tai ei lainkaan |
| mittarit | tiimille, ei yksilöille; tavoitteeksi tehty mittari hajoaa |
| kiinteä hinta | toimittaja kantaa riskin ja hinnoittelee sen |
| tuntityö | tilaaja kantaa riskin; vaatii tilaajan ohjausta |
| tavoitehinta | ylitys ja alitus jaetaan |
| lopetus | uponnut kustannus ei ole syy jatkaa |
