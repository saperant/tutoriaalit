# Säikeet, Send, Sync ja async {.runko-rinnakkaisuus}

Rustin lupaus on "pelottomat säikeet" (*fearless concurrency*):
turvallisessa koodissa datakilpailu on käännösvirhe. Sama
omistajuussääntö, joka estää roikkuvat viitteet, estää kahta säiettä
muokkaamasta samaa dataa ilman synkronointia. Lukkiutumia ja loogisia
kilpailutilanteita kieli ei estä. Rinnakkaisuuden yleiset käsitteet
käsitellään taitopuun taidossa *Rinnakkaisohjelmointi*; tässä luvussa
keskitytään Rustin keinoihin.

## Send ja Sync

Säieturvallisuus ilmaistaan kahdella merkkipiirteellä, jotka kääntäjä
päättelee automaattisesti tyypin kentistä:

- `Send`: arvon voi *siirtää* toiseen säikeeseen.
- `Sync`: arvoon voi *viitata* useasta säikeestä (`&T` on `Send`).

Lähes kaikki tyypit ovat molempia. Poikkeuksia ovat `Rc` (laskuri ei
ole atominen), `RefCell` ja `Cell` (ei `Sync`) sekä raa'at osoittimet.
`thread::spawn` vaatii, että sulkeuma on `Send` ja `'static`, joten
`Rc`-tyypin siirto säikeeseen on käännösvirhe, myös silloin, kun se on
toisen tyypin sisällä:

```{.rust tiedosto="esimerkit/11-send.ei-kaanny.rs" osa="send"}
```

```
error[E0277]: `std::rc::Rc<std::sync::Arc<std::vec::Vec<&str>>>`
              cannot be sent between threads safely
```

## Säikeet ja scope

`thread::spawn` käynnistää säikeen ja palauttaa kahvan, jonka `join`
odottaa säikeen loppuun ja palauttaa sen tuloksen. Koska säie voi elää
kutsujaa pidempään, se ei saa lainata kutsujan dataa (`'static`-raja).
`thread::scope` poistaa rajoituksen: kaikki sen sisällä käynnistetyt
säikeet päättyvät ennen kuin `scope` palaa, joten ne voivat lainata
pinossa olevaa dataa:

```{.rust tiedosto="esimerkit/11-scope.rs" osa="scope"}
```

```{.rust tiedosto="esimerkit/11-scope.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-scope.odotettu"}
```

Jokainen säie laskee oman histogramminsa, ja tulokset yhdistetään
lopuksi. Jaettua muuttuvaa tilaa ei ole, joten synkronointia ei
tarvita. `assert_eq!` varmistaa, että rinnakkainen tulos on sama kuin
yhden säikeen tulos.

## Kanavat

`std::sync::mpsc` (*multiple producer, single consumer*) on säikeiden
välinen jono. Viesti siirtää omistuksen lähettäjältä vastaanottajalle,
joten lähettäjä ei voi enää koskea dataan. Vastaanotto päättyy, kun
kaikki lähettäjät on vapautettu:

```{.rust tiedosto="esimerkit/11-kanava.rs" osa="tyojono"}
```

```{.rust tiedosto="esimerkit/11-kanava.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-kanava.odotettu"}
```

Työjonon vastaanottaja on yksi, joten työläiset jakavat sen
`Arc<Mutex<Receiver>>`-rakenteella. Kaksi `drop`-kutsua ovat olennaisia:
jos alkuperäinen `tulos_tx` jäisi eloon, `tulos_rx.iter()` odottaisi
ikuisesti. Useamman kuluttajan kanavat (`crossbeam-channel`) ja
työvarkauteen perustuva rinnakkaisuus (`rayon`) ovat yleisiä
kirjastoja; `rayon`illa histogrammin voisi kirjoittaa muodossa
`data.par_chunks(n).map(...).reduce(...)`.

## Jaettu tila

Kun tila on todella jaettava, se kääritään synkronointityyppiin ja
jaetaan `Arc`-osoittimella. Rustin `Mutex<T>` omistaa suojaamansa datan:
dataan pääsee vain `lock()`-metodin palauttaman vartijan kautta, ja lukko
vapautuu, kun vartija vapautetaan. Lukon ottamista ei siis voi unohtaa.

```{.rust tiedosto="esimerkit/11-jaettu.rs" osa="tilastot"}
```

```{.rust tiedosto="esimerkit/11-jaettu.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-jaettu.odotettu"}
```

- `lock()` palauttaa `Result`-arvon: jos lukon haltija on kaatunut
  paniikkiin, lukko on *myrkytetty* (*poisoned*), koska data voi olla
  puolivalmiissa tilassa.
- Atomiset tyypit (`AtomicUsize`, `AtomicBool` …) noudattavat C++:n
  muistimallia. `Ordering::Relaxed` riittää laskurille, jonka arvoa ei
  käytetä muun datan synkronointiin. Julkaisu ja hankinta tehdään
  `Release`- ja `Acquire`-järjestyksillä, ja `SeqCst` on varmin, mutta
  hitain.
- `RwLock` sallii monta lukijaa tai yhden kirjoittajan. Se kannattaa,
  kun lukuja on paljon ja lukot pidetään pitkään; lyhyissä kriittisissä
  alueissa `Mutex` on yleensä nopeampi.

## async

Asynkroninen ohjelmointi on tarkoitettu tehtäviin, jotka odottavat
enimmäkseen I/O:ta, kuten verkkopalvelimiin, joissa on tuhansia
yhteyksiä. `async fn` käännetään tilakoneeksi, joka toteuttaa
`Future`-piirteen. Future ei tee mitään itsestään: *suorittaja*
(*executor*) kutsuu sen `poll`-metodia, joka palauttaa joko
`Poll::Ready(arvo)` tai `Poll::Pending`. Jälkimmäisessä tapauksessa
future on rekisteröinyt *herättäjän* (*waker*), jota kutsutaan, kun
odotettu tapahtuma on valmis.

Standardikirjastossa on piirteet mutta ei suorittajaa. Alla on
pienin mahdollinen suorittaja, joka näyttää mekanismin:

```{.rust tiedosto="esimerkit/11-async.rs" osa="tulevaisuus"}
```

```{.rust tiedosto="esimerkit/11-async.rs" osa="suorittaja"}
```

```{.rust tiedosto="esimerkit/11-async.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-async.odotettu"}
```

Käytännössä suorittaja on kirjasto, useimmiten Tokio. Se tarjoaa
monisäikeisen suorittajan, ajastimet, asynkronisen I/O:n
(`epoll`, `kqueue`, `io_uring`) ja synkronointityypit. Tokio-ohjelman
`async fn main` merkitään attribuutilla `#[tokio::main]`, ja esimerkiksi
`tokio::join!(a, b)` odottaa kahta futurea yhtä aikaa samassa
tehtävässä, kun taas `tokio::spawn` käynnistää itsenäisen tehtävän.

`Pin` liittyy siihen, että tilakone voi sisältää viitteitä omiin
kenttiinsä. Kiinnitetty future ei saa siirtyä muistissa, ja `pin!`-
makro kiinnittää sen pinoon.

## Käytännössä

- **Viestit ennen jaettua tilaa.** Työn jakaminen kanavilla tai
  tulosten yhdistäminen lopuksi (`scope` + `join`) välttää lukot
  kokonaan. Jaettu tila on oikea ratkaisu välimuisteille ja
  tilastoille.
- **`thread::scope` lainaavaan rinnakkaisuuteen.** Se poistaa
  tarpeen `Arc`-kääreille ja kloonauksille, kun säikeet käsittelevät
  kutsujan dataa.
- **Datan rinnakkaistus `rayon`illa.** `par_iter()` jakaa iteraattorin
  työn säiepoolille. Se on yleensä nopein tapa nopeuttaa laskentaa
  muuttamatta rakennetta.
- **Lyhyt kriittinen alue.** Ota lukko, kopioi tai muuta data ja
  vapauta lukko. Älä kutsu tuntematonta koodia, tee I/O:ta tai odota
  toista lukkoa lukon ollessa auki. Usean lukon ottojärjestys sovitaan
  ja dokumentoidaan, koska lukkiutumia kieli ei estä.
- **`async` I/O:lle, säikeet laskennalle.** Async-tehtävä ei saa
  estää suorittajaa: raskas laskenta tai estävä kutsu siirretään
  `spawn_blocking`-funktiolla erilliseen säikeeseen. Async tuo mukanaan
  kirjastoriippuvuuden ja *värillisten funktioiden* ongelman: async-
  funktiota voi kutsua vain toisesta async-funktiosta tai
  suorittajan kautta.
- **`std::sync::Mutex` myös async-koodissa,** kun lukkoa ei pidetä
  `.await`-kohdan yli. Muuten käytetään suorittajan omaa lukkoa
  (`tokio::sync::Mutex`).
- **Hinta.** Säikeen luonti maksaa kymmeniä mikrosekunteja ja oman pinon;
  lyhyet tehtävät ajetaan poolissa. Kiistelty `Arc` ja atomiset
  operaatiot voivat skaalautua huonosti saman välimuistirivin takia
  (*false sharing*); säiekohtaiset laskurit, jotka yhdistetään lopuksi,
  skaalautuvat paremmin.

## Itsearviointi

- Osaat selittää `Send`- ja `Sync`-piirteet ja tulkita virheen, jossa
  tyyppiä ei voi siirtää säikeeseen.
- Osaat jakaa laskennan säikeille `thread::scope`-funktiolla niin, että
  säikeet lainaavat dataa.
- Osaat toteuttaa tuottaja–kuluttaja-mallin kanavilla ja sulkea kanavat
  oikein.
- Osaat jakaa tilaa `Arc`-, `Mutex`-, `RwLock`- ja atomisilla tyypeillä
  ja valita järjestysehdon laskurille.
- Osaat selittää, miten `async fn`, `Future`, `poll` ja herättäjä
  toimivat ja milloin async on säikeitä parempi valinta.
