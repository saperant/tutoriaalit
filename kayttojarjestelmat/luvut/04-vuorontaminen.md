# Vuorontaminen

Vuorontaja (engl. scheduler) päättää, mikä ajovalmis säie saa
suorittimen seuraavaksi ja kuinka pitkäksi aikaa. Päätös tehdään
joka kerta, kun ajossa oleva säie estyy, päättyy, sen aikaviipale
loppuu tai joku tärkeämpi herää. Hyvä vuorontaja tasapainoilee
ristiriitaisten tavoitteiden välillä:

| Tavoite | Mittari | Kuka hyötyy |
|-------------|----------------------------------|-------------------------|
| Läpäisy | valmistuneita töitä aikayksikössä | eräajot, laskenta |
| Läpimenoaika | valmistuminen − saapuminen | eräajot |
| Odotusaika | aika valmiusjonossa | kaikki |
| Vasteaika | saapumisesta ensimmäiseen ajoon | vuorovaikutteiset ohjelmat |
| Reiluus | suoritinaika suhteessa osuuteen | monen käyttäjän koneet |

Lyhyt odotusaika ja hyvä vasteaika vaativat usein keskeyttämistä,
joka taas lisää kontekstinvaihtoja ja heikentää läpäisyä. Mikään
algoritmi ei ole paras kaikilla mittareilla.

## Simulaattori

Algoritmeja on helpointa vertailla simuloimalla. Aika etenee yhden
yksikön kerrallaan, ja joka hetkellä algoritmi valitsee
valmiusjonosta prosessin. Jono pidetään saapumisjärjestyksessä, ja
algoritmit eroavat vain siinä, mitä jonosta valitaan ja milloin
ajossa oleva saa keskeytyä:

```{.c tiedosto="esimerkit/04-vuorontaja.c" osa="tyypit"}
```

```{.c tiedosto="esimerkit/04-vuorontaja.c" osa="valitse"}
```

Tasapelissä voittaa jonossa aiemmin oleva. Keskeyttävät algoritmit
palauttavat ajossa olleen joka hetki jonon kärkeen ja valitsevat
uudelleen; näin ajossa oleva voittaa tasapelit, eikä prosessia
vaihdeta turhaan. Round robin palauttaa prosessin jonon perälle vasta,
kun sen kvantti on käytetty:

```{.c tiedosto="esimerkit/04-vuorontaja.c" osa="simuloi"}
```

Neljä prosessia saapuvat eri aikoina. Prioriteetissa pienempi luku on
tärkeämpi, kuten Unixin nice-arvoissa:

```{.c tiedosto="esimerkit/04-vuorontaja.c" osa="data"}
```

```{.tuloste tiedosto="esimerkit/04-vuorontaja.odotettu"}
```

Aikajanalla kukin merkki on yksi aikayksikkö. Odotusaika on
läpimenoaika vähennettynä suoritusajalla.

### FCFS

*First come, first served* ajaa prosessit saapumisjärjestyksessä
loppuun. Se on yksinkertainen ja reilu saapumisjärjestyksen mielessä,
mutta kärsii *saattueilmiöstä* (engl. convoy effect): pitkä A pitää
lyhyttä C:tä odottamassa seitsemän yksikköä, vaikka C tarvitsee vain
yhden.

### SJF ja SRTF

*Shortest job first* valitsee lyhimmän työn. Se minimoi keskimääräisen
odotusajan, kun kaikki työt ovat jonossa yhtä aikaa: lyhyen työn
siirtäminen pitkän eteen lyhentää lyhyen odotusta enemmän kuin
pidentää pitkän. Keskeyttävä versio *shortest remaining time first*
vertaa jäljellä olevaa aikaa aina uuden saapuessa, ja se saa pienimmän
odotusajan, 3,0 yksikköä. Ongelmia on kaksi. Ensinnäkin suoritusaikaa
ei tiedetä etukäteen; todelliset vuorontajat arvioivat sen
aiempien purskeiden painotettuna keskiarvona
$\tau_{n+1} = \alpha t_n + (1 - \alpha)\tau_n$. Toiseksi pitkä työ voi
*nääntyä* (engl. starvation), jos lyhyitä tulee jatkuvasti.

### Round robin

RR antaa jokaiselle vuorollaan kvantin verran aikaa ja siirtää sitten
jonon perälle. Vasteaika on hyvä – kukaan ei odota yli
$(n - 1) \cdot q$ – mutta keskimääräinen odotus on huonompi, ja
keskeytyksiä on eniten. Kvantin koko on kompromissi: liian pieni ja
kontekstinvaihdot syövät ajan, liian suuri ja RR muuttuu FCFS:ksi.
Nyrkkisääntö on, että valtaosan purskeista pitäisi mahtua yhteen
kvanttiin.

### Prioriteetit

Prioriteettivuorontaja ajaa aina tärkeimmän ajovalmiin. Esimerkissä B
ja D ohittavat A:n, ja vähiten tärkeä C odottaa loppuun asti. Matalan
prioriteetin nääntyminen estetään *ikääntämisellä* (engl. aging):
odottavan prioriteettia nostetaan ajan kuluessa.

Prioriteeteilla on myös vaarallinen sivuvaikutus, *prioriteetin
inversio*. Matala L pitää lukkoa, jota korkea H odottaa, ja keskitason
M keskeyttää L:n – jolloin H odottaa M:ää, vaikka niillä ei ole mitään
yhteistä. Mars Pathfinder -luotain käynnistyi toistuvasti uudelleen
juuri tästä syystä vuonna 1997. Ratkaisu on *prioriteetin periytys*:
lukkoa pitävä saa väliaikaisesti odottajansa prioriteetin. POSIXissa
se valitaan mutexin ominaisuudella `PTHREAD_PRIO_INHERIT`, ja
reaaliaikakäyttöjärjestelmissä se on usein oletus.

## Monitasoiset jonot

Yleiskäyttöiset vuorontajat yhdistävät edellisiä. *Monitasoinen
palautejono* (MLFQ) pitää useita jonoja eri prioriteeteilla ja
kvanteilla. Uusi prosessi aloittaa ylimmästä jonosta. Jos se käyttää
koko kvanttinsa, se on todennäköisesti laskentaa ja putoaa alemmas;
jos se estyy ennen sitä, se on vuorovaikutteinen ja pysyy ylhäällä.
Ajoittain kaikki nostetaan takaisin ylös, jottei kukaan nääntyisi.
Näin vuorontaja oppii työn luonteen tietämättä suoritusaikoja
etukäteen. BSD:t ja Windows käyttävät tämän ajatuksen muunnelmia.

## Linuxin CFS: reilu osuus

Linuxin *Completely Fair Scheduler* (versiot 2.6.23–6.5) ja sen
seuraaja EEVDF eivät käytä kiinteitä kvantteja. Tavoite on, että
$n$ yhtä tärkeää tehtävää saa kukin $1/n$ suorittimesta, ja
painotettuna tehtävä saa osuuden

$$\text{osuus}_i = \frac{w_i}{\sum_j w_j}.$$

Paino $w$ tulee nice-arvosta: nice 0 on 1024, ja jokainen askel
muuttaa painoa noin 1,25-kertaisesti, jolloin yhden askeleen ero
muuttaa suoritinaikaa noin kymmenellä prosentilla. Jokaisella
tehtävällä on *virtuaaliaika*, joka kasvaa ajon aikana painon
käänteisluvun mukaan:

$$\Delta\text{vaika} = \Delta t \cdot \frac{1024}{w}.$$

Vuorontaja ajaa aina sitä, jonka virtuaaliaika on pienin. Ytimessä
tehtävät ovat punamustassa puussa virtuaaliajan mukaan järjestettyinä,
joten pienimmän löytäminen on halpaa. Simulaatio ajaa millisekunnin
kerrallaan ja käyttää ytimen painotaulukon arvoja nice-arvoille
−5…5:

```{.c tiedosto="esimerkit/04-cfs.c" osa="valitse"}
```

Uusi tehtävä aloittaa järjestelmän pienimmästä virtuaaliajasta.
Nollasta aloittaessaan se olisi kaukana muiden jäljessä ja saisi
suorittimen yksin, kunnes kirisi muut kiinni. Sama koskee pitkään
nukkunutta: heräävä tehtävä nostetaan lähelle pienintä virtuaaliaikaa,
jottei uni kerrytä sille etuoikeutta:

```{.c tiedosto="esimerkit/04-cfs.c" osa="aja"}
```

```{.tuloste tiedosto="esimerkit/04-cfs.odotettu"}
```

Osuudet vastaavat kaavaa: $335 / (1024 + 1024 + 335) \approx 14{,}1\,\%$
ja D:n tultua $3121 / 5504 \approx 56{,}7\,\%$. Todellinen CFS ajaa
tehtävää kerrallaan pidemmän viipaleen (`sched_min_granularity`),
jotta kontekstinvaihtoja ei tule liikaa, ja tasapainottaa jonoja
suoritinten kesken. Ryhmävuorontamisella (cgroupit, ks. taito
*Virtualisointi*) osuudet jaetaan ensin ryhmille ja sitten ryhmän
sisällä.

## Linuxin vuorontamisluokat

CFS ja EEVDF koskevat tavallisia tehtäviä (`SCHED_OTHER`,
`SCHED_BATCH`, `SCHED_IDLE`). Niiden yläpuolella ovat
määräaikaluokka `SCHED_DEADLINE` ja kiinteän prioriteetin
reaaliaikaluokat `SCHED_FIFO` ja `SCHED_RR` (prioriteetit 1–99).
Korkeamman luokan ajovalmis tehtävä ajetaan aina ennen alempaa.
`SCHED_FIFO`-tehtävä ajaa, kunnes estyy tai tärkeämpi herää; ikuinen
silmukka siinä jumittaa suorittimen, joten ydin varaa oletuksena 5 %
ajasta muille (`sched_rt_runtime_us`). Reaaliaikaprioriteetin asetus
vaatii oikeuden `CAP_SYS_NICE`. Komentoriviltä politiikkaa vaihdetaan
komennolla `chrt` ja nice-arvoa komennoilla `nice` ja `renice`.

## Käytännössä

- **Valitse mittari ensin:** vuorovaikutteinen järjestelmä tarvitsee
  vasteaikaa, eräajo läpäisyä. Algoritmi seuraa tavoitteesta.
- **Keskeyttäminen maksaa:** jokainen vaihto vie aikaa ja
  välimuistin. RR:n kvantin on oltava selvästi vaihtoa pidempi.
- **Varo prioriteetin inversiota:** jos eri prioriteetin säikeet
  jakavat lukon, käytä periytyviä mutexeja.
- **Säädä nice-arvoilla, älä reaaliaikaluokilla:** `SCHED_FIFO`
  kuuluu tehtäville, joiden suoritusaika tunnetaan ja on lyhyt.
- **Simuloi ennen kuin väität:** pieni deterministinen simulaatio
  paljastaa tasapelisääntöjen ja saapumisjärjestyksen vaikutuksen,
  jota käsin laskiessa on helppo erehtyä.

## Itsearviointi

- Osaat laskea FCFS-, SJF-, SRTF-, RR- ja prioriteettivuorontajan
  aikajanan, odotusajat ja läpimenoajat annetulle prosessijoukolle.
- Osaat selittää saattueilmiön, nääntymisen ja prioriteetin
  inversion sekä niiden ratkaisut.
- Osaat kuvata monitasoisen palautejonon idean.
- Osaat selittää CFS:n virtuaaliajan ja laskea nice-arvoja vastaavat
  suoritinosuudet.
- Osaat nimetä Linuxin vuorontamisluokat ja kertoa, milloin kutakin
  käytetään.
