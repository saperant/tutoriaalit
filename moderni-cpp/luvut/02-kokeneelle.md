# C++ kokeneelle {.runko-kokeneelle}

Tämä luku on tarkoitettu lukijalle, joka osaa ohjelmoida jollakin toisella
kielellä, esimerkiksi Javalla, C#:lla, Pythonilla tai C:llä, ja haluaa
oppia C++:n nopeasti. Luku kertoo, missä C++ ajattelee eri tavalla, mikä
siinä on kallista ja mihin kokeneetkin kompastuvat. Yksityiskohdat ovat
myöhemmissä luvuissa.

## Ajattelutapa

**Arvosemantiikka.** C++:n muuttuja *on* olio, ei viittaus olioon.
Sijoitus `a = b` kopioi arvon, ja funktiolle välitetty argumentti on
oletuksena kopio. Viittaukset (`T&`) ja osoittimet (`T*`) ovat
eksplisiittisiä. Javassa ja Pythonissa olioita käsitellään aina
viittausten kautta, joten tämä on suurin yksittäinen ero.

**Elinaika on osa ohjelmaa.** Olio tuhoutuu, kun sen näkyvyysalue päättyy
tai sen omistaja tuhoutuu, ja hajotin suoritetaan juuri silloin.
Roskienkerääjää ei ole. Tähän perustuu *RAII*: resurssi (muisti, tiedosto,
lukko, yhteys) vapautuu automaattisesti ja ennustettavasti. Javan
`try`–`finally` ja Pythonin `with` ovat C++:ssa tarpeettomia, koska jokainen
olio on oma "with-lohkonsa".

**Nollakustannusabstraktiot.** Abstraktion, kuten mallin, `std::vector`in
tai lambdan, ei pitäisi maksaa enempää kuin vastaavan käsin kirjoitetun
koodin. Tämä pitää yleensä paikkansa, mutta vain kun abstraktiota käytetään
oikein: arvoja siirretään eikä kopioida, ja dynaamista sidontaa käytetään
vain kun sitä tarvitaan.

**Määrittelemätön käyttäytyminen.** Kieli ei tarkista taulukon rajoja,
tyhjiä osoittimia eikä kokonaislukujen ylivuotoja. Virheellinen ohjelma ei
välttämättä kaadu, vaan voi toimia väärin mitenkään. Varoitukset ja
sanitoijat ovat siksi osa jokapäiväistä työtä, eivät lisätyökaluja.

## Vastaavuudet

| Käsite | Java / C# | Python | C | C++ |
|----------------|------------------|------------------|----------------|------------------------|
| Olion välitys | viittaus | viittaus | arvo tai osoitin | arvo, `T&`, `const T&` tai osoitin |
| Muistin vapautus | roskienkeruu | viitelaskenta ja roskienkeruu | `free` | hajotin (RAII) |
| Resurssin sulkeminen | `try`–`finally`, `using` | `with` | `goto`-siivous | hajotin |
| Dynaaminen taulukko | `ArrayList`, `List<T>` | `list` | `malloc` + `realloc` | `std::vector<T>` |
| Hakutaulu | `HashMap`, `Dictionary` | `dict` | itse toteutettu | `std::unordered_map` |
| Tyhjä arvo | `null`, `Optional` | `None` | `NULL` | `std::optional<T>` |
| Rajapinta | `interface` | protokolla | funktio-osoittimet | virtuaalifunktiot tai konseptit |
| Geneerisyys | geneeriset tyypit | dynaaminen tyypitys | makrot, `void *` | mallit ja konseptit |
| Virhe arvona | – | – | paluukoodi | `std::expected<T, E>` |

## Hinnat

Monet kielistä tutut mallit maksavat C++:ssa eri tavalla. Seuraavat erot
vaikuttavat suunnittelupäätöksiin.

- **Poikkeukset.** Yleisimmissä toteutuksissa poikkeukset ovat lähes
  ilmaisia, kun mitään ei heitetä, mutta heittäminen ja sieppaaminen ovat
  kalliita: ajonaikainen kirjasto etsii käsittelijää taulukoista ja purkaa
  pinoa. Pythonissa poikkeus on halpa ja idiomaattinen tapa ilmaista
  tavallisiakin poikkeamia (*EAFP: easier to ask forgiveness than
  permission*). C++:ssa poikkeusta ei käytetä normaalin ohjausvuon osana.
  Odotettavat virheet, kuten virheellinen syöte, ilmaistaan arvoina
  (`std::optional`, `std::expected`), ja poikkeukset jätetään aidosti
  poikkeuksellisille tilanteille.
- **Dynaaminen sidonta.** Virtuaalikutsu on epäsuora hyppy, jota kääntäjä ei
  yleensä voi sisällyttää kutsujaan. Mallit ja konseptit ratkaistaan
  käännösaikana, jolloin kutsu voidaan sisällyttää kokonaan. Javassa kaikki
  metodit ovat oletuksena virtuaalisia; C++:ssa ei mikään.
- **Muistinvaraus.** `new` ja säiliöiden kasvaminen varaavat muistia
  keosta, mikä on monin verroin hitaampaa kuin pinon käyttö. Paikalliset
  oliot sijaitsevat pinossa ilman varausta. `reserve` poistaa toistuvat
  uudelleenvaraukset, kun koko tiedetään etukäteen.
- **Kopiot.** Koska välitys on oletuksena arvona, huolimaton koodi kopioi
  suuria olioita. Lukemista varten parametri otetaan `const T&`:nä,
  tallennettava parametri arvona ja siirtäen.
- **`std::function` ja `std::shared_ptr`.** Molemmat ovat joustavia mutta
  maksavat: `std::function` voi varata muistia ja kutsuu epäsuorasti, ja
  `shared_ptr`:n laskuri päivitetään atomisesti jokaisessa kopiossa.

## Sudenkuopat

Seuraavat virheet ovat tavallisia myös kokeneilla kehittäjillä, koska
niistä ei aina seuraa käännösvirhettä eikä edes kaatumista.

**Roikkuva viittaus tai näkymä.** `std::string_view`, `std::span` ja
viittaukset eivät omista dataa. Kun data tuhoutuu, ne jäävät osoittamaan
vapautettuun muistiin:

```{.cpp tiedosto="esimerkit/02-roikkuva.kaatuu.cpp"}
```

AddressSanitizer havaitsee virheen ajon aikana:

```{.tuloste tiedosto="esimerkit/02-roikkuva.virhe"}
```

Clang huomaa yksinkertaisimmat tapaukset jo käännösaikana (varoitus
`-Wdangling`), mutta funktion kautta kulkeva näkymä jää huomaamatta.

**Iteraattorin tai viittauksen mitätöityminen.** Kun `std::vector`
kasvaa, se voi siirtää alkiot uuteen muistiin, ja kaikki viittaukset,
osoittimet ja iteraattorit vanhoihin alkioihin mitätöityvät:

```{.cpp tiedosto="esimerkit/02-mitatoityminen.kaatuu.cpp"}
```

```{.tuloste tiedosto="esimerkit/02-mitatoityminen.virhe"}
```

**Olion viipaloituminen.** Kun johdetun luokan olio kopioidaan
kantaluokan tyyppiseen muuttujaan, kopioituu vain kantaluokan osa, ja
dynaaminen sidonta katoaa:

```{.cpp tiedosto="esimerkit/02-viipaloituminen.cpp" osa="luokat"}
```

```{.cpp tiedosto="esimerkit/02-viipaloituminen.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-viipaloituminen.odotettu"}
```

Monimuotoisia olioita käsitellään viittausten tai osoittimien kautta.
Kantaluokan kopiointi kannattaa usein estää kokonaan (`= delete`).

**Argumenttien laskentajärjestys.** Funktion argumenttien laskentajärjestys
ei ole määrätty. Kutsu `f(seuraava(), seuraava())` voi saada arvot kumpaan
järjestykseen tahansa. Sivuvaikutukselliset kutsut kirjoitetaan omille
riveilleen.

**Implisiittiset muunnokset.** Yksiparametrinen muodostin toimii
oletuksena automaattisena muunnoksena, ja etumerkillisten ja
etumerkittömien lukujen vertailu tuottaa yllätyksiä. Muodostimet merkitään
`explicit`, ja varoitukset pidetään päällä.

## Lukuohje

Kokenut kehittäjä voi edetä näin:

1. Lue tämä luku ja pikaopas (`moderni-cpp-pikaopas.pdf`).
2. Lue luvut [Resurssienhallinta](#resurssienhallinta) ja
   [Siirtosemantiikka](#siirtosemantiikka) huolellisesti. Ne poikkeavat
   eniten muista kielistä.
3. Lue muista luvuista ensin loppuosio *Itsearviointi*. Jos hallitset
   kaikki väitteet, siirry seuraavaan lukuun. Lukujen *Käytännössä*-osiot
   kannattaa lukea joka tapauksessa, koska niissä ovat kielen idiomit ja
   hinnat.
