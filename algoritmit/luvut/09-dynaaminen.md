# Dynaaminen ohjelmointi

Hajota ja hallitse jakaa tehtävän erillisiin osatehtäviin. Monessa
tehtävässä osatehtävät ovat kuitenkin *päällekkäisiä*: sama osatehtävä
tulee vastaan monta kertaa eri reittejä pitkin. Silloin suora rekursio
laskee saman asian yhä uudelleen, ja työ kasvaa eksponentiaalisesti.
*Dynaaminen ohjelmointi* (engl. dynamic programming) laskee jokaisen
osatehtävän kerran ja tallentaa tuloksen.

Menetelmä toimii, kun tehtävällä on *optimaalinen osarakenne*:
optimiratkaisu koostuu osatehtävien optimiratkaisuista. Lyhin reitti
Helsingistä Kuopioon Mikkelin kautta sisältää lyhimmän reitin
Helsingistä Mikkeliin. Nimi on historiallinen: "ohjelmointi" tarkoitti
1950-luvulla suunnittelua taulukon avulla, ei tietokoneohjelmaa.

## Muistiinpano ja taulukointi

Fibonaccin luvut ovat yksinkertaisin esimerkki päällekkäisistä
osatehtävistä. Määritelmä $F(n) = F(n-1) + F(n-2)$ on suoraan
rekursiivinen funktio:

```{.c tiedosto="esimerkit/09-fibonacci.c" osa="suora"}
```

Kutsu $F(30)$ laskee $F(28)$:n kahdesti, $F(27)$:n kolmesti ja
$F(2)$:n yli 500 000 kertaa. Kutsuja on yhteensä $2F(n+1) - 1$, joka
kasvaa kuten $\varphi^n$, missä $\varphi \approx 1{,}618$ on kultainen
leikkaus. Kaksi korjausta on mahdollista:

```{.c tiedosto="esimerkit/09-fibonacci.c" osa="muisti"}
```

- **Muistiinpano** (engl. memoization) säilyttää rekursion mutta
  tallentaa jokaisen lasketun arvon. Toinen kutsu samalla
  argumentilla palauttaa tallennetun arvon heti. Ratkaisu etenee
  *ylhäältä alas*: alkuperäisestä tehtävästä kohti perustapauksia.
- **Taulukointi** (engl. tabulation) täyttää taulukon *alhaalta ylös*
  perustapauksista alkaen niin, että jokainen arvo lasketaan vasta,
  kun sen tarvitsemat arvot ovat valmiina. Fibonaccissa tarvitaan
  vain kaksi edellistä arvoa, joten koko taulukon voi korvata kahdella
  muuttujalla.

```{.tuloste tiedosto="esimerkit/09-fibonacci.odotettu"}
```

Muistiinpanolla kutsuja on $2n - 1$: jokainen arvo lasketaan kerran,
ja sen kahdesta kutsusta toinen laskee ja toinen hakee valmiin arvon.
Viimeinen rivi on tunnettu tulos, jolla toteutus tarkistetaan:
$F(93) = 12\,200\,160\,415\,121\,876\,738$ on suurin Fibonaccin luku,
joka mahtuu 64-bittiseen etumerkittömään kokonaislukuun. Suora
rekursio ei pääsisi siihen ikinä.

Kumpi tapa on parempi? Muistiinpano on helppo lisätä olemassa olevaan
rekursioon, ja se laskee vain ne osatehtävät, joita todella
tarvitaan. Taulukointi välttää rekursion hinnan ja pinon syvyyden, ja
sen täyttöjärjestys tekee usein mahdolliseksi säästää muistia, kuten
tässä kahteen muuttujaan. Suurissa tehtävissä taulukointi on
tavallisempi.

## Menetelmä neljässä vaiheessa

Dynaamisen ohjelmoinnin ratkaisu syntyy samalla kaavalla:

1. **Määrittele osatehtävä.** Mitä taulukon alkio `t[i][w]`
   tarkoittaa? Määritelmä kirjoitetaan sanoin koodin kommenttiin.
2. **Kirjoita rekursio.** Miten alkion arvo saadaan pienempien
   osatehtävien arvoista? Tämä on algoritmin ydin, ja sen
   oikeellisuus perustellaan optimaalisella osarakenteella.
3. **Valitse täyttöjärjestys ja perustapaukset.** Jokaisen arvon
   tarvitsemien arvojen on oltava valmiina.
4. **Rekonstruoi ratkaisu.** Taulukko kertoo optimin *arvon*. Itse
   ratkaisu luetaan kulkemalla taulukkoa takaperin ja katsomalla,
   mikä vaihtoehto tuotti kunkin arvon.

## Reppuongelma

Retkireppuun mahtuu 6 kiloa, ja tarjolla on kahdeksan tavaraa, joilla
on paino ja hyötyarvo. Mitkä tavarat otetaan, jotta arvo on
suurin? Tämä on *0/1-reppuongelma*: kukin tavara otetaan kokonaan tai
ei ollenkaan. Ahne valinta arvon ja painon suhteen mukaan ei ole
optimaalinen, ja kaikkien osajoukkojen kokeilu vie $2^n$ askelta.

Osatehtävä on `paras[i][w]`: suurin arvo, joka saadaan $i$
ensimmäisellä tavaralla, kun painoraja on $w$. Tavara $i$ joko jätetään
pois, jolloin arvo on `paras[i-1][w]`, tai otetaan mukaan, jolloin
jäljelle jää painoraja $w - p_i$ ja arvo on
`paras[i-1][w - p_i] + a_i`. Optimi on parempi näistä kahdesta:

```{.c tiedosto="esimerkit/09-reppu.c" osa="reppu"}
```

```{.tuloste tiedosto="esimerkit/09-reppu.odotettu"}
```

Rekonstruktio kulkee rivit alhaalta ylös. Jos `paras[i][w]` eroaa
rivin yläpuolisesta arvosta `paras[i-1][w]`, tavara $i$ on mukana, ja
painoraja pienenee sen painolla. Optimi jättää pois teltan: se on
painavin tavara, ja sen 2,5 kilolla saa muita tavaroita, joiden
yhteisarvo on suurempi. Raaka vertailu
tarkistaa paitsi arvon myös sen, että rekonstruoidut tavarat todella
mahtuvat rajaan ja niiden arvojen summa on sama kuin taulukon
arvo. Arvon tarkistus yksin ei löytäisi rekonstruktion virhettä.

Työ ja muisti ovat $\Theta(nW)$. Aika on *pseudopolynominen*: se on
polynominen painorajan $W$ arvossa mutta eksponentiaalinen sen
bittien määrässä. Jos painot ovat grammoja ja raja on tonni, taulukossa
on miljoona saraketta tavaraa kohden. Reppuongelma on NP-täydellinen,
joten nopeampaa yleistä ratkaisua ei tunneta; dynaaminen ohjelmointi
on silti käytännössä erinomainen, kun $W$ on kohtuullinen.

Jos ratkaisua ei tarvitse rekonstruoida, riittää yksi rivi, ja muisti
on $\Theta(W)$. Painoraja käydään silloin läpi laskevasti, jotta rivin
vasen puoli on vielä edellisen tavaran arvoja ja jokainen tavara
otetaan enintään kerran. Nousevasti käytynä sama koodi ratkaisee
rajoittamattoman reppuongelman, jossa tavaroita on rajattomasti.
Pikaopas näyttää tämän muodon.

## Tunnista dynaaminen ohjelmointi

Dynaaminen ohjelmointi on vastaus, kun tehtävä kysyy optimia tai
lukumäärää ("pienin", "suurin", "kuinka monella tavalla") ja suora
rekursio kokeilee valintoja, jotka johtavat samoihin tilanteisiin.
Tavallisia osatehtävien muotoja ovat:

| Muoto | Osatehtävä | Esimerkki |
|-------|------------|-----------|
| alkuosa | `t[i]`: ensimmäiset $i$ alkiota | suurin osasumma, kolikot |
| kaksi alkuosaa | `t[i][j]`: $a$:n ja $b$:n alkuosat | LCS, editointietäisyys |
| alkuosa ja resurssi | `t[i][w]`: $i$ alkiota, raja $w$ | reppu |
| väli | `t[i][j]`: osajono $i \ldots j$ | matriisiketju, palindromit |
| osajoukko | `t[S][v]`: joukko $S$, viimeinen $v$ | kauppamatkustaja, $2^n n$ |

Luvun 1 Kadanen algoritmi oli alkuosan muotoa, ja luvun 8
kolikkotehtävän optimi oli sama muoto. Seuraava luku käsittelee kahden
alkuosan muodon merkkijonoille.

## Käytännössä

- **Kirjoita osatehtävän määritelmä kommenttiin.** "`paras[i][w]` on
  suurin arvo $i$ ensimmäisellä tavaralla rajalla $w$" on puolet
  ratkaisusta, ja ilman sitä koodia ei voi tarkistaa.
- **Aloita muistiinpanolla, siirry taulukkoon.** Rekursio ja muisti on
  helpoin saada oikein; taulukointi on nopeampi ja säästää pinoa.
- **Rekonstruoi taulukosta, älä tallenna polkuja.** Valinnat näkyvät
  taulukon arvoista; erillinen valintataulukko on tarpeen vain, jos
  vertailu on kallis.
- **Tarkista sekä arvo että ratkaisu.** Raaka vertailu antaa optimin
  arvon; rekonstruoidun ratkaisun on oltava sallittu ja tuotettava sama
  arvo.
- **Säästä muistia täyttöjärjestyksellä.** Jos rivi tarvitsee vain
  edellisen rivin, kaksi riviä tai yksi oikein päin käyty rivi riittää.

## Itsearviointi

- Osaat tunnistaa päällekkäiset osatehtävät ja optimaalisen
  osarakenteen.
- Osaat muuttaa rekursiivisen ratkaisun muistiinpanoksi ja
  taulukoinniksi ja vertailla näitä.
- Osaat ratkaista 0/1-reppuongelman taulukolla ja rekonstruoida
  valitut tavarat.
- Osaat selittää pseudopolynomisen ajan ja yhden rivin
  reppuratkaisun täyttösuunnan.
