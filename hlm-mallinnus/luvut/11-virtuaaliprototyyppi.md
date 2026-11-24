# Virtuaaliprototyyppi

Edellisten lukujen osat riittävät kokonaiseen järjestelmään: prosessori,
väylä, muisti ja oheislaitteet, ja muistissa ohjelma, jonka prosessori
suorittaa. Tällainen *virtuaaliprototyyppi* on ohjelmistokehittäjälle
laite, jonka voi käynnistää sekunnissa, pysäyttää missä kohdassa tahansa
ja monistaa tuhanteen testikoneeseen. Tämä luku rakentaa pienen
prototyypin, jonka prosessori on RISC-V-käskykannan osajoukon
käskytason simulaattori (ISS).

## Rakenne

| Osa | Malli | Osoite |
|-----|-------|--------|
| prosessori | `Prosessori` (RV32I-osajoukko, LT, DMI) | aloittaja |
| lataaja | `Lataaja` (debug-kirjoitukset) | aloittaja |
| väylä | `Vayla`, viive 5 ns | |
| RAM, 64 kt | `Muisti`, viive 20 ns | `0x0000_0000` |
| sarjaportti | `Uart` | `0x1000_0000` |
| ajastin | `Ajastin`, 100 MHz | `0x1000_1000` |

```{.dot otsikko="Virtuaaliprototyypin rakenne"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.6;
  cpu [label="Prosessori\nRV32I, LT"];
  lataaja [label="Lataaja\ndebug-kirjoitukset"];
  vayla [label="Vayla\nviive 5 ns", style="rounded,filled,bold"];
  ram [label="RAM 64 kt\nviive 20 ns"];
  uart [label="Uart"];
  ajastin [label="Ajastin\n100 MHz"];
  lataaja -> vayla; cpu -> vayla;
  vayla -> ram; vayla -> uart; vayla -> ajastin;
  cpu -> ram [label="DMI", style=dashed, constraint=false];
}
```

Oikeassa virtuaaliprototyypissä prosessorimalli on valmis ja nopea ISS,
kuten QEMU, Spike, Imperas-mallit tai toimittajan oma malli, ja ohjelma
on ristikääntäjällä käännetty ELF-tiedosto. Tässä prosessori on noin
200 rivin malli, jotta sen toiminta näkyy kokonaan, ja ohjelma kootaan
C++:n apuluokalla, jotta esimerkki ei tarvitse ristikääntäjää.

## Prosessorin liitäntä

Prosessori on TLM-aloittaja, joka näkee kaiken väylän kautta:

```{.cpp tiedosto="esimerkit/14-prototyyppi/prosessori.hpp" osa="liitanta"}
```

Kaikki muistiliikenne, myös käskynhaku, kulkee yhden funktion kautta.
RAM-alueella se käyttää DMI-osoitinta, ja oheislaitteiden rekisterit
luetaan transaktioilla. Ensimmäinen RAM-käsky haetaan transaktiolla,
jonka DMI-vihjeen perusteella prosessori pyytää osoittimen:

```{.cpp tiedosto="esimerkit/14-prototyyppi/prosessori.hpp" osa="muistiliikenne"}
```

Väylävirhe on prosessorille kohtalokas: oikea prosessori ottaisi
poikkeuksen, mutta tämä malli ei toteuta poikkeuksia, joten se
pysäyttää simuloinnin ja kertoo osoitteen ja ohjelmalaskurin. Ohjelman
virhe näkyy näin heti eikä vasta oudosti käyttäytyvänä tulosteena.

## Käskyjen suoritus

RISC-V:n käskyt ovat 32-bittisiä, ja niissä on kuusi muotoa (R, I, S, B,
U, J), jotka sijoittavat välittömän arvon (*immediate*) bitit eri
paikkoihin. Apufunktiot `imm_i`, `imm_s`, `imm_b` ja `imm_j` kokoavat ne
takaisin ja laajentavat etumerkin siirtämällä etumerkillistä lukua
oikealle.
Suoritus on yksi `switch` operaatiokoodin mukaan. Malli toteuttaa vain
ne 14 käskyä, joita esimerkkiohjelma käyttää; täysi RV32I on 40 käskyä,
ja tuntematon käsky pysäyttää simuloinnin:

```{.cpp tiedosto="esimerkit/14-prototyyppi/prosessori.hpp" osa="suoritus"}
```

Pääsilmukka hakee käskyn, suorittaa sen ja lisää yhden kellojakson
paikalliseen aikaan. Muistiviiveet lisätään siirroissa, joten käsky,
joka lukee sarjaportin tilarekisteriä, vie yhden jakson lisäksi väylän
ja laitteen viiveen. Ajallinen irrottaminen pitää kontekstinvaihdot
harvoina:

```{.cpp tiedosto="esimerkit/14-prototyyppi/prosessori.hpp" osa="aja"}
```

Ohjelma päättyy käskyyn `ecall`, jonka argumentti `a0` on ohjelman
paluuarvo. Oikea prosessori siirtyisi käyttöjärjestelmän
järjestelmäkutsuun; prototyypeissä vastaavaa *semihosting*-mekanismia
käytetään yleisesti testien lopettamiseen ja tulostukseen.

## Ohjelma

Kokoaja (`rv32.hpp`) on apuluokka, joka koodaa käskyt RISC-V:n
käsikirjan käskymuotojen mukaan ja kerää ne ja datan tavuvektoriin.
Nimiöihin voi viitata ennen niiden määrittelyä; haarautumisten ja
hyppyjen siirtymät ratkaistaan lopuksi, kuten oikea kokoaja ja linkkeri
tekevät. Ohjelma on kirjoitettu kuin assembly, mutta C++:n
funktiokutsuina:

```{.cpp tiedosto="esimerkit/14-prototyyppi/main.cpp" osa="ohjelma"}
```

Aliohjelma `tulosta` on pieni sarjaporttiajuri: se odottaa, että
lähettimen tilabitti on 1, ja kirjoittaa merkin datarekisteriin.
`tulosta_hex` muuttaa luvun heksadesimaaleiksi taulukon avulla. Ohjelma
ja data ovat samassa muistissa, kuten tavallisessa
mikro-ohjainohjelmassa.

## Lataus ja järjestelmä

Lataaja kirjoittaa ohjelman muistiin debug-liikenteellä ennen kuin
prosessori käynnistyy. Funktio `start_of_simulation` on yksi
moduulin elinkaaren takaisinkutsuista: se ajetaan elaboroinnin
jälkeen, kun kaikki kytkennät ovat valmiit, mutta ennen ensimmäistäkään
prosessia.

```{.cpp tiedosto="esimerkit/14-prototyyppi/main.cpp" osa="lataaja"}
```

```{.cpp tiedosto="esimerkit/14-prototyyppi/main.cpp" osa="jarjestelma"}
```

Lopuksi tulostetaan ohjelman koko, paluuarvo ja prosessorin laskemat
tilastot:

```{.tuloste tiedosto="esimerkit/14-prototyyppi/odotettu"}
```

Ohjelma tulostaa rivinsä sarjaporttiin, ja jokaisen rivin aikaleima on
prosessorin paikallinen aika rivin viimeisen merkin hetkellä. Taulukon
neliöiden summa on 1240 = 0x4d8. Ajastin näyttää 1978 jaksoa eli
19,78 µs, mikä on hetki, jolloin ohjelma luki sen.

Tilastot kertovat, mihin aika kuluu. Käskyjä on 615, mutta simulaatioaikaa
26,39 µs eli noin 43 ns käskyä kohden, vaikka käsky vie yhden 10 ns:n
jakson: jokainen käskynhaku maksaa väylän ja muistin 25 ns, ja
sarjaportin rekisterit 25 ns lisää. Oikea prosessori piilottaisi
haun viiveen välimuistilla. Tällainen malli ei siis ennusta
suorituskykyä tarkasti, mutta se näyttää, mitä ohjelma tekee ja
kuinka paljon laitteita se käyttää. Transaktioita on vain 114: niistä
113 on oheislaitteiden rekisterien käyttöjä ja yksi ensimmäinen
käskynhaku, jonka jälkeen kaikki RAM-liikenne kulkee DMI:n kautta.

## Ohjelmistokehitys mallissa

Virtuaaliprototyypin arvo tulee työkaluista, joita sen ympärille
rakennetaan:

- **Debuggeri.** ISS:lle lisätään GDB:n etäprotokolla (*remote serial
  protocol*), jolloin GDB voi pysäyttää prosessorin, lukea rekisterit ja
  muistin (`transport_dbg`) ja asettaa keskeytyskohtia. Koska malli
  pysähtyy kokonaan, myös oheislaitteet pysähtyvät, mikä on oikeassa
  laitteessa mahdotonta.
- **Ohjelman lataus.** ELF-tiedoston osiot luetaan ja kirjoitetaan
  muistiin debug-liikenteellä, kuten tämän luvun lataaja tekee.
- **Jäljitys.** Mallin voi laajentaa kirjaamaan jokaisen käskyn tai
  väylätransaktion. Jäljitystä käytetään sekä virheiden etsintään että
  ohjelman kuorman karakterisointiin (taito *Arkkitehtuurin tutkiminen*).
- **Virheiden injektointi.** Malli voi palauttaa väylävirheen,
  kadottaa keskeytyksen tai kääntää muistibitin hallitusti, ja ajurin
  virheenkäsittelyn voi testata toistettavasti.

## Käytännössä

- **Toiminnallisesti tarkka, ajallisesti karkea.** Virtuaaliprototyypin
  tärkein ominaisuus on, että ohjelmisto näkee saman kuin piirillä:
  samat osoitteet, rekisterit ja sivuvaikutukset. Ajoitus on likimääräinen,
  eikä ohjelmiston pidä riippua siitä.
- **Valmis ISS.** Prosessorimallia ei kannata kirjoittaa itse, jos
  valmis on olemassa. QEMU ja Spike ovat avoimia, ja niiden ympärille on
  tehty SystemC-liitäntöjä; kaupallisista malleista saa myös
  syklitarkkoja versioita.
- **Sama ohjelma piirille ja mallille.** Prototyypille käännetty ohjelma
  on sama binääri kuin piirillä. Jos malli tarvitsee oman versionsa,
  osa ohjelmistosta jää testaamatta.
- **Determinismi on etu.** Sama malli ja sama ohjelma antavat aina
  saman tuloksen, joten jokainen virhe on toistettavissa. Tämä on
  virtuaaliprototyypin suurimpia etuja oikeaan laitteeseen nähden, ja
  se katoaa, jos malli käyttää isäntäkoneen kelloa tai satunnaisuutta.

## Itsearviointi

- Osaat koota virtuaaliprototyypin prosessorista, väylästä, muistista ja
  oheislaitteista ja ladata siihen ohjelman.
- Osaat selittää, miten ISS hakee käskyt ja tekee muistiviittaukset
  TLM:n kautta ja miksi se käyttää DMI:tä ja ajallista irrottamista.
- Osaat lukea prototyypin tilastoista, mihin simulaatioaika ja väylän
  käyttö kuluvat.
- Osaat kertoa, mitä virtuaaliprototyyppi kertoo ohjelmistosta ja mitä
  se ei kerro suorituskyvystä.
