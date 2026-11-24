# Prosessit ja tapahtumat

SystemC-mallin rinnakkaisuus on *yhteistoiminnallista* (*cooperative*):
simulaattori ajaa yhden prosessin kerrallaan samassa käyttöjärjestelmän
säikeessä, ja prosessi luovuttaa vuoron vain palaamalla (metodi) tai
kutsumalla `wait()` (säie). Tämä tekee mallista deterministisen ja
lukkoja ei tarvita, mutta prosessi, joka ei koskaan luovuta vuoroa,
pysäyttää koko simuloinnin. Prosessit heräävät *tapahtumista*
(`sc_event`), ja tämä luku käy läpi, miten tapahtumat ilmoitetaan ja
miten niitä odotetaan.

## Prosessityypit

| Tyyppi | Suoritus | Odotus | Tyypillinen käyttö |
|--------------|------------------------|--------------------|--------------------------------|
| `SC_METHOD` | alusta loppuun joka herätyksellä | ei voi odottaa; `next_trigger()` | kombinaatiologiikka, rekisterit, nopeat reaktiot |
| `SC_THREAD` | kerran, voi pysähtyä | `wait(...)` | testipenkit, protokollat, prosessorimallit |
| `SC_CTHREAD` | säie, herkkä yhdelle kellonreunalle | `wait()` = seuraava reuna | syklitarkka malli, HLS-työkalujen syöte |

`SC_CTHREAD` on säie, jonka ainoa herkkyys on kellonreuna. Se on
vanhempi muoto, jota käytetään lähinnä korkean tason synteesin
syötteenä; tavallisessa mallinnuksessa `SC_THREAD` kellon reunalle
herkkänä tekee saman. Prosesseja voi luoda myös simuloinnin aikana
funktiolla `sc_spawn`, mikä on kätevää esimerkiksi testipenkissä, joka
käynnistää yhden säikeen kutakin transaktiota kohden.

## Odotus ja herkkyys

Prosessin *staattinen herkkyys* määrätään rakentimessa `sensitive <<`
-lausekkeilla. *Dynaaminen herkkyys* korvaa sen yhden odotuksen ajaksi:

| Kutsu | Odottaa |
|-------|---------|
| `wait()` | staattisen herkkyyden tapahtumaa |
| `wait(n)` | `n` staattisen herkkyyden tapahtumaa |
| `wait(e)` | tapahtumaa `e` |
| `wait(lista)` | listan tapahtumia (ks. alla) |
| `wait(10, SC_NS)` | aikaa |
| `wait(aika, e)` | tapahtumaa, enintään annetun ajan |
| `wait(SC_ZERO_TIME)` | yhtä delta-sykliä |

Tapahtumalista muodostetaan operaattoreilla: `e1 | e2` odottaa kumpaa
tahansa ja `e1 & e2` molempia, missä järjestyksessä tahansa. Metodissa
samat muodot ovat funktiolla `next_trigger(...)`: se ei pysäytä
metodia vaan valitsee, mikä herättää sen seuraavan kerran.

## Kolme tapaa ilmoittaa

Tapahtuman voi ilmoittaa kolmella tavalla, ja ero vaikuttaa siihen,
milloin odottajat heräävät:

```{.cpp tiedosto="esimerkit/02-tapahtumat/main.cpp" osa="ilmoitukset"}
```

- `notify()` on *välitön* ilmoitus: odottajat tulevat ajettaviksi samassa
  arviointivaiheessa, ennen kuin simulaattori päivittää signaalit.
- `notify(SC_ZERO_TIME)` on *delta-ilmoitus*: odottajat heräävät
  seuraavassa delta-syklissä, samalla simulaatiohetkellä.
- `notify(5, SC_NS)` on *ajastettu* ilmoitus.

Funktio `triggered()` kertoo metodille, mikä tapahtumista herätti sen.
Tulosteen ensimmäiset rivit näyttävät eron; delta-laskuri on simulaattorin
oma, ja se kasvaa myös, kun aika siirtyy eteenpäin:

```{.tuloste tiedosto="esimerkit/02-tapahtumat/odotettu"}
```

Jos samaa tapahtumaa ilmoitetaan monta kertaa ennen kuin se tapahtuu,
aikaisin ilmoitus voittaa ja muut unohtuvat. Tapahtuma ei siis ole
laskuri eikä jono: kaksi ajastettua ilmoitusta eri hetkille herättää
odottajan vain kerran, aikaisemmalla hetkellä.

## Aikaraja

Säie voi odottaa tapahtumaa enintään annetun ajan. Valvoja odottaa
kunkin työn valmistumista 50 ns:

```{.cpp tiedosto="esimerkit/02-tapahtumat/main.cpp" osa="valvoja"}
```

Herättyään säie tarkistaa `triggered()`-funktiolla, kumpi ehto täyttyi.
Kolmas työ kestää 60 ns, joten valvoja raportoi 105 ns:n kohdalla
aikarajan ylittyneen ja seuraavalla kierroksella työn valmistuneen.
Sama rakenne mallintaa vahtikoiran (*watchdog*), väylän aikarajan ja
protokollan uudelleenyrityksen.

## Tapahtumalla ei ole muistia

Yleisin tapahtumiin liittyvä virhe on ilmoitus, jota kukaan ei vielä
odota:

```{.cpp tiedosto="esimerkit/02-tapahtumat/main.cpp" osa="hukattu"}
```

Lähettäjä ilmoittaa hetkellä 200 ns, mutta vastaanottaja alkaa odottaa
vasta 201 ns:n kohdalla, eikä ilmoitusta ole enää olemassa.
Vastaanottaja odottaa aikarajaan asti ja raportoi ilmoituksen hukkuneen.
Sama virhe syntyy samalla simulaatiohetkellä, jos lähettäjä ajetaan
ennen vastaanottajaa, ja silloin tulos riippuu prosessien
ajojärjestyksestä, jota standardi ei määrää. Korjaus on tallentaa tila
johonkin, jolla on muisti: signaaliin, lippuun tai jonoon (luku 5), ja
odottaa tapahtumaa vain, jos tila ei vielä ole halutunlainen.

## Dynaaminen herkkyys metodissa

Metodi ei voi odottaa, mutta se voi vaihtaa herkkyytensä seuraavaa
kertaa varten:

```{.cpp tiedosto="esimerkit/02-tapahtumat/main.cpp" osa="seuraaja"}
```

Joka toisella kutsulla metodi pyytää heräämään 25 ns:n kuluttua
kellon sijaan. Jos `next_trigger()`-kutsua ei tehdä, seuraava herätys
tulee staattisesta herkkyydestä. Tulosteen viimeiset rivit näyttävät
herätykset: 250 ns ja 260 ns kellosta, 285 ns tauon jälkeen ja 290 ns
taas kellosta.

## Käytännössä

- **Tila ensin, tapahtuma sitten.** Odottava koodi kirjoitetaan
  muotoon `while (!ehto) wait(muuttui);`. Silmukka suojaa sekä hukatulta
  ilmoitukselta että herätykseltä, jonka jälkeen ehto ei vieläkään
  täyty. Sama malli on tuttu ehtomuuttujista (*condition variable*).
- **Delta-ilmoitus oletuksena.** `notify(SC_ZERO_TIME)` tekee tuloksesta
  riippumattoman siitä, missä järjestyksessä samalla hetkellä ajettavat
  prosessit suoritetaan. Välitöntä ilmoitusta käytetään vain, kun on
  varmaa, että odottaja on jo odottamassa, kuten kanavan sisällä.
- **Älä pyöri odottamatta.** Säie, jonka silmukassa ei ole `wait()`-
  kutsua, jumittaa simuloinnin, koska muut prosessit eivät koskaan saa
  vuoroa. Kyselysilmukkaankin (*polling*) kuuluu odotus, esimerkiksi
  yksi kellojakso.
- **Säikeet maksavat.** Jokaisella `SC_THREAD`illa on oma pinonsa
  (kymmeniä tai satoja kilotavuja, koko asetetaan tarvittaessa
  funktiolla `set_stack_size`), ja kontekstinvaihto on moninkertaisesti
  metodikutsua kalliimpi. Tuhansia samanlaisia lohkoja sisältävässä
  mallissa metodit ovat selvästi nopeampia.
- **Ei satunnaisuutta ajojärjestyksestä.** SystemC:n referenssitoteutus
  ajaa prosessit aina samassa järjestyksessä, mutta järjestys ei ole
  standardin takaama. Malli, jonka tulos muuttuu, jos järjestys vaihtuu,
  on virheellinen, vaikka se toimisi tänään.

## Itsearviointi

- Osaat selittää välittömän, delta- ja ajastetun ilmoituksen eron ja
  valita niistä oikean.
- Osaat kirjoittaa säikeen, joka odottaa tapahtumaa aikarajan kanssa ja
  tunnistaa, kumpi herätti sen.
- Osaat selittää, miksi tapahtuma voi hukkua, ja kirjoittaa odotuksen,
  joka ei ole altis sille.
- Osaat muuttaa metodin herkkyyttä `next_trigger()`-kutsulla.
