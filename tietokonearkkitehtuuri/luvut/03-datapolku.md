# Datapolku ja ohjaus

Käskykanta kertoo, mitä käskyn on tehtävä. Datapolku (*datapath*) on
laitteisto, joka sen tekee: rekisterit, ALU, muistit ja niitä yhdistävät
multiplekserit. Ohjausyksikkö (*control unit*) asettaa multiplekserien
valinnat ja kirjoitussallinnat käskyn perusteella. Tässä luvussa
rakennetaan RV32I:lle ensin yksijaksoinen toteutus, jossa jokainen käsky
valmistuu yhdessä pitkässä kellojaksossa, ja sitten monijaksoinen, jossa
käsky kulkee lyhyiden jaksojen sarjana. Luku 4 jatkaa tästä
liukuhihnaan.

Rakennuspalikat (rekisteritiedosto, ALU, multiplekseri, kiikku) on
käsitelty taidossa *Digitaalitekniikka*. Tässä ne oletetaan valmiiksi.

## Yksijaksoinen datapolku

Kaikki käskyt kulkevat saman reitin, vaikka jokainen ei käytä jokaista
osaa:

```{.dot otsikko="Yksijaksoinen datapolku. Suluissa ja multipleksereissä ovat ohjaussignaalit, jotka ohjausyksikkö asettaa opcoden perusteella"}
digraph {
  rankdir=LR; nodesep=0.22; ranksep=0.2;
  edge [fontsize=8];
  node [fontsize=9, margin="0.04,0.03", width=0.3, height=0.3];
  MP [label="mux\nha, hy", shape=box];
  PC;
  P4 [label="+4", shape=circle, fixedsize=true, width=0.32];
  HS [label="+", shape=circle, fixedsize=true, width=0.32];
  IM [label="käsky-\nmuisti"];
  OHJ [label="ohjaus-\nyksikkö", shape=box, style=dashed];
  PU [label="purku\n+ imm"];
  RF [label="rekisteri-\ntiedosto\n(rk)"];
  MA [label="mux\na", shape=box];
  MB [label="mux\nb", shape=box];
  ALU [label="ALU\n(alu)", shape=invtrapezium];
  DM [label="data-\nmuisti\n(ml, mk)"];
  MW [label="mux\nwb", shape=box];
  MP -> PC -> IM -> PU -> RF;
  IM -> OHJ [label="opcode", style=dotted];
  RF -> MA [label="rs1"]; RF -> MB [label="rs2"];
  PU -> MB [label="imm"];
  PC -> MA [constraint=false];
  MA -> ALU; MB -> ALU;
  ALU -> DM [label="osoite"];
  RF -> DM [label="rs2", constraint=false];
  DM -> MW; ALU -> MW;
  PC -> P4; P4 -> MW [label="PC+4"];
  PC -> HS; PU -> HS [label="imm", constraint=false];
  P4 -> MP [constraint=false]; HS -> MP [label="haaran kohde", constraint=false];
  ALU -> MP [label="hypyn kohde", constraint=false, style=dashed];
  MW -> RF [label="rd", constraint=false, style=dashed];
}
```

Kuvasta on jätetty pois A-operandin kolmas vaihtoehto (vakio nolla,
jota `lui` käyttää) ja ohjausyksikön johtimet multiplekserien
valintoihin. Käsky kulkee kuvan läpi viidessä vaiheessa:

1. **Nouto** (IF): ohjelmalaskuri osoittaa käskymuistiin, käsky luetaan.
2. **Purku** (ID): kentät erotetaan, rekisteritiedostosta luetaan rs1 ja
   rs2, välittömän arvon generaattori kokoaa ja laajentaa imm:n.
3. **Suoritus** (EX): ALU laskee tuloksen, muistiosoitteen tai
   haaraehdon; erillinen summain laskee haaran kohteen PC + imm.
4. **Muisti** (MEM): lataus lukee tai talletus kirjoittaa datamuistiin.
5. **Takaisinkirjoitus** (WB): tulos kirjoitetaan rekisteriin rd.

Käsky- ja datamuistit ovat erillisiä (Harvard-rakenne), jotta nouto ja
datan lataus voivat tapahtua samassa jaksossa. Oikeassa suorittimessa
nämä ovat erilliset L1-välimuistit yhteisen keskusmuistin edessä
(*modified Harvard*).

## Ohjausyksikkö

Ohjausyksikkö on kombinaatiologiikkaa, jonka syöte on opcode (ja ALU:n
osalta funct3 ja funct7) ja tuloste joukko ohjaussignaaleja:

```{.cpp tiedosto="esimerkit/03-ohjaus.cpp" osa="signaalit"}
```

Signaalit taulukkona:

```{.cpp tiedosto="esimerkit/03-ohjaus.cpp" osa="taulu"}
```

```{.tuloste tiedosto="esimerkit/03-ohjaus.odotettu" rivit="1-10"}
```

Lyhenteet: `rk` rekisteriin kirjoitus, `a` ALU:n A-operandi (rs1, pc tai
nolla), `b` B-operandi (rekisteri tai välitön), `ml` ja `mk` muistin
luku ja kirjoitus, `wb` takaisinkirjoitettava arvo (ALU, muisti tai
PC + 4), `ha` haara, `hy` hyppy, `imm` välittömän arvon muoto ja `alu`
ALU-ohjauksen taso.

Taulukosta näkee, miksi käskymuotoja on vähän ja ne ovat säännöllisiä:
ohjaus on muutaman rivin totuustaulu. Huomioita:

- `lui` käyttää ALU:ta laskemaan 0 + imm, `auipc` laskee pc + imm.
  Sama summain palvelee molempia, kun A-operandin multiplekseriin
  lisätään vaihtoehdot pc ja nolla.
- `jal` ja `jalr` kirjoittavat rekisteriin paluuosoitteen PC + 4, ja
  ALU laskee hypyn kohteen. Takaisinkirjoituksen multiplekserissä on
  siksi kolme syötettä.
- ALU-ohjaus on kaksitasoinen. Päädekooderi kertoo vain, lasketaanko
  osoite (`add`), haaraehto (`cmp`) vai funct-kenttien määräämä
  operaatio (`f3f7`). Erillinen pieni ALU-dekooderi muuttaa funct3:n ja
  funct7:n varsinaiseksi operaatioksi. Jako pitää päädekooderin pienenä,
  ja sama ratkaisu on klassisessa MIPS-toteutuksessa.

Laittoman opcoden kohdalla kaikki signaalit ovat nollia: mitään ei
kirjoiteta. Oikeassa toteutuksessa ohjausyksikkö nostaa lisäksi
poikkeuksen (luku 9).

## Kriittinen polku

Yksijaksoisen toteutuksen kellojakso on niin pitkä kuin hitaimman
käskyn polku. Oletetaan vaiheille viiveet:

| Vaihe | Viive (ps) | Mitä tapahtuu |
|-------|------------|---------------|
| IF | 200 | käskymuistin luku |
| ID | 100 | purku ja rekisterien luku |
| EX | 200 | ALU |
| MEM | 200 | datamuistin luku tai kirjoitus |
| WB | 100 | rekisterin kirjoitus |

Lataus käyttää kaikkia viittä, joten jakso on 800 ps (1,25 GHz),
vaikka yhteenlasku tarvitsisi vain 600 ps ja haara 500 ps. Kaikki
käskyt maksavat hitaimman käskyn hinnan. Lisäksi jokainen uusi
monimutkainen käsky (esimerkiksi kertolasku yhdessä jaksossa) pidentäisi
*kaikkien* käskyjen jaksoa.

## Monijaksoinen toteutus

Ratkaisu on jakaa käsky vaiheisiin, joiden väliin lisätään rekisterit,
ja kellottaa vaiheita nopeasti. Jakso on nyt hitaimman *vaiheen*
pituinen, 200 ps, ja jokainen käsky käyttää vain tarvitsemansa vaiheet:

```{.cpp tiedosto="esimerkit/03-ohjaus.cpp" osa="jaksot"}
```

Ohjausyksikkö on nyt tilakone: tila kertoo, missä vaiheessa käsky on, ja
siirtymä riippuu opcodesta. Kun tiloja on paljon (CISC-suorittimissa
satoja), tilakone kirjoitetaan usein *mikro-ohjelmaksi*: pieneen
ROM-muistiin tallennetuksi taulukoksi, jonka jokainen rivi on yhden
jakson ohjaussignaalit ja seuraavan rivin osoite. Mikro-ohjelmointi
teki 1960-luvulla mahdolliseksi IBM System/360 -perheen, jossa sama
käskykanta toteutettiin hyvin eri hintaisilla koneilla. Nykyiset
x86-suorittimet käyttävät mikrokoodia yhä harvinaisille ja
monimutkaisille käskyille (luku 12).

Monijaksoisuuden etu on myös, että yksi ALU ja yksi muisti riittävät:
sama ALU laskee eri jaksoissa PC + 4:n, haaran kohteen ja varsinaisen
tuloksen.

## Rautalaki käytännössä

Kumpi on nopeampi? Riippuu käskysekoituksesta. Esimerkki ajaa kolme
ohjelmaa, laskee monijaksoisen CPI:n todellisista käskyistä ja vertaa
suoritusaikoja. Mukana on jo seuraavan luvun liukuhihna, jonka jakso
on 220 ps (200 ps vaihe ja 20 ps vaiherekisterien ylimääräinen viive):

```{.cpp tiedosto="esimerkit/03-ohjaus.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-ohjaus.odotettu" rivit="12-18"}
```

Monijaksoinen CPI on noin 4, ja koska jakso on neljäsosa, ajat ovat
lähes samat kuin yksijaksoisessa. Monijaksoisuus ei siis yksinään nopeuta paljoa: se
voittaa vain, jos sekoituksessa on paljon lyhyitä käskyjä (haaroja) tai
jos jotkin käskyt ovat hyvin pitkiä (kerto- ja jakolasku, liukuluvut),
jolloin yksijaksoinen joutuisi venyttämään jokaisen jakson niiden
mukaan. Liukuhihna sen sijaan on noin 2,5 kertaa nopeampi: se säilyttää
lyhyen jakson ja pitää CPI:n lähellä yhtä, koska käskyt limittyvät.

## Käytännössä

- **Jakso määräytyy hitaimmasta polusta.** Sama periaate pätee
  RTL-suunnittelussa: ajoitusanalyysi kertoo kriittisen polun, ja
  suunnittelija joko lyhentää sitä tai jakaa sen vaiheisiin.
- **Pidä ohjaus säännöllisenä.** Säännöllinen koodaus tekee ohjauksesta
  pienen totuustaulun; uusille käskyille valitaan koodaus, joka ei riko
  olemassa olevia ohjaussignaaleja.
- **Yksijaksoinen on hyvä malli, ei hyvä toteutus.** Se kelpaa
  opetukseen ja verifioinnin viitemalliksi; kaupalliset ytimet ovat
  vähintään kolmivaiheisia liukuhihnoja.
- **Mittaa sekoitus.** Rautalain CPI on keskiarvo jostakin
  käskysekoituksesta, eikä "tyypillinen" sekoitus ole sinun ohjelmasi.

## Itsearviointi

- Osaat piirtää yksijaksoisen RV32I-datapolun ja seurata latauksen,
  talletuksen, haaran ja `jal`-käskyn reitin sen läpi.
- Osaat johtaa ohjaussignaalit opcodesta ja selittää, miksi
  takaisinkirjoituksen multiplekserissä on kolme syötettä.
- Osaat laskea yksijaksoisen ja monijaksoisen toteutuksen jakson
  vaiheviiveistä ja verrata niiden suoritusaikoja rautalailla.
