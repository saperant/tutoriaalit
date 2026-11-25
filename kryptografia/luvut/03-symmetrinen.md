# Symmetrinen salaus

Symmetrisessä salauksessa sama avain salaa ja purkaa. Se on nopeaa:
nykyinen suoritin salaa AES-GCM:llä useita gigatavuja sekunnissa
laitteistokäskyjen (AES-NI, ARMv8 Crypto) avulla. Kaikki suuret
tietomäärät salataan symmetrisesti; julkisen avaimen menetelmillä
sovitaan vain symmetrinen avain.

## Lohkosalain ja virtasalain

**AES** (*Advanced Encryption Standard*, 2001) on *lohkosalain*: se
muuntaa 16 tavun lohkon toiseksi 16 tavun lohkoksi avaimen
(128, 192 tai 256 bittiä) ohjaamana. Yksi lohko ei riitä viesteille,
joten lohkosalainta käytetään jossakin *toimintatilassa*.

**ChaCha20** on *virtasalain*: se tuottaa avaimesta ja noncesta
näennäissatunnaisen *avainvirran*, joka XORataan selvätekstiin.
ChaCha20 on nopea myös ilman AES-laitteistokäskyjä, ja siksi sitä
käytetään esimerkiksi mobiililaitteissa ja WireGuardissa.

Salaimen turvallisuutta arvioidaan sen mukaan, mitä hyökkääjän
oletetaan pystyvän tekemään. Pelkän salatekstin näkeminen on heikoin
oletus. Käytännössä hyökkääjä usein tuntee osan selvätekstistä
(*tunnettu selväteksti*: tiedostomuotojen otsakkeet, protokollien
vakiokentät) tai saa järjestelmän salaamaan valitsemaansa dataa
(*valittu selväteksti*: hän lähettää viestin, jonka palvelu salaa ja
tallentaa). Nykyaikaiselta salaukselta vaaditaan, että hyökkääjä ei
näissäkään tilanteissa pysty erottamaan kahden viestin salatekstejä
toisistaan. Vaatimuksesta seuraa, että saman viestin salaaminen kahdesti
ei saa tuottaa samaa tulosta. Siksi salaus tarvitsee avaimen lisäksi
kertakäyttöisen arvon, *noncen* tai *alustusvektorin* (IV), ja siksi
ECB-tila alla ei kelpaa.

## Toimintatilat

Toimintatila kertoo, miten 16 tavun lohkosalaimella salataan pidempi
viesti. Kaaviossa *P* on selvätekstilohko, *C* salattu lohko ja plus
ympyrässä XOR-operaatio:

```{.dot otsikko="Kolme toimintatilaa kahdelle lohkolle. ECB:ssä lohkot ovat toisistaan riippumattomia, CBC ketjuttaa edellisen salatun lohkon seuraavaan, ja CTR tekee lohkosalaimesta virtasalaimen."}
digraph {
  nodesep=0.35; ranksep=0.28;
  node [width=0.55, height=0.3];
  subgraph cluster_ecb { label="ECB"; style=dashed;
    node [shape=plain, style=""];
    e_p1 [label="P1"]; e_p2 [label="P2"]; e_c1 [label="C1"]; e_c2 [label="C2"];
    node [shape=box, style="rounded,filled"];
    e_a1 [label="AES"]; e_a2 [label="AES"];
    e_p1 -> e_a1 -> e_c1; e_p2 -> e_a2 -> e_c2;
    { rank=same; e_p1 -> e_p2 [style=invis]; }
  }
  subgraph cluster_cbc { label="CBC"; style=dashed;
    node [shape=plain, style=""];
    b_iv [label="IV"]; b_p1 [label="P1"]; b_p2 [label="P2"];
    b_c1 [label="C1"]; b_c2 [label="C2"];
    node [shape=circle, style=filled, fixedsize=true, width=0.26, label="+"];
    b_x1; b_x2;
    node [shape=box, style="rounded,filled", fixedsize=false, width=0.55, label="AES"];
    b_a1; b_a2;
    b_p1 -> b_x1 -> b_a1 -> b_c1; b_p2 -> b_x2 -> b_a2 -> b_c2;
    { rank=same; b_p1 -> b_p2 [style=invis]; }
    { rank=same; b_iv -> b_x1; b_x1 -> b_x2 [style=invis]; }
    b_c1 -> b_x2 [constraint=false];
  }
  subgraph cluster_ctr { label="CTR"; style=dashed;
    node [shape=plain, style=""];
    c_n1 [label="nonce, 1"]; c_n2 [label="nonce, 2"];
    c_p1 [label="P1"]; c_p2 [label="P2"]; c_c1 [label="C1"]; c_c2 [label="C2"];
    node [shape=box, style="rounded,filled", label="AES"];
    c_a1; c_a2;
    node [shape=circle, style=filled, fixedsize=true, width=0.26, label="+"];
    c_x1; c_x2;
    c_n1 -> c_a1 -> c_x1 -> c_c1; c_n2 -> c_a2 -> c_x2 -> c_c2;
    { rank=same; c_n1 -> c_n2 [style=invis]; }
    { rank=same; c_p1 -> c_x1; c_x1 -> c_p2 [style=invis]; c_p2 -> c_x2; }
  }
}
```

| Tila | Toiminta | Huomio |
|------|----------|--------|
| ECB | jokainen lohko salataan erikseen | paljastaa rakenteen, älä käytä |
| CBC | lohko XORataan edelliseen salattuun ennen salausta | satunnainen IV, täyte, ei eheyttä |
| CTR | AES salaa laskurin, tulos on avainvirta | nonce ei saa toistua, ei eheyttä |
| GCM | CTR + tunniste (GHASH) | AEAD, luku 4 |

### ECB paljastaa rakenteen

ECB-tilassa sama selvätekstilohko tuottaa aina saman salatun lohkon.
Esimerkissä viisirivinen "kuva" salataan kolmessa tilassa, ja jokainen
salattu lohko korvataan kirjaimella sen mukaan, onko sama lohko nähty
aiemmin:

```{.python tiedosto="esimerkit/03-ecb.py" osa="tilat"}
```

```{.tuloste tiedosto="esimerkit/03-ecb.odotettu"}
```

ECB:n tulos `A B C B A` toistaa kuvan rakenteen: rivit 1 ja 5 sekä 2 ja
4 ovat samat. Oikealla kuvalla ilmiö näkyy silmällä. Alla sama
harmaasävykuva on salattu AES:llä kahdessa tilassa ja salatut tavut on
piirretty takaisin pikseleiksi:

![Tasaisia pintoja sisältävä kuva selvätekstinä ja salattuna. ECB:ssä
sama 16 pikselin lohko tuottaa aina saman salatun lohkon, joten kuvion
ääriviivat säilyvät. CTR:n tulos ei eroa kohinasta. Kuvan tuottaa
`kuvat/piirra.py`.](kuvat/ecb.png){width=92%}

Sama ongelma koskee tietokantakenttiä: ECB-salattu sukupuoli tai
postinumero paljastaa ryhmät. CBC ja CTR satunnaistavat tuloksen.

### Salaus ei suojaa eheyttä

CTR-tilassa salattu teksti on selväteksti XOR avainvirta. Hyökkääjä,
joka tuntee viestin muodon, voi muuttaa haluamaansa kohtaa tuntematta
avainta. Taidossa *Tietoturvan perusteet* sama näytettiin
havainnollistavalla XOR-salaimella; tässä salain on oikea AES-CTR, ja
tulos on sama:

```{.python tiedosto="esimerkit/03-ctr-muokkaus.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/03-ctr-muokkaus.odotettu"}
```

Tätä kutsutaan *muokattavuudeksi* (*malleability*). CBC-tila on
samassa asemassa: salatun lohkon bitin kääntäminen kääntää saman bitin
seuraavassa selvätekstilohkossa. Ratkaisu on autentikoitu salaus
(luku 4).

### Noncen uudelleenkäyttö

Jos sama avain ja nonce salaavat kaksi viestiä, avainvirta on sama, ja
se kumoutuu, kun salatut viestit XORataan keskenään:

```{.python tiedosto="esimerkit/03-nonce-uudelleen.py" osa="virhe"}
```

```{.python tiedosto="esimerkit/03-nonce-uudelleen.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/03-nonce-uudelleen.odotettu"}
```

Tämä on yksi yleisimmistä todellisista virheistä: kovakoodattu nonce,
nollasta alkava laskuri jokaisessa prosessissa tai virtuaalikoneen
tilannevedoksesta palautettu laskuri. GCM-tilassa noncen toisto
paljastaa myös tunnisteavaimen, jolloin hyökkääjä voi väärentää
viestejä.

## Salaus komentorivillä

OpenSSL:n `enc`-komento salaa tiedoston salasanalla. Salasanasta
johdetaan avain PBKDF2:lla, ja satunnainen suola tallennetaan tiedoston
alkuun:

```{.bash tiedosto="esimerkit/03-openssl-enc.sh" osa="enc"}
```

```{.tuloste tiedosto="esimerkit/03-openssl-enc.odotettu"}
```

`openssl enc` ei tue AEAD-tiloja eikä siksi huomaa muutoksia.
Tiedostojen salaamiseen kannattaa käyttää työkaluja, jotka on tehty
siihen: **age** (moderni, yksinkertainen), **GnuPG** tai
salausavaimet hallitseva tallennusratkaisu.

## Käytännössä

- **Ei koskaan ECB:tä.** Monen kirjaston oletustila on historiallisista
  syistä ECB (esim. Javan `Cipher.getInstance("AES")`). Tila valitaan
  aina itse.
- **Ei pelkkää salausta.** CBC ja CTR ilman MAC:ia ovat muokattavissa,
  ja CBC on lisäksi altis täyteoraakkelihyökkäykselle (luku 11).
  Käytetään AEAD:ta.
- **Avaimen pituus:** AES-128 riittää nykyisiä hyökkäyksiä vastaan;
  AES-256 on yleinen oletus, koska se säilyttää marginaalin myös
  kvanttitietokoneita vastaan (luku 12) ja maksaa vain noin 40 %
  enemmän laskentaa.
- **Avain ei ole salasana.** Avain on 16–32 satunnaista tavua. Jos
  lähtökohta on salasana, avain johdetaan siitä hitaalla funktiolla
  (luku 6).
- **Hinta:** laitteistotuetulla AES:llä salaus maksaa alle tavun kohti
  yhden kellojakson; salauksen poistaminen suorituskykysyistä on lähes
  aina väärä säästökohde.

## Itsearviointi

- Osaat selittää, miksi ECB paljastaa rakenteen ja miksi CBC ja CTR
  eivät.
- Osaat näyttää, miten CTR-salattua viestiä muokataan ilman avainta,
  ja perustella, miksi salaus tarvitsee eheyssuojan.
- Osaat kertoa, mitä noncen uudelleenkäytöstä seuraa virtasalaimessa.
- Osaat salata ja purkaa tiedoston OpenSSL:llä ja tiedät, miksi se ei
  riitä eheyden suojaamiseen.
