# Työn jako ja synkronointi

GPU-laskennassa on kolme tahdistuksen tasoa, ja jokaisella on oma
välineensä. Edellisten lukujen algoritmit käyttivät niitä kaikkia:

| Taso | Väline | Esimerkki |
|------|--------|-----------|
| aliryhmän sisällä | ei tarvita, kaistat etenevät yhdessä | `subgroupAdd` |
| työryhmän sisällä | `barrier()` ja jaettu muisti | reduktion puu, lohkoskannaus |
| työryhmien välillä | uusi ajo ja putken este | monivaiheinen reduktio, lajittelu |
| GPU:n ja CPU:n välillä | aita (fence) tai aikajanasemafori | tulosten luku |

```{.dot otsikko="Tahdistuksen tasot sisäkkäin. Mitä sisempänä riippuvuus on, sitä halvempi tahdistus on."}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.5; compound=true;
  node [shape=box, style="rounded,filled", fillcolor="#C9CEEE"];
  cpu [label="CPU:\nisäntäohjelma", fillcolor="#EEF0F2"];
  subgraph cluster_ajo1 {
    label="ajo 1 (vkCmdDispatch)"; style="rounded"; color="#5B6B70";
    subgraph cluster_ryhma {
      label="työryhmä: barrier(), jaettu muisti"; style="rounded,filled";
      fillcolor="#F4E6DA"; color="#C0652A";
      a0 [label="aliryhmä 0"]; a1 [label="aliryhmä 1"];
    }
    r1 [label="työryhmä 1", fillcolor="#F4E6DA"];
  }
  subgraph cluster_ajo2 {
    label="ajo 2"; style="rounded"; color="#5B6B70";
    r2 [label="työryhmät", fillcolor="#F4E6DA"];
  }
  a1 -> r2 [label="putken este", ltail=cluster_ajo1, lhead=cluster_ajo2];
  r2 -> cpu [label="aita tai\nsemafori", ltail=cluster_ajo2];
  a0 -> a1 [style=invis];
}
```

Algoritmin suunnittelu GPU:lle on pitkälti sitä, että työ jaetaan
näille tasoille: mahdollisimman paljon aliryhmään ja työryhmään,
joissa tahdistus on halpaa, ja mahdollisimman vähän ajojen välisiä
riippuvuuksia.

## Työryhmän sisäinen tahdistus

`barrier()` on **suoritusriippuvuus**: yksikään työryhmän säie ei
jatka ennen kuin kaikki ovat saavuttaneet sen. Lisäksi se on
laskentavarjostimessa **muistieste jaetulle muistille**: ennen estettä
jaettuun muistiin tehdyt kirjoitukset näkyvät kaikille esteen jälkeen.
Varjostimissa näkee usein parin
`memoryBarrierShared(); barrier();`, joka sanoo saman
eksplisiittisesti. Vulkanin GLSL:ssä pelkkä
`barrier()` riittää jaetulle muistille, mutta ei globaalille.

Muistiesteet ilman suoritusriippuvuutta (`memoryBarrier()`,
`memoryBarrierBuffer()`, `memoryBarrierShared()`) järjestävät vain
saman säikeen muistioperaatiot: myöhemmät eivät näy muille ennen
aiempia. Ne eivät pakota muita säikeitä odottamaan. Niitä tarvitaan
esimerkiksi silloin, kun säie kirjoittaa datan globaaliin muistiin ja
asettaa sitten atomisesti valmis-lipun (luku 6). Vulkanin muistimalli
(laajennus `GL_KHR_memory_scope_semantics`) antaa tarkemmat työkalut:
atomiset operaatiot vapauttavalla (release) ja hankkivalla (acquire)
semantiikalla sekä näkyvyysalueen valinnan (aliryhmä, työryhmä, laite).
Ne vastaavat C++:n muistimallia, jota taito *Rinnakkaisohjelmointi*
käsittelee.

Kolme sääntöä estää yleisimmät virheet:

1. **Este tasaisessa ohjausvuossa.** Jokaisen työryhmän säikeen on
   suoritettava sama määrä samoja esteitä. Este haarassa, johon vain
   osa säikeistä menee, tai silmukassa, jonka kierrosmäärä vaihtelee
   säikeittäin, on määrittelemätöntä käytöstä. Siksi luvun 8
   matriisitulo lataa reunoilla nollia eikä palaa aikaisin.
2. **Este sekä ennen lukua että ennen uudelleenkirjoitusta.**
   Ensimmäinen este varmistaa, että data on kirjoitettu, ennen kuin
   sitä luetaan (RAW). Toinen varmistaa, että kaikki ovat lukeneet,
   ennen kuin sama jaettu muisti korvataan (WAR). Jälkimmäinen unohtuu
   helposti silmukassa.
3. **Ei estettä globaalin muistin yli.** `barrier()` ei tahdista eri
   työryhmiä. Globaalin muistin kautta tahdistuvat työryhmät
   tarvitsevat uuden ajon.

Puuttuva este jaetussa muistissa on vaikea virhe. Lavapipellä se näkyy
usein satunnaisesti, ja oikealla GPU:lla se voi näkyä vain tietyllä
aliryhmän leveydellä tai kuormalla. Työkalut auttavat vain osittain:
validointikerroksen GPU-avusteinen tarkistus löytää rajojen yli menevät
haut, mutta ei puuttuvia työryhmän esteitä. Paras suoja on testi, joka
vertaa tulosta referenssiin usealla koolla ja aliryhmän leveydellä.

## Työryhmien välinen tahdistus

Työryhmät voivat valmistua missä järjestyksessä tahansa, eikä laite
takaa, että kaikki ajon työryhmät ovat yhtä aikaa käynnissä. Jos ajo
käynnistää 10 000 työryhmää ja laitteeseen mahtuu 500, ensimmäiset
500 ajetaan loppuun ennen kuin loput alkavat. Jos ensimmäinen
työryhmä jäisi odottamaan viimeistä, ohjelma jumittuisi. Siksi
globaalia estettä ei ole, ja riippuvuus ilmaistaan ajojen rajalla:

```{.cpp tiedosto="esimerkit/yhteinen/laskenta.hpp" osa="este"}
```

Este kuuluu ajojen väliin komentopuskurissa. Se sanoo, että edellisten
laskentavaiheiden varastokirjoitusten on oltava valmiita ja
näkyviä ennen kuin seuraavat laskentavaiheet lukevat tai kirjoittavat.
Taito *GPU-ohjelmointi: OpenGL ja Vulkan* kävi esteiden osat läpi grafiikan kannalta.
Laskennassa vaiheita on vain yksi, `COMPUTE_SHADER`, mutta sama
erottelu suoritus- ja muistiriippuvuuden välillä pätee.

## Synkronoinnin validointi

Puuttuva tai liian heikko este ei yleensä näy tuloksessa lavapipellä,
koska se suorittaa ajot käytännössä peräkkäin. Oikealla GPU:lla
peräkkäiset ajot limittyvät, ja lukeva ajo voi alkaa ennen kuin
kirjoittava on valmis. Validointikerroksen **synkronoinnin
validointi** seuraa jokaisen puskurin käyttöjä ja ilmoittaa
vaaratilanteista (hazard) riippumatta siitä, mitä laite sattuu
tekemään. Esimerkki kokeilee kahta järjestystä kolmella esteellä:

```{.cpp tiedosto="esimerkit/09-synkronointi.cpp" osa="esteet"}
```

```{.cpp tiedosto="esimerkit/09-synkronointi.cpp" osa="raw"}
```

```{.cpp tiedosto="esimerkit/09-synkronointi.cpp" osa="war"}
```

```{.tuloste tiedosto="esimerkit/09-synkronointi.odotettu"}
```

Tulos näyttää esteiden kaksi puolta:

- **Kirjoitus ennen lukua (RAW)** vaatii muistiriippuvuuden. Pelkkä
  suoritusriippuvuus takaa, että täyttö on valmis ennen kuin SAXPY
  alkaa, mutta ei sitä, että sen kirjoitukset ovat päätyneet
  välimuistista sinne, mistä SAXPY lukee. Validointi ilmoittaa
  `SYNC-HAZARD-READ-AFTER-WRITE` kummassakin tapauksessa.
- **Luku ennen kirjoitusta (WAR)** vaatii vain suoritusriippuvuuden.
  Luku ei jätä mitään näkyväksi tehtävää, joten riittää, että
  kirjoitus ei ala ennen kuin luku on valmis. Ilman estettä validointi
  ilmoittaa `SYNC-HAZARD-WRITE-AFTER-READ`.

Synkronoinnin validointi on hidas, joten se on tässä vain yhdessä
esimerkissä. Kehityksessä ja testeissä sen kannattaa olla päällä
aina, kun komentopuskurien rakennetta muutetaan.

## GPU:n ja CPU:n välinen tahdistus

Apukirjaston `suorita` lähettää komentopuskurin ja odottaa aidalla,
että GPU on valmis. Vasta sen jälkeen CPU lukee tulokset. Esimerkkien
muisti on koherenttia (`HOST_COHERENT`), joten erillistä
näkyvyystoimenpidettä ei tarvita. Ei-koherentille muistille tarvitaan
`vkInvalidateMappedMemoryRanges` ennen lukua ja
`vkFlushMappedMemoryRanges` kirjoituksen jälkeen.

Odottaminen jokaisen ajon jälkeen hukkaa rinnakkaisuutta: GPU on
toimettomana, kun CPU valmistelee seuraavaa työtä, ja päinvastoin.
Oikeassa ohjelmassa komentoja lähetetään useampi erä etukäteen, ja
aikajanasemafori kertoo, mihin asti GPU on edennyt (GPU-ohjelmoinnin
luku 9). Laskentaa voi myös ajaa erillisessä laskentajonossa
grafiikan rinnalla (*async compute*), jolloin semaforit tahdistavat
jonot.

## Työn jako

Ajojen määrä on usein suurempi pullonkaula kuin itse laskenta.
Jokainen este odottaa, että edellisen ajon viimeinen työryhmä
valmistuu, ja silloin laite on osittain tyhjä. Kolme keinoa vähentää
ajoja:

1. **Yhdistä vaiheet** (kernel fusion). Jos vaihe B lukee vain sen,
   minkä vaihe A kirjoitti samassa työryhmässä, ne voi tehdä samassa
   ajossa jaetun muistin kautta. Luvun 7 bitonisen lajittelun lohkoajo
   on tällainen yhdistelmä.
2. **Anna säikeelle enemmän työtä.** Kun jokainen säie käsittelee
   useita alkioita, työryhmiä ja osasummia on vähemmän, ja
   monivaiheisen algoritmin tasoja on vähemmän (luku 4).
3. **Atomiset operaatiot viimeisessä vaiheessa.** Kun osatuloksia on
   vähän, ne yhdistetään atomisesti ilman uutta ajoa.

Epäsuora ajo (`vkCmdDispatchIndirect`) lukee ryhmien määrän
puskurista. Edellinen ajo voi siten päättää seuraavan koon, esimerkiksi
virran tiivistyksen tuottaman jonon pituuden mukaan, ilman että CPU
lukee välitulosta.

## Käytännössä

- **Este ajojen väliin, kun data kulkee ajosta toiseen.**
  Muistieste (`SHADER_WRITE` → `SHADER_READ`) RAW-tilanteessa,
  suoritusriippuvuus WAR-tilanteessa. Liian laaja este on oikein mutta
  hidas, liian kapea on virhe.
- **Synkronoinnin validointi testeihin.** Se löytää virheet, jotka
  eivät näy lavapipellä eivätkä usein oikeallakaan laitteella ennen
  kuin kuorma muuttuu.
- **Älä odota GPU:ta turhaan.** Kokoa ajot samaan komentopuskuriin ja
  lue tulokset vasta lopuksi. Jokainen aita on tyhjä hetki sekä CPU:lle
  että GPU:lle.
- **Työryhmät eivät odota toisiaan.** Algoritmi, joka vaatii
  työryhmien välisen tahdistuksen saman ajon aikana, toimii vain
  laitteilla, jotka takaavat edistymisen, ja silloinkin vain, jos
  kaikki työryhmät mahtuvat laitteeseen kerralla.

## Itsearviointi

- Osaat käyttää `barrier()`-kutsua oikein ja selittää, miksi sen on
  oltava tasaisessa ohjausvuossa ja miksi silmukassa tarvitaan este
  myös ennen uudelleenkirjoitusta.
- Osaat selittää, miksi työryhmien välinen riippuvuus vaatii uuden
  ajon, ja kirjoittaa ajojen väliin oikean esteen.
- Osaat erottaa suoritus- ja muistiriippuvuuden ja kertoa, kumpaa RAW-
  ja WAR-tilanteet vaativat.
- Osaat vähentää ajojen määrää yhdistämällä vaiheita, antamalla
  säikeille enemmän työtä ja käyttämällä epäsuoraa ajoa.
