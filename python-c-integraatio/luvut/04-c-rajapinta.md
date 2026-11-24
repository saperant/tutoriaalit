# C-rajapinta C++-kirjastolle

C++-kirjastoa ei voi kutsua `ctypes`illä suoraan. C++-funktioiden
nimet on koristeltu (*name mangling*) argumenttien tyypeillä,
luokkien asettelu riippuu kääntäjästä, ja poikkeukset, `std::string`
ja `std::vector` ovat olemassa vain C++:n sisällä. C-rajapinta on
yhteinen kieli, jota jokainen kieli ja jokainen kääntäjä ymmärtää.
Siksi monet C++-kirjastot tarjoavat C-rajapinnan, vaikka ne itse on
kirjoitettu C++:lla.

Hyvä C-rajapinta ei ole pelkkä `extern "C"` jokaisen funktion edessä.
Se on suunniteltu niin, että rajan yli kulkee vain C:n tyyppejä, kukaan
ei joudu arvaamaan, kuka omistaa minkäkin muistin, ja virheet ovat
arvoja eivätkä poikkeuksia.

## Läpinäkymätön kahva

Esimerkin kirjasto on liukuva keskiarvo, jolla on tila: rengaspuskuri
ja juokseva summa. C-rajapinta näyttää sen *läpinäkymättömänä
kahvana* (*opaque handle*): kutsuja saa osoittimen tyyppiin
`suodatin`, mutta ei tiedä sen sisältöä eikä kokoa.

```{.c tiedosto="esimerkit/04-c-rajapinta/suodatin.h" osa="rajapinta"}
```

- **Vain C-tyyppejä:** osoittimet, `size_t`, `double` ja `enum`.
  `bool`, `std::string` ja viittaukset eivät kuulu C-rajapintaan.
- **Luo ja tuhoa parina.** Kirjasto varaa olion ja vapauttaa sen.
  `suodatin_tuhoa(NULL)` on sallittu, kuten `free(NULL)`, mikä
  yksinkertaistaa kutsujan siivouskoodia.
- **Virhekoodi paluuarvona, tulos ulostuloparametrissa.** Jokainen
  funktio, joka voi epäonnistua, palauttaa tilan. Virheviestin saa
  koodista erillisellä funktiolla.
- **Rajapintaversio.** `suodatin_api_versio` kertoo, minkä version
  mukaan kirjasto on käännetty. Kutsuja tarkistaa sen ennen käyttöä,
  koska väärä versio kaatuisi oudosti eikä selvällä virheellä.
- **Näkyvyys.** Kirjasto käännetään `-fvisibility=hidden`, joten vain
  `SUODATIN_API`-merkityt funktiot näkyvät kirjaston ulkopuolelle.
  Sisäiset funktiot ja C++-luokan symbolit pysyvät piilossa.

## Toteutus rajan takana

Toteutus on tavallista C++:aa: luokka, `std::vector` ja poikkeus
virheellisestä argumentista. Luokka on nimettömässä nimiavaruudessa,
joten se ei näy kirjaston ulkopuolelle edes symbolina. C-rajapinnan
`struct suodatin` sisältää sen:

```{.cpp tiedosto="esimerkit/04-c-rajapinta/suodatin.cpp" osa="luokka"}
```

Rajafunktiot muuntavat C:n tyypit C++:n tyypeiksi ja poikkeukset
virhekoodeiksi:

```{.cpp tiedosto="esimerkit/04-c-rajapinta/suodatin.cpp" osa="raja"}
```

Poikkeus ei saa ylittää C-rajaa. C-kutsujalla ei ole mitään, mikä
pysäyttäisi sen, ja pinon purkaminen C- tai Python-kehysten läpi on
määrittelemätöntä käytöstä: käytännössä ohjelma kaatuu
`std::terminate`en. Siksi jokainen rajafunktio, joka kutsuu
poikkeuksia nostavaa koodia, päättyy `catch (...)`:hon. `std::span`
antaa C-osoittimelle ja pituudelle C++:n käyttöliittymän ilman
kopiota.

## Python-luokka omistaa kahvan

Python-puolella kahva kääritään luokkaan, joka vastaa sen
vapauttamisesta. Käyttäjä ei näe `ctypes`iä eikä kahvaa:

```{.python tiedosto="esimerkit/04-c-rajapinta/main.py" osa="kaare"}
```

Vapautukselle on kolme polkua, ja kaikki päätyvät samaan
`weakref.finalize`-olioon:

- **`with`-lohko** kutsuu `close`a lohkon lopussa myös poikkeuksen
  sattuessa. Tämä on suositeltava tapa, koska vapautuksen hetki on
  ennustettava.
- **`close()`** suoraan, kun olion elinaika ei mahdu yhteen lohkoon.
- **Roskienkeruu.** Jos käyttäjä unohtaa sulkea olion, `finalize`
  kutsuu `suodatin_tuhoa`a, kun olio kerätään, tai viimeistään tulkin
  sulkeutuessa.

`finalize` kutsuu funktiota vain kerran, joten kahvaa ei vapauteta
kahdesti, vaikka `close` kutsuttaisiin ja olio sen jälkeen kerättäisiin.
Se on `__del__`-metodia turvallisempi: `__del__` voi ajautua tulkin
sulkeutuessa, kun moduulin globaalit muuttujat, kuten `lib`, on jo
tyhjennetty, ja viittaussykli voi viivästää sitä mielivaltaisesti.
`finalize` saa vapautusfunktion ja kahvan argumentteinaan, joten se ei
tarvitse itse oliota eikä pidä sitä elossa.

```{.tuloste tiedosto="esimerkit/04-c-rajapinta/main.odotettu"}
```

Suodatin säilyttää tilansa kutsujen välillä: viides arvo 15 tuottaa
keskiarvon 12 kolmesta viimeisestä. Suljetun suodattimen käyttö ja
virheellinen ikkuna antavat Python-poikkeukset eivätkä kaada tulkkia.

## Milloin C-rajapinta kannattaa

C-rajapinnan kirjoittaminen on enemmän työtä kuin pybind11-sidonta
(luku 5), mutta siitä on kolme hyötyä:

- **Vakaa ABI.** C-rajapinnan binäärimuoto ei muutu kääntäjän tai
  C++-standardikirjaston version mukana. Kirjaston voi päivittää
  kääntämättä kutsujia uudelleen, kunhan rajapinta pysyy samana.
- **Kaikki kielet.** Sama kirjasto toimii Pythonista, Rustista, Gosta,
  C#:sta ja Javasta. Pythonin sidonnat ovat yksi asiakas muiden joukossa.
- **Ei Python-riippuvuutta.** Kirjasto ei tiedä Pythonista mitään,
  joten sitä ei tarvitse kääntää erikseen jokaiselle Python-versiolle.

Kun kirjastoa käytetään vain Pythonista, laajennusmoduuli on yleensä
parempi: luokat, poikkeukset ja tyypit siirtyvät suoraan, eikä
kääreitä kirjoiteta kahteen kertaan.

## Käytännössä

- **Läpinäkymätön kahva, luo- ja tuhoa-pari** on C-kirjastojen
  vakiomalli (`FILE *`, `sqlite3 *`, `EVP_MD_CTX *`). Kahvan sisältöä
  voi muuttaa rikkomatta kutsujia.
- **Ei poikkeuksia rajan yli.** Jokainen `extern "C"` -funktio, joka
  kutsuu C++:aa, nappaa kaikki poikkeukset. `noexcept` rajafunktioissa
  tekee vahingon näkyväksi: vuotava poikkeus kaataa ohjelman heti
  eikä myöhemmin oudossa paikassa.
- **Omistajuus kirjoitetaan otsakkeeseen.** Kuka varaa, kuka vapauttaa,
  ja millä funktiolla. Jokainen osoitinparametri on joko lainattu
  kutsun ajaksi tai siirretty, ja sen on luettava kommentissa.
- **Versio ja näkyvyys.** Versiofunktio havaitsee väärän kirjaston, ja
  piilotetut symbolit estävät kutsujia nojaamasta sisäisiin
  funktioihin.
- **Python-kääre `weakref.finalize`lla ja kontekstinhallinnalla**, ei
  `__del__`illä.
- **Sudenkuoppa:** säikeet. Kahvaa käyttävät kutsut eivät ole
  säieturvallisia, ellei kirjasto sitä lupaa. Python-kääre voi
  suojata kahvan `threading.Lock`illa, koska `ctypes` vapauttaa
  tulkkilukon C-kutsun ajaksi.

## Itsearviointi

- Osaat suunnitella C-rajapinnan C++-luokalle läpinäkymättömällä
  kahvalla, virhekoodeilla ja rajapintaversiolla.
- Osaat estää C++-poikkeuksia ylittämästä C-rajaa ja perustella, miksi
  se on välttämätöntä.
- Osaat kääriä kahvan Python-luokkaan, joka vapauttaa sen varmasti
  kerran `weakref.finalize`lla ja `with`-lohkolla.
- Osaat arvioida, milloin C-rajapinta on parempi kuin laajennusmoduuli.
