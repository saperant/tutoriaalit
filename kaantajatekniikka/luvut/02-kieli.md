# Kieli ja sen merkitys

Kääntäjää ei voi kirjoittaa eikä testata ennen kuin tiedetään, mitä
kieli tarkoittaa. Kielen määrittelyssä on kaksi osaa: **syntaksi**
kertoo, mitkä merkkijonot ovat ohjelmia, ja **semantiikka** eli
merkitys kertoo, mitä ohjelma tekee. Tuotantokielten määrittelyt ovat
satojen sivujen standardeja (C, C++, Java, ECMAScript). Kiden koko
määrittely mahtuu tähän lukuun.

## Kielioppi

Syntaksi kuvataan **yhteydettömällä kieliopilla** (*context-free
grammar*). Kielioppi koostuu säännöistä, joiden vasemmalla puolella on
välikesymboli ja oikealla sen mahdolliset muodot. Tässä käytetään
EBNF-merkintää: `{ x }` tarkoittaa nollaa tai useampaa toistoa,
`[ x ]` valinnaisuutta ja `|` vaihtoehtoa.

```{.text tiedosto="esimerkit/kielioppi.ebnf"}
```

Lausekkeiden säännöt koodaavat **presedenssin** eli sitovuuden:
`tulo` on `summa`n osa, joten kertolasku sitoo tiukemmin kuin
yhteenlasku. Toistorakenne `{ "+" tulo }` tekee laskutoimituksista
**vasemmalle assosiatiivisia**: `a - b - c` on `(a - b) - c`.

Kielioppi ei kerro kaikkea. Se hyväksyy ohjelman `var x = true + 1;`,
vaikka ohjelma on virheellinen, ja ohjelman, joka käyttää esittelemätöntä
muuttujaa. Sellaiset säännöt ovat *staattista semantiikkaa*, ja ne
tarkistaa semanttinen analyysi (luku 7). Jako on tavallinen: kielioppi
pidetään yksinkertaisena, ja kontekstista riippuvat säännöt
tarkistetaan erikseen.

## Tyypit

Kidessä on kaksi tyyppiä:

| Tyyppi | Arvot | Operaatiot |
|--------|-------|------------|
| `int` | 64-bittiset kahden komplementin luvut | `+ - * / %`, vertailut, `-x` |
| `bool` | `true`, `false` | loogiset operaattorit, `==`, `!=` |

Loogiset operaattorit ovat `&&`, `||` ja `!`. Kaksi ensimmäistä
laskevat oikean puolen vain tarvittaessa (*oikosulku*): `a && b`
ei laske `b`:tä, jos `a` on epätosi. Oikosulku on osa merkitystä, koska
`b` voi kutsua funktiota, jolla on sivuvaikutuksia.

Tyyppisäännöt:

- Muuttujan tyyppi on sen alkuarvon tyyppi (`var x = 1;` on `int`).
  Muuttujalle ei voi sijoittaa toisen tyyppistä arvoa.
- `if`- ja `while`-ehdon on oltava `bool`. Kokonaisluku ei kelpaa
  ehdoksi, toisin kuin C:ssä.
- `==` ja `!=` vaativat samantyyppiset operandit; vertailut `<` jne.
  vaativat kokonaisluvut.
- Funktion argumenttien on vastattava parametrien tyyppejä, ja
  `return` palauttaa funktion paluutyyppiä. Jokaisen polun on
  päätyttävä `return`-lauseeseen.
- `print` tulostaa kokonaisluvun ja rivinvaihdon.
- Ohjelmassa on oltava funktio `main() -> int`; sen arvo on prosessin
  paluuarvo.

Näkyvyysalueet noudattavat lohkoja: `{ ... }`, `if`- ja `while`-runko
avaavat uuden alueen. Sisempi alue saa esitellä samannimisen muuttujan,
joka peittää ulomman. Funktiot näkyvät koko ohjelmassa, joten niiden
järjestyksellä ei ole väliä ja keskinäinen rekursio toimii.

## Aritmetiikan merkitys

Kide on C:tä tiukempi yhdessä tärkeässä kohdassa: **jokaisella
operaatiolla on määritelty tulos**. C:ssä etumerkillisen luvun
ylivuoto, nollalla jakaminen ja `INT64_MIN / -1` ovat
*määrittelemätöntä käytöstä* (*undefined behavior*, UB): kääntäjä saa
olettaa, ettei niitä tapahdu, ja ohjelma voi tehdä mitä tahansa.
Määrittelemätön käytös antaa C-kääntäjälle optimointivapautta, mutta
se tekee kääntäjän testaamisesta vaikeaa, koska oikeaa vastausta ei
ole.

Kiden aritmetiikka on määritelty niin, että se vastaa suoraan
RISC-V:n käskyjä. Määrittely on kirjoitettu C++:ksi, ja sitä käyttävät
sekä tulkki (luku 8) että vakioiden laskostus (luku 11):

```{.cpp tiedosto="esimerkit/kide/semantiikka.hpp" osa="aritmetiikka"}
```

Yksi määrittely kahdessa paikassa on tärkeä periaate. Jos laskostus
laskisi `7 / 0` eri tavalla kuin suoritin, optimoitu ja optimoimaton
ohjelma tulostaisivat eri tuloksen. Seuraava ohjelma käy reunatapaukset
läpi:

```{.rust tiedosto="esimerkit/ohjelmat/semantiikka.kide"}
```

```{.tuloste tiedosto="esimerkit/ohjelmat/semantiikka.odotettu"}
```

Testiajuri kääntää ohjelman kuudella eri valintayhdistelmällä ja ajaa
sen myös tulkilla; tulosteen on oltava joka kerta sama. Viimeinen
rivi on erityisen kiinnostava: `100 / nolla` lasketaan `-O0`:lla
ajonaikana `div`-käskyllä, mutta `-O1`:llä laskostus näkee, että
`nolla` on vakio, ja laskee tuloksen käännösaikana.

Yhteenlaskun toteutus etumerkittömänä ei ole kikka vaan välttämättömyys:
C++:n `a + b` etumerkillisille luvuille on määrittelemätöntä
ylivuodossa, ja UBSan pysäyttää kääntäjän, jos sen testit ajetaan
sanitoijien kanssa. Etumerkittömien lukujen aritmetiikka on
määritelty modulo $2^{64}$, ja muunnos takaisin etumerkilliseksi on
C++20:stä lähtien määritelty kahden komplementin mukaan.

## Mitä Kidestä puuttuu

Kidessä ei ole taulukoita, osoittimia, merkkijonoja, tietueita,
globaaleja muuttujia eikä syötettä. Ne eivät tuo uusia vaiheita
kääntäjään vaan lisää samoja asioita: taulukko tarvitsee muistin
varauksen ja osoitelaskentaa (luku 13), tietue tyyppijärjestelmän
laajennuksen (luku 7). Luvussa 17 on ehdotuksia laajennuksiksi.

## Käytännössä

- **Määrittele kieli ennen kääntäjää.** Kirjoitettu kielioppi ja
  tyyppisäännöt ovat kääntäjän testien perusta. Jos määrittelyä ei
  ole, kääntäjän toiminta *on* määrittely, ja jokainen virhe on
  ominaisuus.
- **Vältä määrittelemätöntä käytöstä omassa kielessäsi.** Määritelty
  tulos maksaa joskus suorituskykyä (esimerkiksi ylivuototarkistus),
  mutta se tekee optimoinneista ja testauksesta luotettavia. Rust,
  Java ja Go tekevät saman valinnan.
- **Pidä semantiikka yhdessä paikassa.** Tulkki, laskostus ja
  ajonaikainen kirjasto käyttävät samaa määrittelyä; muuten ne
  ajautuvat erilleen.
- **Kielioppi ei tarkista kaikkea.** Kontekstista riippuvat säännöt
  (nimet, tyypit) kuuluvat semanttiseen analyysiin, ei kielioppiin.

## Itsearviointi

- Osaat lukea EBNF-kielioppia ja selittää, miten sääntöjen kerrostus
  koodaa presedenssin ja assosiatiivisuuden.
- Osaat erottaa syntaksin, staattisen semantiikan ja dynaamisen
  semantiikan ja kertoa, mikä kääntäjän vaihe tarkistaa minkin.
- Osaat selittää, miksi määrittelemätön käytös vaikeuttaa kääntäjän
  testaamista ja miten Kide sen välttää.
- Osaat toteuttaa kiertävän 64-bittisen aritmetiikan C++:lla ilman
  määrittelemätöntä käytöstä.
