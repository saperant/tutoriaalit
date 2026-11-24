# Atomiset operaatiot ja histogrammi

Reduktio ja skannaus välttävät kilpailun kokonaan: jokainen säie
kirjoittaa omaan paikkaansa, ja yhdistäminen tehdään puuna. Kaikkia
tehtäviä ei voi järjestää niin. **Histogrammissa** jokainen syötteen
alkio kasvattaa yhtä lokeroa, eikä etukäteen tiedetä, mitä lokeroa.
Kaksi säiettä voi kasvattaa samaa lokeroa samaan aikaan, ja silloin
tarvitaan **atominen operaatio**: luku, muutos ja kirjoitus yhtenä
jakamattomana toimenpiteenä.

## Atomiset operaatiot GLSL:ssä

| Funktio | Toiminta | Palauttaa |
|---------|----------|-----------|
| `atomicAdd(m, v)` | `m += v` | vanhan arvon |
| `atomicMin`, `atomicMax` | minimi, maksimi | vanhan arvon |
| `atomicAnd`, `atomicOr`, `atomicXor` | bittioperaatiot | vanhan arvon |
| `atomicExchange(m, v)` | `m = v` | vanhan arvon |
| `atomicCompSwap(m, odotettu, v)` | `m = v`, jos `m == odotettu` | vanhan arvon |

Operaatiot toimivat varastopuskureissa ja jaetussa muistissa
32-bittisille kokonaisluvuille. 64-bittiset ja liukulukuversiot
vaativat laitteen piirteitä (`shaderBufferInt64Atomics`,
`VK_EXT_shader_atomic_float`). Palautettu vanha arvo tekee atomisesta
lisäyksestä myös paikanvarauksen: `paikka = atomicAdd(laskuri, 1)`
antaa jokaiselle säikeelle oman indeksin jonoon. Järjestys on
kuitenkin satunnainen, toisin kuin skannauksessa (luku 5).

Atomisuus koskee vain yhtä muistipaikkaa. Se ei tee kahdesta
peräkkäisestä operaatiosta yhtä, eikä se itsessään järjestä muita
muistioperaatioita. Jos säie kirjoittaa datan ja sen jälkeen asettaa
atomisesti lipun, toinen työryhmä voi nähdä lipun ennen dataa, ellei
väliin lisätä muistiestettä (luku 9).

## Histogrammi globaalissa muistissa

Esimerkki laskee 16 miljoonan tavun histogrammin 256 lokeroon. Data on
32-bittisinä sanoina, ja jokainen säie käsittelee yhden sanan eli
neljä tavua. Suorin toteutus kasvattaa globaalin muistin lokeroa
jokaisesta tavusta:

```{.glsl tiedosto="esimerkit/varjostimet/histo_globaali.comp" osa="globaali"}
```

Atomisia operaatioita globaaliin muistiin on yhtä monta kuin tavuja:
16 777 216. Kun data on tasaisesti jakautunutta, lisäykset jakautuvat
256 osoitteeseen, ja laitteisto voi käsitellä eri osoitteita
rinnakkain. Kun data on vinoa, lähes kaikki lisäykset osuvat samaan
lokeroon ja sarjallistuvat kuten luvun 4 atominen summa. Todellinen
data on usein vinoa: tekstissä välilyönti, kuvassa tumma tausta ja
lokeissa sama tapahtumatyyppi.

## Yksityistäminen

**Yksityistämisessä** (privatization) jokainen työryhmä kerää oman
histogramminsa jaettuun muistiin. Jaetun muistin atomiset operaatiot
ovat paljon nopeampia kuin globaalin muistin, ja kilpailijoita on
vain yhden työryhmän verran. Lopuksi jokainen säie lisää yhden
lokeron työryhmän tuloksen globaaliin histogrammiin:

```{.glsl tiedosto="esimerkit/varjostimet/histo_jaettu.comp" osa="jaettu"}
```

Jokainen säie käsittelee 16 sanaa 256 sanan harppauksin. Silloin
aliryhmän naapurisäikeet lukevat jokaisella kierroksella peräkkäisiä
sanoja, ja muistihaut yhdistyvät (luku 8). Harppaus myös vähentää
työryhmien määrää 16-osaan, joten globaaleja lisäyksiä on enintään
256 työryhmää kohden:

```{.cpp tiedosto="esimerkit/06-histogrammi.cpp" osa="ajot"}
```

```{.tuloste tiedosto="esimerkit/06-histogrammi.odotettu"}
```

Globaaleja atomisia operaatioita on 64-kertaisesti vähemmän: 262 144
tasaisella datalla ja vielä vähemmän vinolla, koska tyhjiä lokeroita
ei lisätä. Tulos on kokonaislukuja, joten se on tarkalleen sama kuin
CPU:lla laskettu, vaikka lisäysten järjestys vaihtelee joka ajossa.
Kokonaislukujen atominen lisäys on liitännäinen ja vaihdannainen, joten
järjestys ei vaikuta tulokseen.

Mittaustilassa vino data hidasti globaalia versiota lavapipelläkin, ja
yksityistetty versio oli kummallakin datalla nopein. Lavapipellä
atomiset operaatiot ovat CPU:n atomisia käskyjä, ja saman
välimuistirivin kilpailu ytimien välillä maksaa samalla tavalla kuin
oikealla GPU:lla.

Yksityistämisellä on rajansa. Jaetun muistin histogrammi vie
lokeroiden määrän verran muistia jokaisessa työryhmässä, ja se
rajoittaa käyttöastetta (luku 3). Kun lokeroita on tuhansia,
histogrammi jaetaan osiin tai data lajitellaan ensin, jolloin samat
arvot ovat peräkkäin ja ne voi laskea ilman atomisia operaatioita.
Aliryhmäoperaatioilla voi myös yhdistää aliryhmän saman lokeron
lisäykset yhdeksi (`subgroupBallot` ja yhtäsuuruusvertailu), mikä
auttaa juuri vinolla datalla.

## Atomisten operaatioiden hinta

| Tilanne | Hinta |
|---------|-------|
| jaettu muisti, eri osoitteet | lähes kuin tavallinen kirjoitus |
| jaettu muisti, sama osoite | sarjallistuu työryhmän sisällä |
| globaali muisti, eri osoitteet | L2-välimuistin läpäisy, rinnakkainen |
| globaali muisti, sama osoite | sarjallistuu koko laitteella |
| vertaa ja vaihda -silmukka | toistuu kilpailun mukaan, voi nääntyä |

Atominen operaatio, jonka paluuarvoa ei käytetä, on halvempi, koska
säikeen ei tarvitse odottaa tulosta. Kääntäjä tunnistaa tämän itse.
Vertaa ja vaihda -operaatiolla (`atomicCompSwap`) voi rakentaa minkä
tahansa atomisen päivityksen, mutta kilpailussa silmukka toistuu, ja
pahimmillaan sama säie epäonnistuu yhä uudestaan. Lukkojen
rakentaminen atomisista operaatioista on GPU:lla vaarallista: jos
lukkoa odottava säie on samassa aliryhmässä kuin lukon haltija, ne
voivat jumittaa toisensa. Ilman itsenäistä etenemistä (luku 3)
odottava säie ei koskaan päästä haltijaa jatkamaan.

## Käytännössä

- **Kilpailu ratkaisee hinnan.** Mittaa atomiset operaatiot oikealla
  datalla, myös vinolla. Tasaisella testidatalla toimiva toteutus voi
  olla tuotannossa moninkertaisesti hitaampi.
- **Yksityistä ja yhdistä.** Kerää ensin aliryhmään tai jaettuun
  muistiin, sitten yksi globaali operaatio. Sama malli toimii
  reduktiossa, histogrammissa ja jonon paikanvarauksessa.
- **Kokonaisluvut ovat deterministisiä, liukuluvut eivät.** Jos tulos
  on liukuluku ja se lasketaan atomisesti, ajo ei ole toistettava.
  Laske silloin kiinteän pisteen kokonaislukuina tai kiinteässä
  järjestyksessä.
- **Älä rakenna lukkoja.** GPU:n algoritmit suunnitellaan ilman
  lukkoja: atomiset laskurit, skannaukset ja useat ajot.

## Itsearviointi

- Osaat käyttää GLSL:n atomisia operaatioita ja selittää, mitä ne
  takaavat ja mitä ne eivät takaa.
- Osaat toteuttaa histogrammin yksityistämällä ja laskea, kuinka
  paljon se vähentää globaaleja atomisia operaatioita.
- Osaat selittää, miksi vino data hidastaa atomisia operaatioita ja
  miten kilpailua vähennetään.
- Osaat perustella, miksi lukot ovat GPU:lla vaarallisia ja miksi
  atominen liukulukusumma ei ole toistettava.
