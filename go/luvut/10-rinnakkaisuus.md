# Goroutinet, kanavat ja context {.runko-rinnakkaisuus}

Rinnakkaisuus on Go:n tunnetuin ominaisuus. Rinnakkaisuuden yleiset
käsitteet, kuten kilpailutilanteet, lukot ja muistimallit, käsitellään
taidossa *Rinnakkaisohjelmointi*. Tämä luku keskittyy Go:n välineisiin
ja niiden idiomeihin.

## Goroutinet

`go f(x)` käynnistää funktion uudessa *goroutinessa*. Goroutine on
ajonaikaisen ympäristön hallitsema kevyt säie: sen pino alkaa
muutamasta kilotavusta ja kasvaa tarvittaessa, ja ajoitin jakaa
goroutinet käyttöjärjestelmän säikeille (`GOMAXPROCS`, oletuksena
suoritinytimien määrä). Kun goroutine odottaa I/O:ta, kanavaa tai
lukkoa, säie siirtyy ajamaan toista. Siksi verkkopalvelin voi käyttää
yhtä goroutinea yhteyttä kohden ilman tapahtumasilmukkaa ja
takaisinkutsuja.

Goroutinella ei ole paluuarvoa eikä kahvaa. Sen valmistumista odotetaan
`sync.WaitGroup`-laskurilla tai kanavalla, ja tulokset välitetään
kanavaa tai jaettua, suojattua muuttujaa pitkin. Pääohjelman päättyminen
lopettaa kaikki goroutinet.

## Kanavat

Kanava `chan T` välittää arvoja goroutinejen välillä ja synkronoi ne:

- Puskuroimattomassa kanavassa (`make(chan T)`) lähettäjä odottaa
  vastaanottajaa ja päinvastoin.
- Puskuroidussa kanavassa (`make(chan T, n)`) lähettäjä odottaa vain,
  kun puskuri on täynnä.
- `close(k)` ilmoittaa, ettei arvoja enää tule. `range k` päättyy, ja
  vastaanotto suljetusta kanavasta palauttaa heti nolla-arvon ja
  `ok == false`. Kanavan sulkee lähettäjä, koskaan vastaanottaja.
- Lähetys suljettuun kanavaan aiheuttaa paniikin. Lähetys ja vastaanotto
  `nil`-kanavaan odottavat ikuisesti.

```{.go tiedosto="esimerkit/10-kanavat.go" osa="perus"}
```

`select` odottaa useaa kanavatoimintoa ja suorittaa ensimmäisen, joka
voi edetä. `default`-haara tekee valinnasta tukkeutumattoman:

```{.go tiedosto="esimerkit/10-kanavat.go" osa="select"}
```

```{.tuloste tiedosto="esimerkit/10-kanavat.odotettu"}
```

Kanavasuunta kirjoitetaan tyyppiin: `<-chan T` vain vastaanottaa ja
`chan<- T` vain lähettää. Funktio, joka palauttaa `<-chan T`, lupaa
kutsujalle, että se itse sulkee kanavan.

Jos kaikki goroutinet odottavat, ajonaikainen ympäristö havaitsee
umpikujan ja lopettaa ohjelman:

```{.go tiedosto="esimerkit/10-umpikuja.kaatuu.go"}
```

```{.tuloste tiedosto="esimerkit/10-umpikuja.virhe"}
```

Havainto koskee vain koko ohjelman umpikujaa. Jos yksikin goroutine
on toiminnassa, esimerkiksi verkkopalvelin, jumiutuneet goroutinet
jäävät huomaamatta.

## Työntekijäallas

Rinnakkaisuuden rajaaminen kiinteään määrään goroutineja on yleisin
malli. Tehtävät tulevat kanavasta, tulokset menevät toiseen, ja
`WaitGroup` kertoo, milloin tuloskanavan voi sulkea:

```{.go tiedosto="esimerkit/10-tyojono.go" osa="allas"}
```

```{.tuloste tiedosto="esimerkit/10-tyojono.odotettu"}
```

Valmistumisjärjestys vaihtelee ajosta toiseen, joten tulokset
lajitellaan. Pelkän samanaikaisuuden rajaamiseen riittää myös
puskuroitu kanava semaforina: `sem := make(chan struct{}, n)`,
`sem <- struct{}{}` ennen työtä ja `<-sem` sen jälkeen.

## Jaettu tila

Kanava ei ole aina paras väline. Kun goroutinet päivittävät yhteistä
tilaa, lukko on yksinkertaisempi ja nopeampi:

| Tilanne | Väline |
|---------|--------|
| Datan omistus siirtyy, työn jakaminen, tapahtumat | kanava |
| Yhteinen välimuisti, laskurit, tila rakenteessa | `sync.Mutex`, `sync.RWMutex` |
| Yksi luku tai lippu | `sync/atomic` (`atomic.Int64`, `atomic.Bool`) |
| Kertaluonteinen alustus | `sync.Once`, `sync.OnceValue` |
| Odota, että goroutinet valmistuvat | `sync.WaitGroup` |
| Peruutus ja aikaraja | `context.Context` |

```{.go tiedosto="esimerkit/10-laskuri.go" osa="versiot"}
```

```{.go tiedosto="esimerkit/10-laskuri.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-laskuri.odotettu"}
```

Synkronoimaton `n++` on *datakilpailu*: kaksi goroutinea lukee ja
kirjoittaa samaa muuttujaa ilman synkronointia. Go:n muistimallissa
datakilpailun sisältävän ohjelman tulos on määrittelemätön.
Kilpailutilanteiden tunnistin (*race detector*) löytää kilpailut
ajonaikana:

```
$ go run -race 10-laskuri.go -kilpa
==================
WARNING: DATA RACE
Read at 0x00c00011c088 by goroutine 12:
  main.main.func1()
      10-laskuri.go:49 +0x2e
...
exit status 66
```

Tämän tutoriaalin testit ajavat esimerkin ja moduulin testit
tunnistimen kanssa (`esimerkit/Makefile`). Tunnistin hidastaa ohjelmaa
moninkertaisesti ja löytää vain ne kilpailut, jotka ajossa todella
tapahtuvat, joten testit ajetaan sen kanssa säännöllisesti.

## context: peruutus ja aikarajat

`context.Context` kuljettaa peruutuksen, aikarajan ja pyyntökohtaiset
arvot kutsuketjun läpi. Se on funktion ensimmäinen parametri, nimeltään
`ctx`. Funktio, joka odottaa (verkko, tietokanta, kanava), tarkistaa
`ctx.Done()`-kanavan ja palauttaa `ctx.Err()`-virheen, kun konteksti
perutaan.

Tyypillisin rinnakkaisuusvirhe on *goroutine-vuoto*: goroutine jää
odottamaan kanavaa, jota kukaan ei enää lue. Seuraavassa haku
aikakatkaistaan, mutta hakeva goroutine jää jumiin lähetykseensä:

```{.go tiedosto="esimerkit/10-vuoto.go" osa="vuotava"}
```

```{.go tiedosto="esimerkit/10-vuoto.go" osa="korjattu"}
```

```{.tuloste tiedosto="esimerkit/10-vuoto.odotettu"}
```

Yhden paikan puskuri riittää: lähetys onnistuu aina, ja goroutine
päättyy, vaikka tulosta ei koskaan lueta. Toinen korjaus on välittää
`ctx` hakufunktiolle, joka keskeyttää itse työnsä.

Putkessa (*pipeline*) jokainen vaihe on goroutine, joka lukee
edellisen vaiheen kanavaa. Ensimmäinen virhe peruu kontekstin, ja kaikki
vaiheet lopettavat:

```{.go tiedosto="esimerkit/10-putki.go" osa="vaiheet"}
```

```{.go tiedosto="esimerkit/10-putki.go" osa="ryhma"}
```

```{.tuloste tiedosto="esimerkit/10-putki.odotettu"}
```

`context.WithCancelCause` (Go 1.20) tallentaa perumisen syyn, jonka
`context.Cause` palauttaa. Sama malli on valmiina paketissa
`golang.org/x/sync/errgroup`: `g.Go(f)` käynnistää goroutinen, ja
`g.Wait()` palauttaa ensimmäisen virheen ja peruu ryhmän kontekstin.

## Käytännössä

- **Tiedä, miten jokainen goroutine päättyy.** Ennen `go`-lausetta
  on pystyttävä sanomaan, mikä lopettaa goroutinen: kanavan sulkeminen,
  kontekstin peruutus tai työn valmistuminen.
- **Kutsuja päättää rinnakkaisuudesta.** Kirjastofunktio on
  synkroninen, ja kutsuja käynnistää sen goroutinessa tarvittaessa.
  Funktio, joka käynnistää goroutineja, myös odottaa niitä.
- **Kanava omistuksen siirtoon, lukko tilaan.** "Jaa muisti
  viestimällä" on hyvä oletus, mutta suojattu kartta on selkeämpi kuin
  kanavien verkko.
- **Rajaa rinnakkaisuus.** Goroutine jokaiselle syötteen riville voi
  avata tuhansia yhteyksiä yhtä aikaa. Työntekijäallas tai semafori
  rajaa kuorman.
- **`ctx` ensimmäisenä parametrina**, ei rakenteen kenttänä. Kutsu
  `cancel` aina, mieluiten `defer`-lauseella, jotta ajastimet ja
  goroutinet vapautuvat.
- **Testit `-race`-lipulla** CI:ssä. Tunnistin ei löydä kaikkea, mutta
  sen löydökset ovat aina oikeita virheitä.
- **Hinta.** Goroutinen käynnistys maksaa noin mikrosekunnin ja
  kilotavuja muistia, kanavaoperaatio kymmeniä nanosekunteja, lukko
  kilpailemattomana noin kymmenen ja atominen operaatio muutaman.
  Hyvin pienen työn jakaminen goroutineille on hitaampaa kuin sen
  tekeminen suoraan.

## Itsearviointi

- Osaat käynnistää goroutineja, odottaa niitä `WaitGroup`-laskurilla
  ja välittää tuloksia kanavilla.
- Osaat käyttää puskuroituja ja puskuroimattomia kanavia,
  `close`-kutsua ja `select`-lausetta oikein.
- Osaat toteuttaa työntekijäaltaan ja putken, jotka eivät vuoda
  goroutineja.
- Osaat valita kanavan, lukon ja atomisen operaation välillä.
- Osaat käyttää `context`-pakettia peruutukseen ja aikarajoihin.
- Osaat löytää datakilpailut `-race`-lipulla.
