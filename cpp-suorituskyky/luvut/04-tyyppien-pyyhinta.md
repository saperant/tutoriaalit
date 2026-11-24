# Funktiot arvoina ja tyyppien pyyhintä

C++:ssa funktion voi antaa toiselle funktiolle kolmella tavalla:
malliparametrina, funktio-osoittimena tai tyypit pyyhkivänä
kääreenä, kuten `std::function`. Ne näyttävät kutsupaikalla samoilta,
mutta kääntäjälle ne ovat hyvin erilaisia. *Tyyppien pyyhintä* (engl.
type erasure) yleisemmin, eli eri tyyppien piilottaminen yhteisen
rajapinnan taakse, maksaa epäsuoran kutsun ja usein muistinvarauksen.

## Kolme tapaa välittää ehto

Sama laskenta kolmella tavalla:

```{.cpp tiedosto="esimerkit/04-funktiot.cpp" osa="tavat"}
```

**Malliparametri** tuottaa jokaiselle ehdon tyypille oman version
funktiosta. Jokaisella lambdalla on oma nimetön tyyppinsä, joten
kääntäjä tietää kutsun kohteen ja sisällyttää sen. Silmukasta tulee
yksi vertailu ja yhteenlasku, ja Clang vektoroi sen.

**Funktio-osoitin** on yksi tyyppi kaikille saman allekirjoituksen
funktioille. Funktiosta käännetään yksi versio, joka kutsuu
osoitinta epäsuorasti. Jos kääntäjä näkee kutsukohdassa vakio-osoittimen,
se voi kloonata funktion ja sisällyttää kohteen, mutta siihen ei voi
luottaa.

**`std::function`** hyväksyy minkä tahansa kutsuttavan: funktion,
lambdan sieppauksineen tai funktio-olion. Se tallentaa kutsuttavan
sisäiseen puskuriin tai kekoon ja kutsuu sitä funktio-osoittimen
kautta. Lisäksi tyhjä `std::function` heittää kutsuttaessa
poikkeuksen `std::bad_function_call`, joten jokainen kutsu tarkistaa
tyhjyyden.

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-funktiot.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/04-funktiot.txt"}
```

Malliparametri on yli kaksi kertaa nopeampi kuin kumpikaan epäsuora
tapa. Ero kasvaa, mitä vähemmän työtä ehto tekee: kalliin ehdon
rinnalla kutsun hinta häviää.

## Pienen olion puskuri

`std::function` on kiinteän kokoinen olio (libstdc++:ssa 32 tavua),
mutta siihen voi tallentaa minkä kokoisen lambdan tahansa. Pieni
kutsuttava mahtuu olion sisäiseen puskuriin (engl. small buffer
optimization, SBO), suuri varataan keosta. Varauslaskuri näyttää
rajan:

```{.cpp tiedosto="esimerkit/04-pyyhinta.cpp" osa="apu"}
```

```{.cpp tiedosto="esimerkit/04-pyyhinta.cpp" osa="function"}
```

```{.cpp tiedosto="esimerkit/04-pyyhinta.cpp" osa="kopio"}
```

```{.cpp tiedosto="esimerkit/04-pyyhinta.cpp" osa="muut"}
```

```{.tuloste tiedosto="esimerkit/04-pyyhinta.odotettu"}
```

libstdc++:n `std::function` tallentaa sisäisesti kutsuttavan, joka on
enintään 16 tavua ja jonka voi kopioida tavu tavulta. Neljän
liukuluvun taulukko (32 tavua) ei mahdu, joten jokainen rakentaminen
ja jokainen *kopio* varaa muistia. Siirto vain siirtää osoittimen.
Viittauksen sieppaava lambda on 8 tavua ja mahtuu, mutta silloin
kutsujan on pidettävä taulukko elossa.

`std::any` tallentaa sisäisesti vain osoittimen kokoisen arvon, joka
siirtyy poikkeuksetta. Jo 16 tavun taulukko ja lyhyt `std::string`
varataan keosta. Puskurien koot ovat toteutuksen valintoja: libc++ ja
MSVC:n kirjasto käyttävät eri rajoja.

## Vaihtoehdot

| Tarve | Valinta | Hinta |
|-----------------------|---------------------------|-------------------------------|
| Kutsuttava, jota ei tallenneta | malliparametri tai `auto`-parametri | ei mitään, koodi monistuu |
| Tallennettava, kopioitava | `std::function` | epäsuora kutsu, varaus isolle |
| Tallennettava, vain siirrettävä | `std::move_only_function` (C++23) | epäsuora kutsu, ei tyhjyystarkistusta |
| Tilapäinen viittaus kutsuttavaan | `std::function_ref` (C++26) | epäsuora kutsu, ei varausta |
| Kiinteä joukko funktioita | `enum` ja `switch` tai `std::variant` | ajonaikainen valinta ilman kutsua |

`std::move_only_function` hyväksyy myös vain siirrettävät kutsuttavat,
kuten `std::unique_ptr`in sieppaavan lambdan, eikä tarkista tyhjyyttä
(tyhjän kutsuminen on määrittelemätöntä). `std::function_ref` ei
omista kutsuttavaa: se on kaksi osoitinta, eikä se koskaan varaa
muistia. Ennen C++26:ta saman saa omalla parin rivin luokalla tai
kirjastoista, kuten LLVM:n `function_ref`.

Mallien hinta on koodin monistuminen: jokainen eri lambda tuottaa oman
version funktiosta. Kymmenen kutsupaikkaa kymmenellä lambdalla on
kymmenen kopiota konekoodia, mikä kasvattaa binääriä ja
käskyvälimuistin kuormaa. Siksi kirjastojen julkisissa rajapinnoissa,
joiden takana on paljon koodia, tyyppien pyyhintä on usein parempi.

## Käytännössä

- **Ota kutsuttava malliparametrina**, kun funktio kutsuu sitä heti
  eikä tallenna sitä: algoritmit, vierailijat ja apufunktiot.
  `std::sort` ja `std::ranges`-algoritmit tekevät näin.
- **Tallenna `std::function`illa tai `std::move_only_function`illa**
  takaisinkutsut ja tapahtumankäsittelijät, joita kutsutaan harvoin
  suhteessa niiden tekemään työhön.
- **Pidä sieppaukset pieninä**: sieppaa viittaus tai osoitin suureen
  olioon, kun elinaika on varmasti riittävä, tai `std::shared_ptr`, kun
  ei ole.
- **Siirrä, älä kopioi** suuria `std::function`-olioita: kopio varaa
  ja kopioi koko sieppauksen.
- **Ole tarkka `std::any`n kanssa**: lähes kaikki muu kuin skalaari
  varataan keosta, ja arvon lukeminen tarkistaa tyypin ajon aikana.

## Itsearviointi

- Osaat selittää, miksi malliparametrina annettu lambda sisällytetään
  mutta `std::function` ei.
- Osaat mitata, milloin `std::function` ja `std::any` varaavat
  muistia, ja selittää pienen olion puskurin.
- Osaat valita malliparametrin, `std::function`in,
  `std::move_only_function`in ja `std::function_ref`in välillä.
- Osaat arvioida mallien aiheuttaman koodin monistumisen hinnan.
