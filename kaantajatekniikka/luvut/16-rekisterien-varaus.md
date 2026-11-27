# Rekisterien varaus

Välikielessä rekistereitä on rajattomasti; RISC-V:llä niitä on 31, ja
niistä Kide varaa arvoille yksitoista. **Rekisterien varaus**
(*register allocation*) päättää, mikä virtuaalirekisteri on missäkin
fyysisessä rekisterissä ja mitkä joudutaan viemään pinoon
(*spill*). Se on takaosan tärkein optimointi: rekisteri luetaan
yhdessä kellojaksossa, muistiin osuva lataus vie useita jaksoja, ja
jokainen latauskäsky vie tilaa käskyvälimuistista.

Kahdella virtuaalirekisterillä voi olla sama fyysinen rekisteri, jos
ne eivät ole koskaan yhtä aikaa eläviä. Varaus on siis elävyyden
(luku 10) sovellus.

## Elinvälit

Yksinkertaisin tapa kuvata, milloin rekisteri on elävä, on
**elinväli** (*live interval*): käskyt numeroidaan lohkojen
järjestyksessä, ja rekisterin väli ulottuu sen ensimmäisestä
esiintymästä viimeiseen. Jos rekisteri on elävä lohkon alussa tai
lopussa, väli venytetään lohkon reunaan; näin silmukan yli elävä arvo
kattaa koko silmukan.

```{.cpp tiedosto="esimerkit/kide/rekisterit.cpp" osa="elinvalit"}
```

Käskyllä on kaksi sijaintia: operandit luetaan parillisessa ja tulos
kirjoitetaan parittomassa. Arvo, joka kuolee käskyssä, ja käskyn tulos
eivät siksi ole yhtä aikaa eläviä, ja ne voivat käyttää samaa
rekisteriä, kuten käskyssä `add s1, s1, s2`. Elinväli on konservatiivinen
yksinkertaistus: rekisterin elinikään voi kuulua aukkoja (esimerkiksi
`if`-haara, jossa arvoa ei tarvita), mutta väli kattaa ne.

Varauksen tulos on jokaiselle virtuaalirekisterille *paikka*:
`s`-rekisterin numero 1–11 tai pinopaikan numero. Lisäksi talletetaan
käytettyjen `s`-rekisterien luettelo prologia ja epilogia varten.

## Lineaarinen pyyhkäisy

**Lineaarinen pyyhkäisy** (*linear scan*, Poletto ja Sarkar 1999)
käy elinvälit alkukohdan mukaan järjestettyinä. Aktiivisten välien
listassa ovat välit, joilla on rekisteri. Kun uusi väli alkaa,
päättyneet välit vapauttavat rekisterinsä; jos vapaata rekisteriä ei
ole, pinoon viedään se väli, joka päättyy viimeisenä, koska se
varaisi rekisteriä pisimpään:

```{.cpp tiedosto="esimerkit/kide/rekisterit.cpp" osa="lineaarinen"}
```

Algoritmi on nopea (lähes lineaarinen välien määrässä), ja siksi sitä
käytetään JIT-kääntäjissä, joissa käännösaika on osa suoritusaikaa
(HotSpotin C1, V8:n varhaiset tasot, LuaJIT). Luvun 10 summafunktion
välit ja varaus 11 rekisterillä (`--vaihe=valit`):

```{.tuloste tiedosto="esimerkit/naytteet/valit-summa.txt"}
```

Ajoituskaaviona näkyy, miksi tilapäisarvot voivat jakaa `s4`:n:
niiden välit eivät mene päällekkäin. Vain `%5` ja `%6` elävät yhtä
aikaa, joten `%6` saa oman rekisterinsä `s5`.

```{.ajoituskaavio tiedosto="kaaviot/valit-summa.json" otsikko="Funktion summa elinvälit ja varatut rekisterit"}
```

Väliaikaiset `%3`–`%9` ovat lyhytikäisiä ja jakavat lähes kaikki
`s4`:n. Pinoa ei tarvita. Kun rekistereitä on vain kaksi (`--rekistereita=2`), kolme
koko silmukan ajan elävää arvoa joutuu pinoon:

```{.tuloste tiedosto="esimerkit/naytteet/valit-summa-2.txt"}
```

Valinta on heuristiikan mukainen mutta huono: silmukan ehto
`le i, n` vaatii nyt kaksi latausta pinosta joka kierroksella, ja
`s = add s, i` kaksi latausta ja tallennuksen. Pinoon joutuivat juuri ne
arvot, joita silmukka käyttää joka kierroksella, ja rekisterit jäivät
lyhytikäisille väliaikaisille. Pisimmän välin heuristiikka ei tiedä
silmukoista mitään. Tuotantovaraajat laskevat jokaiselle välille
**viennin hinnan** (*spill cost*): käyttökertojen määrä painotettuna
silmukoiden syvyydellä, tyypillisesti $10^{\text{syvyys}}$. Silmukan
sisällä käytetty arvo on silloin kallis viedä pinoon.

## Pinosta rekistereihin

Rekisterien vaikutus näkyy samasta funktiosta kahdella varauksella.
Funktio `nelioiden_summa` vei kaikki pinoon -varauksella 13 käskyä
rungossaan (luku 15); lineaarisella pyyhkäisyllä optimoituna:

```{.gnuassembler tiedosto="esimerkit/naytteet/asm-lineaarinen.txt"}
```

Rungossa on enää kolme laskentakäskyä ja paluuarvon siirto.
Prologin ja epilogin `s`-rekisterien tallennukset ovat nyt suurin
kustannus, koska Kide varaa vain kutsun säilyttämiä rekistereitä.
Lehtifunktio, joka ei kutsu mitään, voisi käyttää `t`- ja
`a`-rekistereitä, joita ei tarvitse tallentaa; tuotantovaraajat
valitsevat rekisteriluokan sen mukaan, eläkö arvo kutsun yli.

## Graafinväritys

Klassinen vaihtoehto on **graafinväritys** (*graph coloring*,
Chaitin 1982, Briggs 1994). Rakennetaan **interferenssigraafi**: solmuina
ovat virtuaalirekisterit, ja kaari yhdistää kaksi rekisteriä, jos ne ovat
jossakin kohdassa yhtä aikaa eläviä. Rekisterien varaus on graafin
värittämistä $k$ värillä niin, ettei kaaren päissä ole samaa väriä.

Värittäminen on NP-täydellinen, mutta Chaitinin heuristiikka toimii
hyvin: solmu, jolla on alle $k$ naapuria, voidaan aina värittää, joten
se poistetaan graafista pinoon ja jatketaan. Jos sellaista solmua ei
ole, valitaan halvin pinoon vietävä. Lopuksi solmut väritetään
käänteisessä järjestyksessä. Samaan kehykseen kuuluu kopioiden
**yhdistäminen** (*coalescing*): kopiolla yhdistetyt solmut, jotka eivät
interferoi, sulautetaan, jolloin ne saavat saman värin ja kopio katoaa.

| Menetelmä | Laatu | Nopeus | Käyttäjiä |
|-----------|-------|--------|-----------|
| kaikki pinoon | huono | erittäin nopea | `-O0`-käännökset |
| lineaarinen pyyhkäisy | kohtuullinen | nopea | JIT-kääntäjät |
| graafinväritys | hyvä | hitaampi | GCC (IRA), monet AOT-kääntäjät |
| LLVM:n *greedy* | hyvä | kohtuullinen | Clang, rustc |

SSA-muodossa interferenssigraafi on aina *kordaalinen*, ja sen voi
värittää optimaalisesti polynomisessa ajassa. Tämä havainto (2005)
on johtanut SSA-pohjaisiin varaajiin, joissa varaus tehdään ennen
SSA:sta poistumista.

## Käytännössä

- **Varaus on elävyyden sovellus.** Ensin oikea elävyysanalyysi, sitten
  varaus; virheellinen elävyys tuottaa koodia, jossa kaksi arvoa
  kirjoittaa samaan rekisteriin.
- **Pinoon viennin hinta ratkaisee laadun.** Silmukoiden sisällä
  käytetyt arvot pidetään rekistereissä; harvoin käytetyt saavat mennä
  pinoon.
- **Testaa varaaja rekisteripulalla.** Kiden testit ajavat jokaisen
  ohjelman myös yhdellä ja kahdella rekisterillä, jolloin pinoon vienti
  ja lataukset tulevat testatuiksi; täydellä rekisterimäärällä ne eivät
  koskaan suoritu.
- **Valitse menetelmä käännösajan mukaan.** JIT tarvitsee nopean
  varaajan; AOT-kääntäjä voi käyttää enemmän aikaa.

## Itsearviointi

- Osaat laskea elinvälit elävyystiedosta ja selittää, miksi käskyllä on
  erilliset luku- ja kirjoitussijainnit.
- Osaat toteuttaa lineaarisen pyyhkäisyn ja kertoa, miten se valitsee
  pinoon vietävän välin.
- Osaat rakentaa interferenssigraafin ja kuvata Chaitinin
  värityksen ja kopioiden yhdistämisen periaatteen.
- Osaat arvioida varauksen laatua assemblystä ja selittää viennin
  hinnan merkityksen silmukoissa.
