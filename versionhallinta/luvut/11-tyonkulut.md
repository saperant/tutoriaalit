# Työnkulut ja repositorion rakenne

Git ei määrää, miten tiimi käyttää haaroja. Työnkulku on sopimus siitä,
mihin muutokset tehdään, miten ne yhdistetään ja mistä julkaistaan. Hyvä
työnkulku pitää päähaaran aina toimivana ja yhdistämisen pienenä.

## Runkopohjainen kehitys

Runkopohjaisessa kehityksessä (trunk-based development) kaikki
yhdistävät muutoksensa päähaaraan vähintään päivittäin. Haarat ovat
lyhytikäisiä, usein vain pull requestin ajan. Keskeneräinen ominaisuus
piilotetaan *ominaisuuslipulla* (feature flag) eikä pitkällä haaralla.
Päähaara on aina julkaisukelpoinen, koska CI testaa jokaisen muutoksen.

```{.bash tiedosto="esimerkit/11-runko.sh" osa="lyhyet"}
```

Käytännöt, joiden varassa malli toimii (pienet erät, ominaisuusliput ja
jokaisen muutoksen testaava CI-putki), käsitellään taidossa *Jatkuva
integraatio ja toimitus*.

`--first-parent` seuraa vain päähaaran omia askeleita, joten jokainen
ominaisuus näkyy yhtenä rivinä, vaikka haaroissa oli useampi commit.
Julkaisuhaara tehdään tarvittaessa tagista vain korjauksia varten, ja
korjaukset tuodaan päähaarasta cherry-pickillä (luku *Historian
tutkiminen ja korjaaminen*):

```{.bash tiedosto="esimerkit/11-runko.sh" osa="julkaisu"}
```

```{.tuloste tiedosto="esimerkit/11-runko.odotettu"}
```

## Muut työnkulut

| Työnkulku | Rakenne | Sopii |
|-----------|---------|-------|
| Runkopohjainen | Päähaara + tunnin–päivän haarat, liput | Jatkuva toimitus, palvelut |
| GitHub flow | Päähaara + ominaisuushaarat pull requesteina | Useimmat tiimit |
| Git flow | `main`, `develop`, ominaisuus-, julkaisu- ja korjaushaarat | Monta tuettua versiota rinnakkain |
| Fork-malli | Jokaisella oma kopio, pull requestit alkuperäiseen | Avoin lähdekoodi |

Git flow syntyi aikana, jolloin julkaisut olivat harvinaisia. Jatkuvasti
käyttöön otettavalle palvelulle sen pitkäikäiset haarat ovat raskaita, ja
sen kehittäjäkin suosittelee niihin yksinkertaisempaa mallia.
Pakettikirjastossa tai laiteohjelmistossa, jossa tuetaan useaa versiota,
julkaisuhaaroista on hyötyä.

## Monorepo ja polyrepo

*Monorepossa* useat projektit (palvelut, kirjastot) ovat yhdessä
repositoriossa. *Polyrepossa* jokainen on omansa.

- **Monorepo:** yksi muutos voi päivittää kirjaston ja kaikki sen
  käyttäjät kerralla (atominen muutos), ja työkalut ja säännöt ovat
  yhteiset. Hintana on koko: CI:n on osattava testata vain muuttunut osa,
  ja kloonaus kasvaa.
- **Polyrepo:** selkeät omistajuus- ja oikeusrajat, ja jokainen repositorio
  on pieni. Hintana on, että ristiin menevät muutokset vaativat
  koordinoituja versioita ja pull requesteja useaan repositorioon.

Suuressa monorepossa ei tarvitse ladata eikä purkaa kaikkea. Osittainen
työhakemisto (`sparse-checkout`) purkaa vain valitut hakemistot, ja
osittainen kloonaus (`--filter=blob:none`) hakee tiedostojen sisällön
vasta tarvittaessa:

```{.bash tiedosto="esimerkit/11-monorepo.sh" osa="sparse"}
```

*Työpuu* (worktree) on repositorion toinen työhakemisto, jossa on eri
haara. Se ei liity monorepoon vaan sopii mihin tahansa repositorioon:
kiireellisen korjauksen voi tehdä omassa hakemistossaan ilman toista
kloonia ja koskematta keskeneräiseen työhön. Suuressa repositoriossa
hyöty on suurin, koska toinen klooni olisi kallis:

```{.bash tiedosto="esimerkit/11-monorepo.sh" osa="worktree"}
```

```{.tuloste tiedosto="esimerkit/11-monorepo.odotettu"}
```

## Käytännössä

- **Valitse yksinkertaisin toimiva malli.** Useimmille tiimeille riittää
  GitHub flow: päähaara, lyhyet haarat, pull requestit, CI ja
  haarasuojaus.
- **Päähaara toimii aina.** Rikkinäinen päähaara pysäyttää kaikki. CI
  ajetaan jokaiselle pull requestille ja haarasuojaus estää
  yhdistämisen ilman vihreää tulosta.
- **Lipuilla, ei haaroilla.** Pitkä ominaisuushaara kerää konflikteja.
  Ominaisuuslippu yhdistää keskeneräisen koodin päähaaraan pois päältä,
  ja lipun poistaminen kuuluu työhön.
- **CODEOWNERS ja omistajuus.** Monorepossa tiedosto `CODEOWNERS` ohjaa
  katselmoinnit oikeille tiimeille. Sen tietoturvanäkökulmat käsitellään
  taidossa *Tietoturva kehitystyössä*.

## Itsearviointi

- Osaat kuvata runkopohjaisen kehityksen, GitHub flow'n ja Git flow'n ja
  valita niistä tiimille sopivan.
- Osaat lukea päähaaran historian `--first-parent`illa ja ylläpitää
  julkaisuhaaraa korjauksia varten.
- Osaat perustella monorepon ja polyrepon valinnan ja käyttää
  `sparse-checkout`ia ja `worktree`tä.
