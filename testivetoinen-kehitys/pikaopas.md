---
title: Testivetoinen kehitys ja testisuunnittelu
subtitle: Pikaopas · TDD · tekniikat · BDD · ominaisuudet · mutaatiot · saumat
---

# TDD

1. **Punainen:** yksi pieni testi, joka epäonnistuu oikeasta syystä.
2. **Vihreä:** yksinkertaisin koodi, jolla testi menee läpi.
3. **Refaktorointi:** rakenne paranee, testit pysyvät vihreinä.

```{.python tiedosto="esimerkit/02-tdd/8-refaktorointi/test_kori.py" osa="taulukko"}
```

- Testilista ensin; yksi testi kerrallaan.
- Kolmiointi: toinen esimerkki pakottaa yleistämään.
- Vian korjaus alkaa testistä, joka toistaa vian.
- Ei sovi: tutkiva koodi, ulkoasu, ohut liima.

| Tarkistus | Kestää refaktoroinnin | Käytä, kun |
|-----------|-----------------------|------------|
| tila | hyvin | kumppani on nopea tai väärennettävissä |
| vuorovaikutus | huonosti | kutsu itse on vaatimus |

`Mock(spec=Luokka)` aina. Älä mockaa sitä, mitä et omista.

# Testisuunnittelu

| Tekniikka | Ongelma | Testit |
|-----------|---------|--------|
| ekvivalenssiluokat | paljon samanlaisia syötteitä | edustaja luokasta; kelvottomat yksi kerrallaan |
| raja-arvot | vertailut ja vakiot | rajan molemmat puolet |
| päätöstaulu | ehtojen yhdistelmät | sarake jokaiselle yhdistelmälle |
| tilasiirtymät | järjestyksestä riippuva käytös | sallitut *ja* kielletyt siirtymät |
| parit | riippumattomat asetukset | jokainen arvopari kerran |

```{.python tiedosto="esimerkit/04-rajat/test_3_rajat.py" osa="rajat"}
```

Piilorajat: tyhjä, yksi, nolla, negatiivinen, suurin arvo, keskiyö,
kuun vaihde, karkauspäivä, ääkköset.

# BDD

Esimerkkikartoitus: sääntö → esimerkit → avoimet kysymykset.

```text
# language: fi
Tapaus: Kevyt tilaus lähetetään pienenä pakettina
  Oletetaan että korin arvo on 20,00 euroa
  Ja korin paino on 1,5 kg
  Kun asiakas siirtyy kassalle
  Niin toimitusmaksu on 5,90 euroa
```

- Yksi tapaus, yksi sääntö, yksi *Kun*.
- Kuvaa käytös, älä klikkauksia.
- Askeleet ovat ohut liima; logiikka sovellukseen.
- Kannattaa, kun joku muu kuin ohjelmoija lukee tapaukset.

# Ominaisuustestit

| Malli | Väite |
|-------|-------|
| edestakaisuus | `jasenna(muotoile(x)) == x` |
| invariantti | osien summa säilyy |
| oraakkeli | nopea toteutus = hidas ja selvä |
| tilakone | olio vastaa mallia joka askeleella |

```{.python tiedosto="esimerkit/07-ominaisuudet/1-viallinen/test_2_ominaisuudet.py" osa="invariantti"}
```

```{.python tiedosto="esimerkit/07-ominaisuudet/1-viallinen/conftest.py" osa="profiili"}
```

Pienennetty vastaesimerkki pysyväksi: `@example(...)`.

# Kattavuus ja mutaatiot

- Kattavuus kertoo, mitä testit *suorittavat*. Lue aukot, älä prosenttia.
- Mutantti = yksi pieni muutos koodiin. Tapettu, jos jokin testi
  epäonnistuu.
- Henkiin jäänyt mutantti rajalla = puuttuva rajatesti.
- Ekvivalenttia mutanttia ei voi tappaa; 100 % ei ole tavoite.
- Työkalut: mutmut, cosmic-ray, PIT, Stryker. Aja muuttuneelle koodille.

# Testattava suunnittelu

```{.python tiedosto="esimerkit/09-saumat/jalkeen.py" osa="kuori"}
```

- Päätökset puhtaaseen ytimeen, sivuvaikutukset ohueen kuoreen.
- Aika (`datetime`) ja satunnaisuus (`random.Random`) argumentteina.
- Palvelut konstruktorissa; testissä väärennös.
- `monkeypatch` vain perintökoodin ensimmäiseen testiin.

# Perintökoodi

1. Valitse syötteet haaroista ja vakioista.
2. Tallenna nykyiset tulosteet (kultainen tiedosto).
3. Refaktoroi pienin askelin; vertailu pysyy vihreänä.
4. Käytöksen muutos erikseen; päivitä tiedosto tietoisesti.
5. Korvaa ajan mittaan nimetyillä yksikkötesteillä.

# Hyvä testi

| Haju | Korjaus |
|------|---------|
| `test_1` | nimi kertoo tilanteen ja odotuksen |
| monta käytöstä | yksi käytös testiä kohden |
| `olio._sisus` | julkinen rajapinta |
| kaava odotuksena | kirjattu luku |
| jaettu tila | testi luo oman tilansa |
| `if`, `for` | parametrointi |
| `sleep` | väärennetty kello |

Rakenne: alkutilanne, toiminto, väite. Katso testin epäonnistuvan.
