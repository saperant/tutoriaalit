# Graafien esitystavat

Graafi on joukko solmuja ja niitä yhdistäviä kaaria. Graafien
käsitteet – aste, polku, yhtenäisyys, suunnattu ja suuntaamaton graafi –
ovat tuttuja diskreetistä matematiikasta, ja niiden algoritmit
(leveys- ja syvyyshaku, lyhimmät polut) kuuluvat taitoon *Algoritmit*.
Tämä luku käsittelee niiden välissä olevaa kysymystä: miten graafi
tallennetaan muistiin niin, että algoritmien tarvitsemat operaatiot
ovat halpoja.

Algoritmit tarvitsevat graafilta lähinnä kahta operaatiota:

1. **Onko kaari $(u, v)$ olemassa?**
2. **Mitkä ovat solmun $v$ naapurit?** – Leveyshaku, syvyyshaku,
   Dijkstra ja lähes kaikki muut graafialgoritmit käyvät läpi
   jokaisen käsittelemänsä solmun naapurit.

Esitystavat eroavat siinä, kumman ne tekevät halvaksi ja paljonko
muistia ne vievät. Ratkaisevaa on graafin *tiheys*. Graafissa, jossa on
$n$ solmua, voi olla jopa $n(n-1)/2$ kaarta, mutta todellisissa
graafeissa – tieverkot, sosiaaliset verkostot, riippuvuusgraafit,
piirilevyn kytkennät – kaaria on tavallisesti vain pieni vakio kertaa
$n$. Tällainen graafi on *harva*.

Kolme esitystapaa näkyvät rinnakkain viiden solmun graafissa. Esimerkki
tulostaa sen matriisina ja CSR-taulukoina, ja kuva on piirretty
tulosteesta:

```{.tuloste tiedosto="esimerkit/10-graafit.odotettu" rivit="1-9"}
```

```{.dot tiedosto="kaaviot/graafi-esitykset.dot" otsikko="Sama graafi matriisina, vierekkäisyyslistoina ja CSR-taulukoina. Taulukon alku paikka v osoittaa solmun v naapurien alkuun taulukossa kohde."}
```

Mittauksia varten esimerkki rakentaa suuremman harvan graafin samoilla
kolmella tavalla: 2000 solmua ja 6000 suuntaamatonta kaarta (rengas ja
satunnaisia oikoteitä), keskimäärin kuusi naapuria solmua kohti.

## Vierekkäisyysmatriisi

Vierekkäisyysmatriisi on $n \times n$ -taulukko, jonka alkio $(u, v)$
kertoo, onko kaari olemassa. Painottomassa graafissa yksi bitti
riittää:

```{.c tiedosto="esimerkit/10-graafit.c" osa="matriisi"}
```

Kaaren olemassaolo on yksi bittihaku, $O(1)$. Mutta solmun
naapureiden luettelemiseen on käytävä läpi koko rivi, $O(n)$, vaikka
naapureita olisi vain kuusi. Muistia kuluu $n^2$ bittiä kaarten
määrästä riippumatta. Matriisi sopii tiheille graafeille ja pienille
graafeille, joissa $n^2$ ei ole ongelma, sekä algoritmeille, jotka
kysyvät jatkuvasti mielivaltaisia kaaria (esimerkiksi kaikkien parien
lyhimmät polut laskeva Floyd–Warshall, taito *Algoritmit*).

## Vierekkäisyyslistat

Vierekkäisyyslistoissa jokaisella solmulla on lista naapureistaan:

```{.c tiedosto="esimerkit/10-graafit.c" osa="lista"}
```

Naapureiden läpikäynti on $O(\text{aste})$, ja muistia kuluu
$O(n + m)$, kun kaaria on $m$. Kaaren olemassaolon tarkistus vaatii
listan läpikäynnin, $O(\text{aste})$. Suuntaamattomassa graafissa
kaari tallennetaan kahdesti, kerran kummankin päätesolmun listaan.

Listat ovat joustavia: kaaren lisääminen on listan alkuun lisäämistä.
Haittana on linkitetyn listan hinta (luku 4): jokainen naapuri vie
osoittimen verran lisää muistia, ja läpikäynti seuraa osoittimia.
Esimerkissä solmut varataan yhdestä taulukosta; jos jokainen olisi
erillinen `malloc`-varaus, varaajan otsake kasvattaisi kulutusta
entisestään ja solmut olisivat hajallaan muistissa. Listan tilalla
voi käyttää jokaiselle solmulle omaa vektoria (luku 3), mikä poistaa
osoittimet mutta säilyttää jokaisen solmun erillisen varauksen.

## CSR

Jos graafi ei muutu rakentamisen jälkeen, kaikki naapurilistat voi
pakata yhteen taulukkoon peräkkäin. Toinen taulukko kertoo, mistä
kohdasta kunkin solmun naapurit alkavat. Tämä on *CSR*-esitys
(engl. compressed sparse row), sama, jota käytetään harvoille
matriiseille numeerisessa laskennassa.

```{.c tiedosto="esimerkit/10-graafit.c" osa="csr"}
```

Rakennus tehdään kolmella läpikäynnillä. Ensin lasketaan jokaisen
solmun aste. Sitten asteista lasketaan kumulatiivinen summa, joka
antaa kunkin solmun alkukohdan (kuvan graafissa asteet 2, 3, 2, 2 ja 1
antavat alkukohdat 0, 2, 5, 7 ja 9). Lopuksi naapurit kirjoitetaan
paikoilleen apulaskurin avulla. Kaikki on $O(n + m)$, eikä
välivaiheessa tarvita listoja. Naapureiden läpikäynti on yksinkertainen
silmukka (tässä pääohjelman tarkistuksesta, joka vertaa naapuria
matriisiin):

```{.c tiedosto="esimerkit/10-graafit.c" osa="naapurit"}
```

Pääohjelma tarkistaa, että kaikki kolme esitystä kertovat samat
naapurit, ja vertaa muistinkulutusta:

```{.tuloste tiedosto="esimerkit/10-graafit.odotettu" alkaen="2000 solmua"}
```

Matriisi vie lähes kymmenkertaisesti listojen ja listat lähes
nelinkertaisesti CSR:n verran muistia. CSR tallentaa naapuria kohti
vain neljän tavun solmunumeron, kun listan solmu vie kuusitoista
(numero, täyte ja osoitin). Lisäksi CSR:n naapurit ovat peräkkäin
muistissa, joten niiden läpikäynti on välimuistille ihanteellinen
(luku 11).

## Valinta

| Ominaisuus | Matriisi | Listat | CSR |
|----------------|----------------|----------------|----------------|
| Muisti | $n^2$ bittiä | $O(n + m)$, osoittimet | $O(n + m)$, ei osoittimia |
| Onko kaari $(u, v)$? | $O(1)$ | $O(\text{aste})$ | $O(\text{aste})$, lajiteltuna $O(\log \text{aste})$ |
| Naapurit | $O(n)$ | $O(\text{aste})$ | $O(\text{aste})$, peräkkäin |
| Kaaren lisäys | $O(1)$ | $O(1)$ | rakennettava uudelleen |
| Sopii | tiheät ja pienet graafit | muuttuvat graafit | suuret, muuttumattomat graafit |

Painotetussa graafissa CSR:ään lisätään kolmas taulukko painoille
samoilla indekseillä kuin `kohde`-taulukkoon. Suunnatussa graafissa
kaari tallennetaan vain kerran; jos algoritmi tarvitsee myös
saapuvat kaaret, rakennetaan toinen CSR käänteisille kaarille.

Solmujen numerointi on kaikkien esitystapojen edellytys. Jos solmut
ovat alun perin nimiä tai tunnisteita, ne muunnetaan ensin
kokonaisluvuiksi $0 \ldots n - 1$ hajautustaululla (luku 6), ja
algoritmit käsittelevät vain numeroita.

## Käytännössä

- **Oletuksena vierekkäisyyslistat tai CSR.** Todelliset graafit ovat
  harvoja, ja matriisi tuhlaa muistia neliöllisesti.
- **CSR muuttumattomalle graafille.** Rakenna kerran kolmella
  läpikäynnillä, käytä monta kertaa.
- **Numeroi solmut.** Kokonaislukutunnisteet tekevät esityksistä
  tiiviitä taulukoita; nimet muunnetaan numeroiksi kerran.
- **Lajittele naapurit,** jos kaaren olemassaoloa kysytään usein:
  CSR-rivin puolitushaku on $O(\log \text{aste})$.
- **Tarkista esitykset toisiaan vasten.** Kaksi esitystä samasta
  graafista on hyvä vertailutesti rakennusfunktioille.

## Itsearviointi

- Osaat kertoa, mitkä operaatiot ovat halpoja vierekkäisyysmatriisissa
  ja mitkä vierekkäisyyslistoissa.
- Osaat laskea, paljonko muistia kukin esitystapa vie annetulle
  graafille.
- Osaat rakentaa CSR-esityksen kaarilistasta asteluvuilla ja
  kumulatiivisella summalla.
- Osaat valita esitystavan graafin tiheyden ja muuttuvuuden
  perusteella.
