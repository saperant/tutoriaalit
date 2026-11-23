# Johdanto {.runko-johdanto}

Verkkosivu koostuu kolmesta kerroksesta. **HTML** kertoo, mitä sisältö
on: otsikko, navigaatio, lomake tai taulukko. **CSS** kertoo, miltä se
näyttää eri laitteilla. **JavaScript** lisää käyttäytymistä. Kerrokset
pidetään erillään, koska jokainen niistä palvelee eri lukijaa: HTML:ää
lukevat selaimen lisäksi ruudunlukijat, hakukoneet, lukutilat ja
käännöstyökalut, CSS:ää vain selain.

Tämä tutoriaali opettaa kaksi ensimmäistä kerrosta niin, että tuloksena
on sivuja, jotka toimivat kaikilla laitteilla ja kaikille käyttäjille.
Esitietoja ei tarvita. JavaScript ja interaktiiviset sovellukset
kuuluvat taitoihin *JavaScript* ja *Web-sovellukset*.

## Historia ja standardit

Tim Berners-Lee julkaisi HTML:n ja ensimmäisen selaimen CERNissä
vuonna 1991. Selainsotien aikana 1990-luvulla valmistajat lisäsivät
kieleen omia ulkoasuelementtejään (`<font>`, `<center>`), ja sivujen
rakenne ja ulkoasu sekoittuivat. CSS (1996) erotti ulkoasun rakenteesta,
ja HTML 4 (1997) siirsi esitysmerkinnät vanhentuneiksi.

| Vuosi | Tapahtuma |
|-------|-----------|
| 1991 | HTML ja WWW julkaistaan |
| 1996 | CSS 1 |
| 1998 | CSS 2; asemointi ja mediatyypit |
| 2000 | XHTML 1.0: HTML XML-syntaksilla |
| 2004 | WHATWG perustetaan jatkamaan HTML:n kehitystä |
| 2014 | HTML5 W3C:n suosituksena |
| 2017 | CSS Grid kaikissa suurissa selaimissa |
| 2019 | HTML on yksi WHATWG:n elävä standardi (*Living Standard*) |
| 2023 | `:has()`, konttikyselyt ja sisäkkäiset säännöt yleistyvät |

HTML:ää ylläpitää nykyään WHATWG ainoana jatkuvasti päivittyvänä
standardina. CSS koostuu W3C:n CSS-työryhmän itsenäisistä moduuleista
(esimerkiksi *CSS Grid Layout Module Level 2*). Versionumeroa "CSS3" ei
virallisesti ole. Työryhmä julkaisee vuosittain koosteen (*CSS
Snapshot*) siitä, mitkä moduulit ovat vakaita.

Käytännössä kysymys ei ole standardin versiosta vaan selaintuesta.
Selainmoottoreita on kolme: Blink (Chrome, Edge, Opera), WebKit (Safari)
ja Gecko (Firefox). *Baseline*-merkintä MDN:ssä ja caniuse.com
kertovat, milloin ominaisuus toimii kaikissa kolmessa. Tämän tutoriaalin
ominaisuudet ovat Baseline-tasoa vuonna 2026.

## Mihin HTML ja CSS sopivat ja mihin eivät

HTML ja CSS ovat oikea valinta kaikkeen, mikä on luettavaa tai
täytettävää sisältöä: julkiset sivustot, dokumentaatio, verkkokaupan
tuotesivut, lomakkeet ja sähköpostit. Moderni CSS hoitaa asettelut,
teemat, animaatiot ja responsiivisuuden ilman JavaScriptiä.

Pelkkä HTML ja CSS eivät riitä, kun sivun tila muuttuu käyttäjän
toimista ilman sivun latausta (sovellusmaiset käyttöliittymät) tai kun
piirretään vapaata grafiikkaa (`<canvas>`, WebGL). Silloinkin pohjana
on semanttinen HTML, jota JavaScript täydentää: tätä kutsutaan
**progressiiviseksi parantamiseksi** (*progressive enhancement*).
Perussisältö ja -toiminnot toimivat kaikilla, ja paremmat selaimet ja
laitteet saavat lisää.

## Työkalut

- **Selaimen kehittäjätyökalut** (F12) näyttävät DOM-puun, kunkin
  elementin lasketut tyylit ja niiden alkuperän, laatikkomallin,
  flex- ja grid-asettelun peittokuvat sekä saavutettavuuspuun.
  Tärkein yksittäinen työkalu.
- **html-validate** tarkistaa HTML:n rakenteen ja osan
  saavutettavuussäännöistä komentoriviltä. W3C:n validaattori
  (<https://validator.w3.org/nu/>) tarkistaa standardin mukaisuuden.
- **Saavutettavuustarkistimet** kuten axe ja Lighthouse löytävät
  automaattisesti noin kolmanneksen saavutettavuusongelmista. Loput
  vaativat käsin testausta: näppäimistöllä ja ruudunlukijalla (NVDA
  Windowsissa, VoiceOver macOS:ssä ja iOS:ssä, TalkBack Androidissa).
- **Editori**: Visual Studio Code tai muu editori, jossa on HTML- ja
  CSS-tuki. Emmet-lyhenteet nopeuttavat HTML:n kirjoittamista.

## Esimerkkien testaus

Jokainen tämän tutoriaalin esimerkki on testattu kahdella tavalla:

1. **html-validate** tarkistaa HTML:n suositelluilla säännöillä ja
   kokonaisen dokumentin säännöillä (otsikkotasot, lomakekenttien
   nimiöt, viittausten kohteet). `.ei-kaanny`-esimerkki on tarkoituksella
   virheellinen: rivi, jolla on merkintä `@virhe`, saa validaattorin
   hylkäämään sen.
2. **Chromium** avaa sivun ilman verkkoyhteyttä ja tulostaa raportin,
   jota verrataan tallennettuun odotettuun tulosteeseen.

Raportti näyttää sen, mitä silmä ei näe. Elementin attribuutti
`data-mitta="nimi"` tulostaa sen laatikon sijainnin ja koon
(`x`, `y`, leveys `l` ja korkeus `k` pikseleinä), `data-tyyli="color"`
ominaisuuden lasketun arvon, ja `<meta name="testi:leveydet">` valitsee
näkymän leveydet. Lopuksi tulostetaan *saavutettavuuspuu*: se, mitä
ruudunlukija ja muut avustavat teknologiat sivusta saavat. Data-
attribuutit ovat vain testausta varten; tuotantokoodissa niitä ei
tarvita.

## Ensimmäinen sivu

Tehtävä: kirjaston aukioloajat. Pienin kunnollinen HTML-dokumentti:

```{.html tiedosto="esimerkit/01-aukiolo.html"}
```

```{.tuloste tiedosto="esimerkit/01-aukiolo.odotettu"}
```

- `<!doctype html>` valitsee standarditilan. Ilman sitä selain
  käyttää vanhojen sivujen *quirks*-tilaa, jossa laatikkomalli toimii
  toisin.
- `lang="fi"` kertoo kielen ruudunlukijan puhesyntetisaattorille,
  tavutukselle, oikoluvulle ja konekääntäjälle.
- `<meta charset="utf-8">` on oltava tiedoston ensimmäisen 1024 tavun
  sisällä; muuten ääkköset voivat näkyä väärin.
- `viewport`-metatieto estää mobiiliselainta esittämästä sivua
  980 pikselin levyisenä ja pienentämästä sitä.
- `<title>` näkyy välilehdessä, kirjanmerkeissä ja hakutuloksissa, ja
  ruudunlukija lukee sen ensimmäisenä. Muoto *sivu – sivusto*: yksilöivä
  osa ensin.
- `<main>`, `<h1>` ja `<ul>` näkyvät saavutettavuuspuussa rooleina
  `main`, `heading` ja `list`. Niiden avulla ruudunlukijan käyttäjä
  hyppää suoraan sisältöön, otsikoihin tai luetteloon.

HTML on armollinen kieli: selain näyttää lähes minkä tahansa merkinnän
jotenkin. Siksi virheet eivät näy selaimessa vaan vasta validaattorissa,
ruudunlukijassa tai toisessa selaimessa. Validaattori kuuluu
työnkulkuun samoin kuin kääntäjän varoitukset muissa kielissä.
