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

```{.dot otsikko="Esimerkin viimeinen lauseke ennen sievennystä ja sen jälkeen. Jokainen kaari on `Box`. Sievennys siirtää alipuun `x` uuteen puuhun ja vapauttaa solmut, joita ei enää tarvita."}
digraph {
  rankdir=TB; nodesep=0.25; ranksep=0.35;
  subgraph cluster_ennen { label="ennen: (x + 0) * (1.5 + 2)"; style=rounded; color="#9AA3AF";
    t1 [label="Tulo"]; s1 [label="Summa"]; s2 [label="Summa"];
    x1 [label="x"]; n0 [label="0"]; n1 [label="1.5"]; n2 [label="2"];
    t1 -> s1; t1 -> s2; s1 -> x1; s1 -> n0; s2 -> n1; s2 -> n2;
  }
  subgraph cluster_jalkeen { label="jälkeen: x * 3.5"; style=rounded; color="#9AA3AF";
    t2 [label="Tulo"]; x2 [label="x"]; n3 [label="3.5"];
    t2 -> x2; t2 -> n3;
  }
}
```

`Lauseke` vie 24 tavua. Suurin muunnelma on `Muuttuja(String)`, ja
kääntäjä tallentaa tunnisteen `String`-kentän käyttämättömiin
bittikuvioihin (*niche*), joten tunniste ei vie lisätilaa. Summa- ja
tulosolmut ovat kahden osoittimen kokoisia.

### Deref-pakotus

`Box<T>`, `Rc<T>`, `String` ja `Vec<T>` toteuttavat `Deref`-piirteen,
joka kertoo, mihin tyyppiin osoitin viittaa. Kun viitteen tyyppi ei
täsmää parametriin, kääntäjä kokeilee `Deref`-muunnoksia peräkkäin
(*deref coercion*). Tästä syystä luvun 5 ohje "ota `&str`, älä
`&String`" toimii: `&String` muuntuu itsestään `&str`-viitteeksi ja
`&Vec<T>` viipaleeksi `&[T]`. Sama ketju käydään läpi metodikutsussa,
joten älykkään osoittimen läpi voi kutsua sisällön metodeja suoraan.

```{.rust tiedosto="esimerkit/09-deref.rs" osa="deref"}
```

```{.tuloste tiedosto="esimerkit/09-deref.odotettu"}
```

Muunnos on käännösaikainen eikä maksa mitään. Se toimii vain viitteille
ja vain `Deref`-ketjun suuntaan; lukutyyppien välillä vastaavaa
automaattista muunnosta ei ole.

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

```{.dot otsikko="Hakemistopuun omistus kahden `lisaa`-kutsun jälkeen. Yhtenäinen nuoli on vahva viite (`Rc`), katkoviiva heikko (`Weak`). Solmussa ovat laskurit: `koti`-hakemistolla on kaksi omistajaa (muuttuja ja juuren lapsivektori) ja yksi heikko viite lapseltaan. Jos katkoviivat olisivat vahvoja, vanhempi ja lapsi pitäisivät toisensa elossa ikuisesti."}
digraph {
  rankdir=TB; nodesep=0.9; ranksep=0.4;
  vj [label="muuttuja juuri", shape=plaintext, style=""];
  vk [label="muuttuja koti", shape=plaintext, style=""];
  va [label="muuttuja ada", shape=plaintext, style=""];
  j [label="\"\" (juuri)\nvahvat 1, heikot 1"];
  k [label="\"home\"\nvahvat 2, heikot 1"];
  a [label="\"ada\"\nvahvat 2, heikot 0"];
  vj -> j; vk -> k; va -> a;
  { rank=same; j; k; a; }
  j -> k [label="lapset"]; k -> a [label="lapset"];
  k -> j [style=dashed, label="vanhempi", constraint=false];
  a -> k [style=dashed, label="vanhempi", constraint=false];
}
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
- Osaat selittää, miksi `&String` kelpaa `&str`-parametrille ja miksi
  `Rc<T>`:n läpi voi kutsua `T`:n metodeja.
- Osaat katkaista viitesyklin `Weak`-viitteellä ja selittää, miksi sykli
  vuotaa muistia.
- Osaat kirjoittaa elinaikamerkinnät funktioon ja viitteitä sisältävään
  rakenteeseen ja selittää päättelysäännöt.
- Osaat mallintaa graafin indekseillä ilman jaettua omistusta.
