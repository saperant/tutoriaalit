# Kääntäjän tuottamat rakenteet

Kääntäjä muuntaa lähdekoodin rakenteet konekieleksi muutamalla
toistuvalla kuviolla. Kun kuviot tunnistaa, lohkojen ja hyppyjen
verkosta näkee taas `if`-lauseet, silmukat, `switch`-rakenteet ja
tietueet. Tämän luvun kohde on käännetty `-O1`:llä ja valitsimella
`-fno-inline`, jotta jokainen funktio näkyy erikseen:

```{.c tiedosto="esimerkit/03-rakenteet/ohjaus.c" osa="luokka"}
```

## Ehtolauseet

```{.tuloste tiedosto="esimerkit/03-rakenteet/odotettu" osa="t1"}
```

Ehtoketju kääntyy vertailuiksi ja ehdollisiksi hypyiksi. Kääntäjä
kääntää vertailut usein: `pisteet >= 90` on `cmp edi,0x59; jg`, eli
`pisteet > 89`. Paluuarvo asetetaan ennen vertailua (`mov eax,0x5`),
ja hyppy vie suoraan `ret`-käskyyn. Viimeinen haara on ilman hyppyjä:
`setg al` tekee vertailusta arvon 0 tai 1, ja `lea eax,[rax+rax*2]`
kertoo sen kolmella. Lauseke on siis `(pisteet > 49) * 3`: kääntäjä on
huomannut, että `return 3` ja `return 0` voi laskea ehdosta.

Tavallinen kuvio on

```text
    cmp  a, b
    jXX  muu        ; hyppy, jos ehto EI päde
    ...             ; then-haara
    jmp  loppu
muu:
    ...             ; else-haara
loppu:
```

Ehdollisen hypyn ehto on usein lähdekoodin ehdon vastakohta, koska
hyppy ohittaa then-haaran.

## Silmukat

```{.c tiedosto="esimerkit/03-rakenteet/ohjaus.c" osa="pituus"}
```

```{.tuloste tiedosto="esimerkit/03-rakenteet/odotettu" osa="t5"}
```

Silmukan tunnistaa taaksepäin hyppäävästä haarasta (`jne
<pituus+0x1c>` hyppää aiempaan osoitteeseen). Optimoitu `while`-silmukka
on muunnettu muotoon `if (ehto) do { … } while (ehto)`: ensimmäinen
tarkistus on erikseen silmukan edessä (`cmp BYTE PTR [rdi],0x0; je`),
ja varsinainen ehto on silmukan lopussa. Tätä kutsutaan *silmukan
kiertämiseksi* (*loop rotation*); `for`- ja `while`-silmukat näyttävät
konekielessä samalta.

## Switch ja hyppytaulut

```{.c tiedosto="esimerkit/03-rakenteet/ohjaus.c" osa="hinnoittele"}
```

```{.tuloste tiedosto="esimerkit/03-rakenteet/odotettu" osa="t2"}
```

Tiheä `switch` kääntyy *hyppytauluksi*:

1. `cmp edi,0x5; ja` tarkistaa rajat: arvot yli viiden (myös
   negatiiviset, koska `ja` on etumerkitön vertailu) menevät
   oletushaaraan.
2. `lea rcx,[rip+X]` hakee taulun osoitteen `.rodata`-osiosta, ja
   `movsxd rdx,DWORD PTR [rcx+rdi*4]` lukee indeksin mukaisen
   32-bittisen siirtymän.
3. `add rdx,rcx` lisää siirtymän taulun osoitteeseen, ja `notrack jmp
   rdx` hyppää. `notrack` kertoo, että kohteissa ei ole
   `endbr64`-merkintää.

Taulun alkiot ovat suhteellisia siirtymiä, jotta koodi on
paikkariippumaton. Harvassa `switch`-rakenteessa (esim. arvot 1, 100 ja
10000) kääntäjä tekee sen sijaan vertailuketjun tai binäärihakupuun.
Rekursiivinen disassembleri ei löydä hyppytaulun kohteita ilman taulun
tulkintaa; radare2 ja Ghidra tunnistavat tämän kuvion ja nimeävät
haarat (`case 0:` jne.).

Haaroissa on myös jakolaskuja vakioilla: `imul rdx,rdx,0x66666667;
sar rdx,0x23` on jakolasku kahdellakymmenellä. Luku 5 selittää kuvion.

## Rakenteet ja taulukot

Rakenteen kentät näkyvät vakiosiirtyminä samasta osoittimesta, ja
taulukon alkion koko näkyy osoittimen askeleena:

```{.c tiedosto="esimerkit/03-rakenteet/ohjaus.c" osa="tuote"}
```

```{.tuloste tiedosto="esimerkit/03-rakenteet/odotettu" osa="t3"}
```

`shl rsi,0x4` ja `add rax,0x10` kertovat, että alkion koko on 16
tavua. `cvtsi2sd xmm0,DWORD PTR [rax+0x4]` lukee siirtymästä 4
32-bittisen kokonaisluvun ja muuntaa sen liukuluvuksi, ja `mulsd
xmm0,QWORD PTR [rax+0x8]` kertoo sen siirtymän 8 `double`-arvolla.
Siirtymän 0 kenttää ei lueta, mutta koko 16 kertoo, että siinä on
neljä tavua jotakin. Päätelty rakenne on

```text
struct ? {          // 16 tavua
    ?      kentta0; // +0, 4 tavua, ei käytetä tässä funktiossa
    int    kentta4; // +4
    double kentta8; // +8
};
```

Kaksiulotteinen taulukko on yksi muistialue, jonka rivi lasketaan
kertolaskulla:

```{.c tiedosto="esimerkit/03-rakenteet/ohjaus.c" osa="ruudukko"}
```

```{.tuloste tiedosto="esimerkit/03-rakenteet/odotettu" osa="t4"}
```

`lea rax,[rsi+rsi*4]` ja `lea rdx,[rdi+rax*4]` laskevat osoitteen
`ruudukko + rivi * 5 * 4`: rivin pituus on viisi neljän tavun alkiota.
Silmukka on avattu kokonaan viideksi yhteenlaskuksi.

## Analyysin automatisointi

Kuvioiden etsimisen voi automatisoida. Skripti `tunnista.py` lukee
`objdump`-purun moduulilla `tyokalut/purku.py` ja tulostaa kustakin
funktiosta havainnot:

```{.python tiedosto="esimerkit/03-rakenteet/tunnista.py" osa="silmukat"}
```

Hyppytaulun skripti lukee ohjelmatiedostosta: rajavertailu antaa
alkioiden määrän ja `lea`-käskyn `rip`-suhteellinen siirtymä taulun
osoitteen.

```{.bash tiedosto="esimerkit/03-rakenteet/aja.sh" osa="tunnista"}
```

```{.tuloste tiedosto="esimerkit/03-rakenteet/odotettu" osa="t6"}
```

Tulos ei korvaa lukemista, mutta se suuntaa sitä: isossa ohjelmassa
tällainen kysely löytää esimerkiksi kaikki hyppytaulut tai kaikki
funktiot, jotka käsittelevät 16 tavun tietueiden taulukkoa. Samaa
tekevät Ghidran ja radare2:n skriptirajapinnat laajemmin.

## Käytännössä

- **Etsi ensin silmukat.** Taaksepäin hyppäävä haara ja sen ehto
  rajaavat funktion ytimen; silmukan ulkopuolinen koodi on usein
  alustusta ja virheenkäsittelyä.
- **Käännä ehdot mielessä.** Hyppy ohittaa koodin, joten lähdekoodin
  ehto on yleensä hypyn ehdon vastakohta.
- **Kerää rakenteen siirtymät taulukoksi** ja kokoa niistä tietuemäärittely.
  Kun sama siirtymä esiintyy useassa funktiossa samalla tyypillä, kenttä
  on varmistunut.
- **Tunnista hyppytaulut** rajavertailusta ja epäsuorasta hypystä; jos
  työkalu ei tunnista niitä, haarat jäävät analysoimatta.
- **Kirjoita havainnot skripteiksi**, kun samaa kysymystä kysytään
  monesta funktiosta.

## Itsearviointi

- Osaat tunnistaa ehtolauseet, silmukat ja kierretyt silmukat
  konekielestä.
- Osaat purkaa hyppytaulun: rajat, taulun osoite, siirtymät ja kohteet.
- Osaat päätellä rakenteen kentät ja koon muistiviittausten
  siirtymistä ja osoittimen askeleesta.
- Osaat kirjoittaa skriptin, joka etsii purusta kääntäjän kuvioita.
