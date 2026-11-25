---
title: Reaaliaikaiset moninpelit
subtitle: Verkkopelin rakenteet tiiviisti
lang: fi
---

# Arkkitehtuuri

| Malli | Hyvä | Huono |
|-------|------|-------|
| vertaisverkko | ei palvelinkuluja, suora reitti | N², ei auktoriteettia, NAT |
| asiakas–palvelin | auktoriteetti, huijausten esto | palvelinkulut |
| isäntä | ei kuluja | isännän etu, isännän kaista |
| lukitusaskel | pieni kaista, paljon yksiköitä | syöteviive, determinismi |

Asiakas lähettää **aikeita** (syötteet), palvelin päättää
**lopputuloksen**.

# Verkko

- RTT = kiertoviive; värinä vaihtaa järjestystä; 1–5 % häviö on
  tavallista.
- Tila UDP:llä, ei TCP:llä: jonopää-ongelma jäädyttää pelin.
- Paketti alle ~1 200 tavua (MTU, ei pilkkomista).

# Yhteys

- Kättely: pyyntö → haaste → vastaus → hyväksytty; paikka varataan
  vasta vastauksesta. Haaste = tiiviste(salaisuus, osoite, asiakkaan
  luku), ei tallenneta.
- Aikakatkaisu ja elossaoloviestit molempiin suuntiin.
- NATin läpi: molemmat lähettävät ensin (reiän avaaminen); varalla
  välityspalvelin.

# Sekvenssinumerot ja kuittaukset

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="sekvenssi"}
```

- Joka paketissa: oma numero, uusin vastaanotettu, 32 bitin kenttä.
- Tapahtumat tunnisteella; uudelleen kunnes kuitattu; kaksoiskappaleet
  pois tunnisteesta.

# Vedokset

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="kvantisointi"}
```

- Kvantisointi → bittipakkaus → delta **kuitattuun** vedokseen →
  kiinnostusalue.
- Prioriteettikertymä täyttää kiinteän pakettibudjetin.

# Oma hahmo: ennustus ja täsmäytys

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="tasmaytys"}
```

- Sama simulaatiokoodi asiakkaalla ja palvelimella.
- Toista 2–3 viimeistä syötettä joka paketissa.
- Kello: `siirtymä = ts + rtt/2 − t1`, paras näyte = pienin rtt.
- Syöte 1–2 tikkiä etuajassa: säädä asiakkaan tahtia ±5 %, älä hyppää.

# Muut pelaajat: interpolointi

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="puskuri"}
```

- Näytä hetki *nyt − puskuri*; ekstrapolointi vain lyhyesti.
- Teleportit ohittavat interpoloinnin.

# Viiveen kompensointi

- Historia osuma-alueista ~1 s; kelaa ampujan näkemään hetkeen.
- Yläraja 200–400 ms: kohteen reiluus ja huijarin viive.

# Lukitusaskel ja rollback

| | Lukitusaskel | Rollback |
|-|-------------|----------|
| puuttuva syöte | odotetaan | arvataan |
| syöteviive | ≥ yhden suunnan viive | 0–3 ruutua |
| hinta | viive | tallennus, uudelleensimulointi |

Determinismi: kokonaisluvut, oma PCG32, kiinteä järjestys,
tarkistussumma joka ruutu.

# Huijaamisen esto

- Tarkista syötteet: pituus, määrä (merkkiämpäri), ehdot.
- Lähetä vain näkyvä (näkölinja, konservatiivisesti).
- Kirjaa poikkeamat, käsittele tilastollisesti.

# Palvelimet

- Elo: `E = 1 / (1 + 10^((Rb − Ra) / 400))`, `Ra += K (S − E)`.
- Glicko-2 / TrueSkill: luokitus + epävarmuus.
- Laajeneva hakuikkuna; alueet pingin mukaan.
- Istunto tilakoneena, armonaika uudelleenliittymiselle.
