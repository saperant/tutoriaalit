# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

**Kokonaisluvut**

- Valitse tyyppi arvoalueen mukaan: `size_t` koille, `int64_t`
  määrille ja rahalle sentteinä, tarkan leveyden tyypit ulkoisille
  muodoille.
- Etumerkillinen ylivuoto on C:ssä määrittelemätöntä. Tarkista ulkoa
  tulevat laskut `ckd_add`- ja `ckd_mul`-makroilla ennen kuin tulosta
  käytetään.
- Etumerkittömät tyypit bittioperaatioille ja tarkoitukselliselle
  kiertymiselle, etumerkilliset määrille. Älä sekoita niitä
  vertailuissa.
- Siirtomäärä on aina pienempi kuin tyypin leveys.
- Tiedä kielen jakolaskusääntö: C katkaisee kohti nollaa, Python
  pyöristää alaspäin.
- NumPy-taulukot kiertävät hiljaa. Anna kertymälle leveämpi tyyppi.

**Liukuluvut**

- `double` oletuksena. `float` ja pienemmät muodot valitaan
  perustellusti.
- Ei liukulukuja rahalle eikä aikaleimoille.
- Ei `==`-vertailua lasketuille arvoille. Käytä suhteellista ja
  absoluuttista toleranssia.
- Pitkät summat kompensoiden tai parittain, varianssi Welfordilla,
  kumoutuminen pois kaavaa muokkaamalla.
- NaN leviää ja rikkoo vertailut. Tarkista syötteet rajalla.
- Ei `-ffast-math`-valitsinta ilman testejä ja perustelua.
- Kirjoita liukuluvut tiedostoihin 17 numerolla tai heksadesimaalina.

**Koneoppimisen muodot**

- Kertymä on aina leveämpi kuin syötteet: int8 → int32, FP8 ja
  bfloat16 → float32.
- Pyöristä lähimpään parilliseen, älä katkaise.
- Kalibroi kvantisoinnin skaala edustavalla datalla ja mittaa tulos
  tehtävän tarkkuutena.

**Stokastinen pyöristys**

- Kun samaan lukuun kertyy paljon portaan kokoa pienempiä muutoksia,
  lähimpään pyöristys pysähtyy. Stokastinen pyöristys on harhaton,
  mutta lisää kohinaa.
- Kiinnitä siemen ja tallenna se tulosten mukana.

**Muisti**

- Sisin silmukka kulkee peräkkäisiä osoitteita.
- Tiedä, onko NumPy-operaation tulos näkymä vai kopio.
- Käytä BLAS-kirjastoa matriisilaskentaan. Mittaa optimoidulla
  käännöksellä.

## Mallit ja niiden nimet

| Malli | Ongelma, jonka se ratkaisee | Luku |
|-------|-----------------------------|------|
| Tarkistettu aritmetiikka | ylivuoto ulkoisesta syötteestä | 3 |
| Sarjanumeroaritmetiikka (RFC 1982) | kiertyvien laskurien vertailu | 3 |
| Etumerkin laajennus | kapea kahden komplementin kenttä | 2 |
| Lattiajako ja -jäännös | jaksolliset arvot negatiivisilla luvuilla | 5 |
| Kahanin summa, parittainen summa | summauksen virheen kasvu | 7 |
| Welfordin algoritmi | varianssin kumoutuminen | 7 |
| Error-free transformation (TwoSum, FMA) | tulon ja summan virheen talteenotto | 7 |
| Symmetrinen ja asymmetrinen kvantisointi | liukulukujen esitys int8:na | 8 |
| Stokastinen pyöristys | pysähtyvä kertymä matalalla tarkkuudella | 9 |
| Lohkominen (tiling) | datan uudelleenkäyttö välimuistissa | 11 |

## Jatkotaidot

Taitopuussa tästä jatketaan taitoihin *Lukujen esitys ja kiinteän pilkun aritmetiikka*,
jossa samoja kysymyksiä ratkaistaan laitteistossa ja signaalinkäsittelyssä,
ja *Suorituskyvyn analyysi ja optimointi*, jossa mitataan ja optimoidaan välimuistin ja
SIMD-käskyjen käyttöä. GPU:iden laskenta ja koneoppimisen muodot
jatkuvat taidossa *GPU-laskenta*. Virheanalyysi, ehtoluku ja
algoritmien stabiilisuus ovat taidon *Numeeriset menetelmät* aiheita.

## Lähteet ja jatkolukeminen

### Standardit

- **IEEE 754-2019**, *Standard for Floating-Point Arithmetic*.
  Maksullinen, mutta Wikipedian artikkelit kattavat sen pääkohdat.
- **ISO/IEC 9899:2024 (C23)**. Viimeinen julkinen luonnos N3220
  (<https://open-std.org/jtc1/sc22/wg14/>) sisältää `<stdckdint.h>`-
  ja `<stdbit.h>`-otsakkeet.
- **OCP 8-bit Floating Point Specification (OFP8)**, Open Compute
  Project 2023 (<https://www.opencompute.org>), määrittelee E4M3- ja
  E5M2-muodot.
- **RFC 1982**, *Serial Number Arithmetic*
  (<https://www.rfc-editor.org/rfc/rfc1982>).

### Kirjat ja artikkelit

- David Goldberg: *What Every Computer Scientist Should Know About
  Floating-Point Arithmetic*, ACM Computing Surveys 1991. Liukulukujen
  perusartikkeli, saatavilla verkosta.
- Nicholas J. Higham: *Accuracy and Stability of Numerical Algorithms*,
  2. painos, SIAM 2002. Summauksen, pistetulon ja muiden algoritmien
  virheanalyysi.
- Randal E. Bryant ja David R. O'Hallaron: *Computer Systems: A
  Programmer's Perspective*, 3. painos, Pearson 2016. Luku 2 käsittelee
  kokonaislukujen ja liukulukujen esityksen ohjelmoijan kannalta.
- Henry S. Warren: *Hacker's Delight*, 2. painos, Addison-Wesley 2012.
  Bittitason algoritmit ja vakiolla jako kertolaskuna.
- Jean-Michel Muller ym.: *Handbook of Floating-Point Arithmetic*,
  2. painos, Birkhäuser 2018.
- Ulrich Drepper: *What Every Programmer Should Know About Memory*, 2007
  (<https://people.freebsd.org/~lstewart/articles/cpumemory.pdf>).
  Välimuistit ja muistin rakenne ohjelmoijan näkökulmasta.
- Kazushige Goto ja Robert van de Geijn: *Anatomy of High-Performance
  Matrix Multiplication*, ACM TOMS 2008. Miten BLAS-ytimet rakennetaan.
- Benoit Jacob ym.: *Quantization and Training of Neural Networks for
  Efficient Integer-Arithmetic-Only Inference*, CVPR 2018. int8-
  kvantisoinnin perusartikkeli.
- Suyog Gupta ym.: *Deep Learning with Limited Numerical Precision*,
  ICML 2015. Neuroverkon koulutus 16 bitin kiinteällä pilkulla onnistuu
  stokastisella pyöristyksellä mutta ei lähimpään pyöristämällä.
- Matteo Croci ym.: *Stochastic rounding: implementation, error
  analysis and applications*, Royal Society Open Science 2022.
  Katsausartikkeli stokastisesta pyöristyksestä.
- Michael P. Connolly, Nicholas J. Higham ja Theo Mary: *Stochastic
  Rounding and Its Probabilistic Backward Error Analysis*, SIAM Journal
  on Scientific Computing 2021. Virherajat, jotka kasvavat kuten
  $\sqrt{n}$.

### Dokumentaatio ja työkalut

- Python: `decimal`-, `fractions`- ja `math`-moduulien dokumentaatio
  (<https://docs.python.org/3/library/>), erityisesti `math.fsum` ja
  `math.isclose`.
- NumPy: *Internal organization of NumPy arrays* ja *Copies and views*
  (<https://numpy.org/doc/stable/>).
- GCC:n ja Clangin käsikirjat: liukulukuvalitsimet (`-ffp-contract`,
  `-ffast-math`) ja sanitoijat.
- Compiler Explorer (<https://godbolt.org>) näyttää kääntäjän tuottaman
  koodin.
- Float Toy (<https://evanw.github.io/float-toy/>) ja IEEE-754 Analysis
  (<https://weitz.de/ieee/>) näyttävät liukuluvun bitit selaimessa.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
