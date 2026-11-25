# Ominaisuuksien tunnistus ajon aikana

Linux-jakelut kääntävät ohjelmansa prosessorien yhteiselle
perustasolle, jotta sama paketti toimii kymmenen vuotta vanhassa
kannettavassa ja uudessa palvelimessa. Uudemmat käskyt, kuten AVX2
tai RISC-V:n vektorilaajennus, ovat silloin käytettävissä vain, jos
ohjelma tarkistaa ajon aikana, onko prosessorissa niitä, ja valitsee
toteutuksen sen mukaan. Näin toimivat glibc:n `memcpy` ja `strlen`,
OpenSSL, zlib-ng ja lähes jokainen mediakirjasto.

Tehtävässä on kolme osaa: ominaisuuden tunnistus, toteutuksen
kääntäminen laajennukselle ilman, että muu ohjelma vaatii sitä, ja
valinta toteutusten välillä.

## Tunnistus x86-64:llä

x86-64:n käsky `cpuid` palauttaa ominaisuusbitit rekistereissä `eax`,
`ebx`, `ecx` ja `edx`. Kysymys valitaan `eax`:n arvolla (*lehti*) ja
joskus `ecx`:n arvolla (*alalehti*). Käskyn operandit ovat kiinteissä
rekistereissä, joten se on tyypillinen inline-assemblyn käyttökohde:

```{.c tiedosto="esimerkit/06-ominaisuudet/tunnistus.c" osa="cpuid"}
```

Pelkkä AVX2-bitti ei riitä. AVX-käskyjen 256-bittiset `ymm`-rekisterit
ovat käytettävissä vain, jos käyttöjärjestelmä tallentaa ne
säikeenvaihdossa. Sen kertoo ohjausrekisteri XCR0, jonka käsky
`xgetbv` lukee, ja `xgetbv` on käytettävissä vain, jos OSXSAVE-bitti
on päällä. Tunnistus, joka unohtaa XCR0:n, toimii useimmilla koneilla,
mutta kaatuu virtuaalikoneissa ja ytimissä, joissa AVX on kytketty
pois.

Käsin kirjoitettua tunnistusta tarvitaan harvoin, koska GCC tarjoaa
sen valmiina: `__builtin_cpu_supports("avx2")` tekee saman
tarkistuksen, mukaan lukien XCR0:n. Otsake `<cpuid.h>` tarjoaa lisäksi
funktiot `__get_cpuid` ja `__get_cpuid_count`, jotka tarkistavat
myös, onko pyydetty lehti olemassa. Esimerkin oma toteutus on mukana,
jotta näkee, mitä valmiit funktiot tekevät, ja ohjelma vertaa niitä
toisiinsa.

## Toteutus laajennukselle

Funktion attribuutti `target("avx2")` sallii AVX2-käskyt vain siinä
funktiossa. Muu ohjelma käännetään edelleen perustasolle, ja
AVX2:n sisäisiä funktioita saa kutsua vain tällaisesta funktiosta:

```{.c tiedosto="esimerkit/06-ominaisuudet/laske.c" osa="avx2"}
```

Funktiota ei saa kutsua ennen tunnistusta. Jos sitä kutsutaan
prosessorilla, jolla AVX2:ta ei ole, ohjelma kaatuu laittomaan
käskyyn (`SIGILL`). Vaara ei rajoitu itse kirjoitettuihin sisäisiin
funktioihin: kääntäjä saa käyttää AVX2-käskyjä missä tahansa kohdassa
`target`-funktiota, myös tavallisessa C-koodissa, jonka se
vektoroi.

## Valinta: ifunc

Yksinkertaisin valintatapa on funktio-osoitin, joka asetetaan
ohjelman alussa. Se toimii kaikilla alustoilla, mutta jokainen kutsu
kulkee osoittimen kautta, ja asetus pitää muistaa tehdä ennen ensimmäistä
kutsua. Linuxin ELF-alustoilla on parempi keino, *ifunc*
(*indirect function*): symboli, jonka osoitteen ratkaisee
valitsijafunktio, kun ohjelma ladataan:

```{.c tiedosto="esimerkit/06-ominaisuudet/laske.c" osa="ifunc"}
```

```{.dot otsikko="ifunc-symbolin elinkaari. Valinta tehdään kerran latauksessa; sen jälkeen jokainen kutsu menee linkitystaulun kautta suoraan valittuun toteutukseen."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.5;
  subgraph cluster_lataus {
    label="ohjelman lataus (kerran)"; color="#C9CED6"; style=rounded;
    lataaja [label="dynaaminen linkkeri\n(tai käynnistyskoodi)"];
    valitsija [label="valitse_laske()\ncpuid, XCR0", fillcolor="#F3E2C7"];
    taulu [label="linkitystaulun\npaikka: laske", fillcolor="#FFFFFF"];
    lataaja -> valitsija [label="kutsuu"];
    valitsija -> taulu [label="osoite"];
  }
  subgraph cluster_ajo {
    label="ajon aikana (joka kutsu)"; color="#C9CED6"; style=rounded;
    kutsu [label="laske(t, n, c)"];
    avx2 [label="laske_avx2"];
    perus [label="laske_perus", fillcolor="#FFFFFF", style="rounded,dashed"];
  }
  kutsu -> taulu [label="epäsuora hyppy"];
  taulu -> avx2;
  taulu -> perus [style=dashed];
}
```

Dynaaminen linkkeri kutsuu valitsijaa kerran ja kirjoittaa sen
palauttaman osoitteen linkitystauluun. Sen jälkeen `laske`-kutsu
maksaa saman kuin mikä tahansa kirjastokutsu, eikä valinnasta jää
ajonaikaista haaraa. Staattisesti linkitetyssä ohjelmassa saman tekee
C-kirjaston käynnistyskoodi. Valitsijaa kutsutaan hyvin varhain,
ennen konstruktoreita ja joskus ennen kuin muiden kirjastojen
relokaatiot on käsitelty, joten se ei saa kutsua muita kirjastoja eikä
käyttää globaaleja muuttujia, joiden alustus on kesken.
`__builtin_cpu_init` on siksi kutsuttava itse.

GCC osaa tuottaa saman rakenteen automaattisesti. Attribuutti
`target_clones("avx2", "default")` kääntää funktiosta kaksi versiota
ja ifunc-valitsijan. Sitä kannattaa käyttää, kun versiot eroavat vain
kääntäjän vektoroinnissa, ja käsin kirjoitettua valitsijaa, kun
toteutukset ovat erilaiset.

## Molemmat polut testiin

Valinta tekee testaamisesta hankalaa: kehittäjän kone valitsee aina
saman toteutuksen, ja toinen polku jää testaamatta. Siksi esimerkin
ohjelma ei kerro, kumpi toteutus valittiin, vaan vain sen, että
tunnistustavat ovat samaa mieltä ja tulos on oikein:

```{.tuloste tiedosto="esimerkit/06-ominaisuudet/odotettu"}
```

Molemmat polut testataan ajamalla sama ohjelma QEMU:n x86-64-emulaattorissa
kahdella prosessorimallilla:

```{.bash tiedosto="esimerkit/06-ominaisuudet/tarkistus.sh" osa="mallit"}
```

```{.tuloste tiedosto="esimerkit/06-ominaisuudet/tarkistus.odotettu"}
```

Nehalem (2008) ei tue AVX:ää, Haswell (2013) tukee AVX2:ta. Mallin
nimen pääte `noTSX` jättää pois transaktiomuistin, jota QEMU ei emuloi.
Toinen tapa on pakottaa valinta ympäristömuuttujalla testejä varten.
Glibc tekee näin omille funktioilleen: `GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX2`
kieltää AVX2-toteutukset.

## Tunnistus RISC-V:llä

RISC-V:llä ei ole `cpuid`-käskyn vastinetta käyttäjätilassa. Laajennukset
kertova CSR-rekisteri `misa` on luettavissa vain konetilassa, eikä se
kuvaa monikirjaimisia laajennuksia (Zbb, Zvbb ja muut) lainkaan.
Tunnistus tehdään käyttöjärjestelmän kautta:

- **`getauxval(AT_HWCAP)`** palauttaa bittikartan yksikirjaimisista
  laajennuksista; bitti `'V' - 'A'` kertoo vektorilaajennuksesta.
- **Järjestelmäkutsu `riscv_hwprobe`** (Linux 6.4 ja uudemmat) kertoo
  myös monikirjaimiset laajennukset ja suorituskykytietoja, kuten
  tasaamattomien muistiosoitusten nopeuden. Uudemmat glibc-versiot
  tarjoavat sille kääreen `__riscv_hwprobe` ja välittävät
  ifunc-valitsijalle sen osoittimen.

Laajennukselle kääntäminen tehdään RISC-V:llä erillisellä
käännösyksiköllä, joka käännetään valitsimella `-march=rv64gcv`, tai
GCC 14:stä alkaen attribuutilla `target("arch=+v")`. Tämän tutoriaalin
RISC-V-ristikääntäjä (GCC 13) varoittaa attribuutista ja jättää sen
huomiotta, joten erillinen käännösyksikkö on varmempi.

## Käytännössä

- **Valmis tunnistus ennen omaa.** `__builtin_cpu_supports`,
  `getauxval` ja `__riscv_hwprobe` tietävät käyttöjärjestelmän
  osuuden (XCR0, ytimen tuki). Oma `cpuid`-koodi on perusteltu vain,
  jos tarvitaan tietoa, jota kääntäjä ei tarjoa.
- **Tunnista kerran, valitse kerran.** ifunc tai käynnistyksessä
  asetettu funktio-osoitin; ei tunnistusta jokaisessa kutsussa.
- **Laajennuskoodi omaan käännösyksikköönsä** tai
  `target`-attribuutin taakse. Valitsin `-mavx2` koko ohjelmalle
  tekee siitä AVX2-ohjelman, vaikka tunnistus olisi kunnossa, koska
  kääntäjä saa käyttää AVX2:ta missä tahansa.
- **Testaa jokainen polku.** QEMU-prosessorimallit, Intelin SDE tai
  ympäristömuuttuja, joka pakottaa valinnan. Testaamaton varapolku
  on yleinen virhe, joka löytyy vasta asiakkaan vanhalta koneelta.
- **Perustaso varapoluksi.** Skalaari- tai SSE2-versio pysyy aina
  mukana, eikä sen oikeellisuus saa riippua siitä, millä koneella
  testit ajetaan.

## Itsearviointi

- Osaat tunnistaa AVX2:n `cpuid`- ja `xgetbv`-käskyillä ja selittää,
  miksi XCR0 pitää tarkistaa.
- Osaat kääntää yksittäisen funktion laajennukselle
  `target`-attribuutilla ja kertoa, miksi sitä ei saa kutsua ennen
  tunnistusta.
- Osaat valita toteutuksen ifunc-valitsijalla ja kertoa, mitä
  valitsija saa ja ei saa tehdä.
- Osaat testata kaikki valintapolut emuloiduilla prosessorimalleilla.
- Osaat kertoa, miten laajennukset tunnistetaan RISC-V Linuxissa.
