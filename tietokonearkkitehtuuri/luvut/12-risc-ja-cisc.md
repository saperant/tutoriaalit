# RISC, CISC ja mikro-operaatiot

Käskykantojen historiassa on kaksi koulukuntaa. **CISC** (*complex
instruction set computer*) pyrki tekemään jokaisesta käskystä
mahdollisimman ilmaisuvoimaisen: muistioperandit missä tahansa
käskyssä, monimutkaiset osoitustavat, merkkijono- ja jopa
polynomikäskyt (VAX:n `POLY`). **RISC** (*reduced instruction set
computer*) pyrki päinvastaiseen: vähän yksinkertaisia, säännöllisiä
käskyjä, jotka on helppo liukuhihnoittaa. Tämä luku kertoo, miksi
kumpikin syntyi, ja miksi ero on nykyisissä suorittimissa pienempi kuin
nimistä voisi päätellä.

## Miksi CISC

1960- ja 1970-luvulla muisti oli kallista ja hidasta, ja kääntäjät
olivat alkeellisia. Tiivis koodi säästi muistia, ja monimutkainen käsky
oli nopeampi kuin sama asia useana käskynä, koska käskyjen nouto
muistista oli pullonkaula. Mikro-ohjelmointi (luku 3) teki
monimutkaisista käskyistä halpoja toteuttaa: uusi käsky oli vain uusi
mikro-ohjelma ROM:ssa. Käskykannasta tuli korkean tason kielen
kaltainen, mikä myös helpotti assemblyllä ohjelmointia.

## Miksi RISC

1970-luvun lopulla IBM:n John Cocke (801-projekti), Berkeleyn David
Patterson (RISC-I) ja Stanfordin John Hennessy (MIPS) mittasivat, mitä
käskyjä kääntäjät oikeasti tuottivat. Valtaosa suoritetuista käskyistä
oli yksinkertaisia latauksia, talletuksia, yhteenlaskuja ja haaroja,
ja monimutkaiset käskyt olivat usein *hitaampia* kuin vastaava
yksinkertaisten käskyjen jono, koska mikro-ohjelma oli yleiskäyttöinen.
Johtopäätös:

- Tee yleiset käskyt nopeiksi ja jätä harvinaiset ohjelmistolle.
- Käytä piipinta-ala rekistereihin, liukuhihnaan ja välimuistiin, ei
  mikrokoodiin.
- Anna kääntäjän tehdä ajoitus ja rekisterien varaus.

Tuloksena oli lataa–talleta-arkkitehtuuri, kiinteäpituiset käskyt,
paljon rekistereitä ja ohjaus kombinaatiologiikalla. Ensimmäiset
RISC-suorittimet olivat samalla tekniikalla nopeampia kuin
CISC-kilpailijansa.

| Piirre | Tyypillinen CISC | Tyypillinen RISC |
|--------|------------------|------------------|
| Käskyn pituus | vaihteleva (x86: 1–15 tavua) | kiinteä (4 tavua, C-laajennuksella 2) |
| Muistioperandit | useimmissa käskyissä | vain lataus ja talletus |
| Osoitustavat | monia, myös epäsuoria | rekisteri + siirtymä |
| Rekistereitä | 8–16 | 32 |
| Ohjaus | mikrokoodi | kombinaatiologiikka |
| Liput | ehtoliput sivuvaikutuksena | ei lippuja (RISC-V) tai erilliset |

## Mikro-operaatiot

x86 ei kuitenkaan kuollut. Intel ratkaisi ongelman Pentium Pro
-suorittimessa (1995): purkuvaihe kääntää jokaisen x86-käskyn yhdeksi tai
useammaksi RISC-tyyppiseksi **mikro-operaatioksi** (µop), ja kaikki sen
jälkeen on epäjärjestyksessä suorittava RISC-ydin. Lelumalli purusta:

```{.cpp tiedosto="esimerkit/12-mikrooperaatiot.cpp" osa="purku"}
```

```{.cpp tiedosto="esimerkit/12-mikrooperaatiot.cpp" osa="taulu"}
```

```{.tuloste tiedosto="esimerkit/12-mikrooperaatiot.odotettu"}
```

Muistioperandi tuottaa erillisen latauksen, ja muistikohde lisäksi
talletuksen, joka on jaettu osoitteen laskentaan (`tal-os`) ja datan
siirtoon (`tal-data`). `add [ebx+8], eax` on siis neljä µop:ia, eli
samat neljä operaatiota, jotka RISC-V tekisi neljällä käskyllä. `push`
ja `call` tallettavat pinoon; pino-osoittimen päivitys hoituu erillisellä
*stack engine* -laitteistolla ilman µop:ia.

Kaksi optimointia pienentää µop-määrää:

- **Makrofuusio**: vertailu ja sitä seuraava ehdollinen hyppy
  (`cmp` + `jl`) sulautetaan yhdeksi µop:ksi. Malli näyttää tämän
  rivillä `(sulautui)`.
- **Mikrofuusio**: lataus ja laskutoimitus (`add eax, [mem]`) kulkevat
  purusta poistoon yhtenä alkiona ja erotetaan vain suoritusyksiköissä.

Harvinaiset ja monimutkaiset käskyt (`rep movsb`, `cpuid`, `div` joissain
malleissa) ajetaan yhä mikrokoodilla, joka tuottaa µop-jonon
mikrokoodi-ROM:sta.

## Silmukka kahdella käskykannalla

Sama taulukon summaus x86:lla ja RISC-V:llä:

```{.cpp tiedosto="esimerkit/12-mikrooperaatiot.cpp" osa="silmukka"}
```

Tulosteen lopussa: kumpikin käyttää neljä käskyä kierrosta kohden.
x86-koodi on puolet lyhyempi (8 tavua 16:n sijaan), mutta µop:eja on
yhtä monta kuin RISC-V:n käskyjä. x86 hyötyy skaalatusta
indeksiosoitteesta (`[esi+ecx*4]`), RISC-V osoittimen kasvatuksesta.
C-laajennuksella RISC-V:n silmukka lyhenisi 10–12 tavuun, jos
rekisterit valitaan tiivistettyjen käskyjen kahdeksasta rekisteristä.

## Purun hinta

Kun suoritusydin on RISC-tyyppinen kummassakin, ero jää etupäähän.
Neljä RISC-V-käskyä on helppo purkaa rinnakkain, koska jokainen alkaa
neljällä jaollisesta osoitteesta (tai C-laajennuksella parillisesta, ja
pituus näkyy kahdesta bitistä). x86-käskyn pituus selviää vasta, kun
etuliitteet, opcode, ModRM- ja SIB-tavut on tulkittu, joten rinnakkainen
purku vaatii joko pituuden ennakoivaa merkitsemistä välimuistissa tai
pituuden arvaamista jokaisesta tavusta. Siksi nykyisissä
x86-suorittimissa on **µop-välimuisti** (*decoded stream buffer*,
*op cache*), joka tallentaa jo puretut µop:t: kuumat silmukat ohittavat
purkajan kokonaan, mikä säästää sekä aikaa että energiaa.

Purkajan osuus ytimen energiasta ja pinta-alasta on nykyään muutamia
prosentteja, joten käskykannan vaikutus suorituskykyyn on pieni
verrattuna mikroarkkitehtuuriin. ARMin Apple M1 ja AMD:n Zen ovat
samaa suuruusluokkaa saman valmistustekniikan ja tehobudjetin
puitteissa. Käskykanta ratkaisee enemmän muilla tavoilla:
ohjelmistoyhteensopivuus, lisensointi (x86 on suljettu, ARM
lisensoitava, RISC-V avoin) ja se, kuinka helposti käskykantaa voi
laajentaa omilla käskyillä.

## Käytännössä

- **Älä arvioi suorituskykyä käskymäärästä.** CISC-käsky voi olla yksi
  tai kymmeniä µop:eja. Agner Fogin käskytaulukot ja uops.info
  kertovat jokaisen x86-käskyn µop-määrän, viiveen ja läpäisyn.
- **Vältä mikrokoodattuja käskyjä kuumassa silmukassa.** `div` on
  kymmeniä jaksoja, `rep`-etuliitteiset merkkijonokäskyt ovat nopeita
  vain tietyissä koko- ja kohdistusrajoissa. Kääntäjä tietää nämä
  (`-mtune`), käsin kirjoitettu assembly ei automaattisesti.
- **Tiheys merkitsee käskyvälimuistille.** Suurissa ohjelmissa
  (tietokannat, selaimet) käskyvälimuistin ja µop-välimuistin hudit
  ovat merkittäviä. Profiiliohjattu optimointi ja linkkerin
  funktiojärjestely (BOLT) pakkaavat kuuman koodin yhteen.
- **Käskykannan valinta on ekosysteemin valinta.** Uudessa sulautetussa
  tuotteessa RISC-V:n avoimuus ja laajennettavuus ovat etu; valmiiden
  työkalujen, kirjastojen ja ajureiden kypsyys kannattaa kuitenkin
  tarkistaa.

## Itsearviointi

- Osaat selittää, mitkä teknologiset olosuhteet suosivat CISC:iä
  1970-luvulla ja RISC:iä 1980-luvulla.
- Osaat purkaa x86-käskyn mikro-operaatioiksi ja selittää makro- ja
  mikrofuusion.
- Osaat verrata saman silmukan koodin tiheyttä ja µop-määrää kahdella
  käskykannalla.
- Osaat perustella, miksi vaihtelevan pituinen koodaus vaikeuttaa
  rinnakkaista purkua ja miten µop-välimuisti auttaa.
