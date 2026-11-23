# Älykkäät osoittimet ja elinajat {.runko-muisti}

Luvun 5 säännöt riittävät, kun jokaisella arvolla on yksi selvä
omistaja ja lainaukset ovat lyhytikäisiä. Tässä luvussa käsitellään
rekursiiviset rakenteet, jaettu omistus, sisäinen muuttuvuus ja
rakenteet, jotka lainaavat dataa.

| Tyyppi | Omistus | Hinta | C++ |
|-------------|-----------------------|----------------|------------------|
| `Box<T>` | yksi omistaja, data keossa | yksi varaus | `unique_ptr<T>` |
| `Rc<T>` | jaettu, yksi säie | varaus, laskuri | `shared_ptr<T>` ilman atomisuutta |
| `Arc<T>` | jaettu, säikeiden välillä | varaus, atominen laskuri | `shared_ptr<T>` |
| `Weak<T>` | ei omista | laskuri, `upgrade` tarkistaa | `weak_ptr<T>` |
| `Cell<T>` | muokkaus jaetun viitteen läpi, `Copy`-arvot | ei mitään | `mutable` |
| `RefCell<T>` | muokkaus jaetun viitteen läpi | ajonaikainen lainalaskuri | – |
| `Mutex<T>`, `RwLock<T>` | kuten `RefCell`, säikeiden välillä | lukko (luku 11) | `std::mutex` + data |

## Box: rekursiiviset tyypit

Rakenteen koon on oltava tiedossa käännösaikana, joten `enum` ei voi
sisältää itseään suoraan. `Box<T>` on osoittimen kokoinen omistava
osoitin kekoon, ja sen avulla voi tehdä puita:

```{.rust tiedosto="esimerkit/09-lauseke.rs" osa="puu"}
```

Laatikon sisällön voi siirtää ulos dereferoimalla (`*a`), kun laatikko
on omistuksessa. Sievennys kuluttaa vanhan puun ja rakentaa uuden
siirtämällä alipuita, joten mitään ei kopioida. Hahmot voivat yhdistää
vaihtoehtoja (`|`), jos jokainen vaihtoehto sitoo samat muuttujat:

```{.rust tiedosto="esimerkit/09-lauseke.rs" osa="sievennys"}
```

```{.rust tiedosto="esimerkit/09-lauseke.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-lauseke.odotettu"}
```

`Lauseke` vie 24 tavua. Suurin muunnelma on `Muuttuja(String)`, ja
kääntäjä tallentaa tunnisteen `String`-kentän käyttämättömiin
bittikuvioihin (*niche*), joten tunniste ei vie lisätilaa. Summa- ja
tulosolmut ovat kahden osoittimen kokoisia.

## Rc, Weak ja RefCell: jaettu omistus

`Rc<T>` (*reference counted*) sallii useita omistajia. `Rc::clone`
kasvattaa laskuria eikä kopioi dataa, ja data vapautuu, kun viimeinen
`Rc` poistuu. `Rc` antaa vain jaetun viitteen sisältöön. Jos dataa on
muutettava, se kääritään `RefCell`-tyyppiin, joka siirtää
lainaussääntöjen tarkistuksen ajonaikaiseksi: `borrow()` ja
`borrow_mut()` palauttavat vartijan, joka pitää kirjaa lainoista.

Puu, jossa lapsi tuntee vanhempansa, on tyypillinen esimerkki.
Vanhempi omistaa lapsensa, ja lapsi viittaa vanhempaansa `Weak`-
viitteellä. Jos lapsikin omistaisi vanhempansa, syntyisi sykli, jonka
laskurit eivät koskaan laskisi nollaan:

```{.rust tiedosto="esimerkit/09-jaettu.rs" osa="hakemisto"}
```

```{.rust tiedosto="esimerkit/09-jaettu.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-jaettu.odotettu"}
```

`Weak::upgrade` palauttaa `Option<Rc<T>>`: `None`, jos kohde on jo
vapautettu. Roikkuvaa viitettä ei siis synny.

`RefCell` ei poista lainaussääntöjä vaan siirtää niiden rikkomisen
ajonaikaiseksi paniikiksi. Tavallinen virhe on muuttaa kokoelmaa sitä
läpikäytäessä, esimerkiksi tarkkailija, joka poistaa itsensä
ilmoituksen aikana:

```{.rust tiedosto="esimerkit/09-refcell.kaatuu.rs" osa="kaksoislaina"}
```

```{.tuloste tiedosto="esimerkit/09-refcell.virhe"}
```

Korjaus on kerätä muutokset ja tehdä ne läpikäynnin jälkeen, tai
kopioida lista ennen ilmoitusta. `try_borrow_mut` palauttaa `Result`-
arvon paniikin sijaan.

## Elinajat

Jokaisella viitteellä on *elinaika*: koodin alue, jolla viite on
kelvollinen. Kääntäjä päättelee elinajat funktioiden sisällä.
Allekirjoituksissa ne joko päätellään säännöillä (*elision*) tai
kirjoitetaan näkyviin elinaikaparametreina `'a`.

Päättelysäännöt ovat yksinkertaiset: jos funktio saa yhden viitteen,
paluuarvon viite lainaa sitä. Jos metodi saa `&self`-parametrin,
paluuarvo lainaa `self`-arvoa. Muuten elinaika on kirjoitettava:

```{.rust tiedosto="esimerkit/09-elinajat.rs" osa="pidempi"}
```

Merkintä ei muuta elinaikoja. Se kertoo kääntäjälle ja lukijalle, että
paluuarvo on kelvollinen niin kauan kuin molemmat parametrit ovat.

Rakenne, joka sisältää viitteitä, tarvitsee elinaikaparametrin. Sen
avulla voi kirjoittaa *nollakopioisen* jäsentimen, joka ei varaa
muistia lainkaan vaan palauttaa näkymiä syötteeseen:

```{.rust tiedosto="esimerkit/09-elinajat.rs" osa="viipalejasennin"}
```

Metodi `otsake` palauttaa `&'a str` eikä `&str`. Ilman merkintää
päättelysääntö sitoisi paluuarvon `&self`-lainaan, eikä otsakkeen arvoa
voisi käyttää `Pyynto`-arvon vapauttamisen jälkeen, vaikka data on
syötteessä:

```{.rust tiedosto="esimerkit/09-elinajat.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-elinajat.odotettu"}
```

Erityinen elinaika `'static` tarkoittaa koko ohjelman ajan kelvollista
dataa, kuten merkkijonoliteraaleja. Piirrerajana `T: 'static`
tarkoittaa, ettei tyyppi sisällä lyhytikäisiä viitteitä. Siksi
`thread::spawn` vaatii sen (luku 11).

## Käytännössä

- **Omistuspuu ensin.** Suunnittele data niin, että sillä on selvä
  omistuspuu. `Rc<RefCell<T>>` on oikea ratkaisu aidosti jaetulle,
  muuttuvalle tilalle, mutta se tuo ajonaikaiset tarkistukset ja
  paniikkimahdollisuuden takaisin. Ensimmäinen ratkaisu kannattaa
  yleensä etsiä muualta.
- **Areena ja indeksit graafeille.** Graafit ja sykliset rakenteet
  tallennetaan usein `Vec`-tyyppiin, ja solmut viittaavat toisiinsa
  indekseillä (`usize` tai newtype `SolmuId`). Malli on nopea ja
  välimuistiystävällinen, eikä siinä ole viitelaskentaa. Hinta on, että
  poistettuun solmuun osoittava indeksi on looginen virhe, jota kääntäjä
  ei havaitse (`slotmap`-kirjasto lisää sukupolvilaskurin).
- **`Weak` takaisinviittauksiin.** Vanhempi–lapsi-, tarkkailija- ja
  välimuistirakenteissa omistus kulkee yhteen suuntaan, ja paluusuunta
  on `Weak`.
- **Lyhyet `RefCell`-lainat.** Älä pidä `borrow_mut()`-vartijaa yli
  funktiokutsun, joka voi palata samaan olioon. Kopioi tarvittava arvo
  ulos ja vapauta laina.
- **Lainaavat rakenteet lyhytikäisiksi.** Elinaikaparametrilliset
  rakenteet sopivat jäsentimiin, iteraattoreihin ja näkymiin.
  Pitkäikäinen tila omistaa datansa. Jos rakenne tarvitsee sekä datan
  että siihen osoittavat viitteet (*itseensä viittaava rakenne*), tallenna
  indeksejä viitteiden sijaan.
- **Hinta.** `Box`-varaus maksaa kuten `malloc`. `Rc::clone` on halpa,
  `Arc::clone` atominen operaatio, joka voi kilpailla välimuistirivistä
  säikeiden kesken. `Box<[T]>` ja `Rc<str>` säästävät kapasiteettikentän,
  kun dataa ei enää muuteta.

## Itsearviointi

- Osaat tehdä rekursiivisen tietorakenteen `Box`-tyypillä ja muokata
  sitä siirtämällä alipuita.
- Osaat valita `Box`-, `Rc`-, `Arc`-, `Cell`- ja `RefCell`-tyypin
  välillä ja kertoa niiden hinnan.
- Osaat katkaista viitesyklin `Weak`-viitteellä ja selittää, miksi sykli
  vuotaa muistia.
- Osaat kirjoittaa elinaikamerkinnät funktioon ja viitteitä sisältävään
  rakenteeseen ja selittää päättelysäännöt.
- Osaat mallintaa graafin indekseillä ilman jaettua omistusta.
