# Oikeat kääntäjät

Kide sisältää tuotantokääntäjän kaikki vaiheet pienessä mittakaavassa.
Tämä luku sijoittaa ne GCC:n ja LLVM:n arkkitehtuuriin ja vertaa
tuotettua koodia, jotta näkee, mitä isot kääntäjät tekevät lisää.

## GCC ja LLVM

| Vaihe | Kide | GCC | LLVM ja Clang |
|-------|------|-----|---------------|
| syntaksipuu | `Lauseke`, `Lause` | GENERIC | Clangin AST |
| korkean tason IR | – | GIMPLE (kolmiosoitekoodi) | Clangin CFG analyyseille |
| SSA-muoto | tason `-O2` passit | GIMPLE SSA | LLVM IR (aina SSA) |
| matalan tason IR | välikieli | RTL | SelectionDAG, MachineIR |
| käskyjen valinta | makrolaajennus | konekuvaukset (`.md`) | TableGen-mallit |
| rekisterien varaus | lineaarinen pyyhkäisy | IRA ja LRA | *greedy* |
| tuloste | assembly | assembly | assembly tai suoraan objekti |

GCC:ssä on kaksi päävälikieltä: GIMPLE, joka on Kiden välikielen
kaltaista kolmiosoitekoodia ja jossa kohteesta riippumattomat
optimoinnit tehdään SSA-muodossa, ja RTL, joka on lähellä konekieltä.
LLVM:ssä on yksi keskeinen välikieli, LLVM IR, joka on aina SSA-muodossa
ja jolla on tekstimuoto, binäärimuoto ja muistissa oleva muoto. Tämä
yksi hyvin määritelty välikieli tekee LLVM:stä helpon kohteen uusille
etuosille: kielen tekijä tuottaa LLVM IR:ää, ja kaikki optimoinnit ja
takaosat ovat valmiina.

Molempien kääntäjien vaiheita voi tutkia samaan tapaan kuin Kiden
`--vaihe`-valinnalla:

| Komento | Näyttää |
|---------|---------|
| `gcc -fdump-tree-all` | GIMPLE jokaisen passin jälkeen |
| `gcc -fdump-rtl-all` | RTL jokaisen passin jälkeen |
| `clang -Xclang -ast-dump` | Clangin syntaksipuu |
| `clang -S -emit-llvm` | LLVM IR |
| `opt -passes='...' -print-after-all` | LLVM:n passit yksitellen |
| `llc -print-after-all` | takaosan vaiheet |

Compiler Explorer (godbolt.org) näyttää saman verkkoselaimessa monella
kääntäjällä rinnakkain.

## Sama funktio GCC:llä

Kertomafunktio C:llä:

```{.c tiedosto="esimerkit/vertailu/kertoma.c"}
```

Ilman optimointeja (`riscv64-linux-gnu-gcc -O0 -S`):

```{.gnuassembler tiedosto="esimerkit/vertailu/kertoma-O0.s"}
```

GCC:n `-O0` muistuttaa Kiden kaikki pinoon -varausta: parametri
tallennetaan pinoon heti alussa ja ladataan sieltä jokaista käyttöä
varten. Syy on debuggaus: kun jokainen muuttuja on muistissa, debuggeri
voi näyttää ja muuttaa sitä milloin tahansa. Vertailu ja haara on silti
yhdistetty yhdeksi käskyksi (`bgt`), koska käskyjen valinta tuntee
RISC-V:n haarakäskyt, ja vakio vähennetään `addi`-käskyllä.

Optimoituna (`-O2`):

```{.gnuassembler tiedosto="esimerkit/vertailu/kertoma-O2.s"}
```

Rekursio on kadonnut. GCC on muuttanut funktion silmukaksi, joka
kertoo tuloksen akkumulaattoriin `a0`. Muunnos vaatii kaksi askelta.
Ensin `n * kertoma(n - 1)` ei ole häntäkutsu, koska kertolasku tehdään
kutsun jälkeen. Kertolasku on kuitenkin liitännäinen, joten kääntäjä voi
kuljettaa osittaisen tulon mukana (*akkumulaattorimuunnos*), ja sen
jälkeen kutsu on häntäkutsu, jonka voi korvata hypyllä. Kaikki muuttujat
ovat rekistereissä, pinokehystä ei ole, eikä `ra`:ta tarvitse tallentaa,
koska funktio ei enää kutsu mitään.

Kiden `-O1` on näiden välissä: rekisterit ovat käytössä, mutta
rekursio, pinokehys ja kolmen käskyn vertailu ovat jäljellä (luku 1).
Kiden `-O2` ei muuta tilannetta, koska sen SSA-passit eivät koske
kutsuihin eivätkä käskyjen valintaan (luku 14).

## Mitä tuotantokääntäjä tekee lisää

Ero Kiden ja GCC:n välillä syntyy muutamasta tekniikasta, joista
jokainen on tässä tutoriaalissa esitellyn jatke:

- **Käskyjen valinta malleilla** yhdistää vertailun ja haaran sekä
  käyttää välittömiä vakioita (luku 15).
- **Rekisterien varaus kustannuksilla** pitää silmukan arvot
  rekistereissä ja käyttää kutsun tuhoamia rekistereitä
  lehtifunktioissa (luku 16).
- **Silmukkaoptimoinnit SSA-muodossa** (silmukasta riippumattoman
  koodin siirto, induktiomuuttujat, osittaisen redundanssin poisto)
  jatkavat siitä, mihin Kiden kolme SSA-passia jäävät (luvut 11 ja
  13).
- **Upottaminen ja funktioiden väliset analyysit** tuovat kutsutun
  koodin kutsujan optimoinnin piiriin, ja linkitysaikainen optimointi
  (LTO) tekee saman käännösyksiköiden yli.
- **Kohdekoneen malli** ajoittaa käskyt liukuhihnan viiveiden mukaan
  (taito *Tietokonearkkitehtuuri*) ja valitsee vektorikäskyt.

Lisäksi tuotantokääntäjällä on velvollisuuksia, joita Kidellä ei ole:
debuggaustieto (DWARF, taito *Objektitiedostot, linkitys ja ABI*),
varoitukset, kielistandardin tarkka noudattaminen ja yhteensopivuus
vuosikymmenten koodin kanssa. Ne muodostavat suurimman osan GCC:n ja
LLVM:n miljoonista koodiriveistä.

## Käytännössä

- **Lue kääntäjän tuottamaa koodia.** Kun suorituskyky ratkaisee,
  `-S`-tuloste tai Compiler Explorer kertoo, tekikö kääntäjä sen, mitä
  oletit.
- **Käytä välikielen tulosteita vianetsintään.** Jos optimoitu ohjelma
  toimii väärin, `-fdump-tree-all` tai `-print-after-all` näyttää,
  minkä passin jälkeen koodi muuttui; usein syy on silti ohjelman
  määrittelemätön käytös eikä kääntäjä.
- **Rakenna oma kieli LLVM:n päälle.** Uuden kielen kannattaa tuottaa
  LLVM IR:ää (tai C:tä) eikä assemblyä, ellei tavoitteena ole oppia
  takaosan tekniikkaa.

## Itsearviointi

- Osaat sijoittaa Kiden vaiheet GCC:n ja LLVM:n arkkitehtuuriin ja
  nimetä niiden välikielet.
- Osaat tulostaa GCC:n ja Clangin välivaiheita ja käyttää niitä
  vianetsintään.
- Osaat selittää, miksi `-O0`-koodi pitää muuttujat pinossa ja miten
  `-O2` muuttaa kertoman rekursion silmukaksi.
- Osaat luetella tekniikat, jotka erottavat Kiden koodin GCC:n
  optimoidusta koodista.
