# Lopuksi {.runko-lahteet}

Sama sovellus viidesti on enemmän toistoa kuin yksikään oikea projekti
tarvitsee, ja juuri toisto on tämän tutoriaalin sisältö. Kun näkymä,
komponentti, tila ja efekti on nähty neljällä syntaksilla, syntaksi
lakkaa olemasta se, mitä kehyksestä opetellaan.

## Nyrkkisäännöt

- **Näkymä on tilan funktio.** Älä muokkaa DOM:ia ohi kehyksen äläkä
  lue tilaa DOM:sta.
- **Yksi totuus.** Jokaisella tiedolla on yksi omistaja. Kaikki muu
  johdetaan siitä.
- **Tieto alas, tapahtumat ylös.** Kaksisuuntainen sidos on lyhennys
  tälle, ei poikkeus siitä.
- **Kysy uudesta kehyksestä kaksi asiaa:** mistä se tietää, mikä
  muuttui, ja ajetaanko komponentin koodi kerran vai joka päivityksellä.
  Loput seuraavat näistä.
- **Listan riveillä on avain**, ja avain on tiedon tunniste.
- **Efekti on synkronointia ulkomaailmaan**, ei tapa laskea arvoja.
- **Säännöt eivät kuulu komponenttiin.** Se, mikä ei tuo kehystä, ei
  vanhene kehyksen mukana.
- **Testaa käyttäjän silmin.** Testi, joka ei tunne kehystä, kestää
  kehyksen vaihdon ja sen suuret päivitykset.
- **Valitse tylsästi ja päivitä usein.**

## Mitä tässä ei käsitelty

Tutoriaali rajautui kehysten ytimeen. Oikeassa sovelluksessa tarvitaan
lisäksi ainakin reititin, palvelindatan välimuisti, lomakekirjasto,
komponenttikirjasto, kansainvälistys ja usein metakehys. Ne ovat
kehyskohtaisia, ja niiden rajapinnat muuttuvat ydintä nopeammin, joten
ne opetellaan kehyksen omasta dokumentaatiosta silloin kun projekti on
valittu. Myöskään suorituskyvyn mittaamista suurilla näkymillä,
animaatioita ja mobiilisovelluksia (React Native ja vastaavat) ei
käsitelty.

Tämän sarjan muista taidoista aihetta jatkavat *Web-sovellukset*
(React-sovelluksen rakentaminen alusta loppuun, verkko ja testaus),
*Web-sovellusten tietoturva*, *Testivetoinen kehitys ja
testisuunnittelu* sekä *Tietoturva kehitystyössä* (riippuvuuksien
hallinta). Kielen puolelta pohjana on *TypeScript*.

## Mihin seuraavaksi

Paras jatko on tehdä itse sama, mitä tässä tehtiin valmiiksi:

1. Lisää sovellukseen ominaisuus, esimerkiksi tehtävän nimen muokkaus
   paikallaan, ensin testiin ja sitten kaikkiin viiteen toteutukseen.
   Huomaat, missä kehyksessä se on helpointa ja miksi.
2. Toteuta sama sovellus kuudennella kehyksellä, esimerkiksi Solidilla
   tai Litillä. Lisää se testisarjan projekteihin ja katso, mikä
   testeistä epäonnistuu ensimmäisenä.
3. Käy läpi valitsemasi kehyksen virallinen opas alusta loppuun. Tämän
   tutoriaalin jälkeen se on nopeaa, koska käsitteet ovat tuttuja ja
   vain nimet ovat uusia.

## Lähteet

Kehysten omat dokumentaatiot ovat ensisijainen lähde kaikelle, mikä
riippuu versiosta. Ne ovat ajan tasalla ja hyvin kirjoitettuja:

| Kehys tai työkalu | Dokumentaatio | Lisenssi |
|-------------------|---------------|----------|
| React | <https://react.dev> | MIT |
| Vue | <https://vuejs.org> | MIT |
| Angular | <https://angular.dev> | MIT |
| Svelte | <https://svelte.dev> | MIT |
| Vite | <https://vite.dev> | MIT |
| Playwright | <https://playwright.dev> | Apache-2.0 |
| TypeScript | <https://www.typescriptlang.org> | Apache-2.0 |
| selaimen rajapinnat | <https://developer.mozilla.org> (MDN) | – |

Periaatteiden taustaa:

- **Pete Hunt: *React: Rethinking Best Practices*.** JSConf EU 2013.
  Esitys, jossa perusteltiin, miksi mallipohjan ja logiikan erottaminen
  eri tiedostoihin ei ole vastuiden erottamista (luku 4).
- **Rich Harris: *Rethinking Reactivity*.** You Gotta Love Frontend,
  vuosi 2019. Svelten perustelu kääntäjälle ja virtuaalisen DOM:n
  kritiikki (luku 3).
- **Reactin dokumentaatio, luvut *Thinking in React* ja *You Might Not
  Need an Effect*.** Yksisuuntainen tietovirta, johdettu tila ja
  efektien oikea käyttö; pätevät sellaisinaan muihinkin kehyksiin.
- **Vuen dokumentaatio, luvut *Reactivity in Depth* ja *Rendering
  Mechanism*.** Selkeä kuvaus signaalipohjaisesta reaktiivisuudesta
  ja käännetyistä mallipohjista sekä vertailu muihin kehyksiin.
- **Angularin dokumentaatio, signaaleja ja muutostentunnistusta
  käsittelevät oppaat.** Siirtymä `zone.js`-kirjastosta signaaleihin kehyksen
  omin sanoin.
- **TC39: *Signals*-ehdotus.** Kehysten tekijöiden yhteinen ehdotus
  signaalien tuomisesta JavaScript-kieleen; kertoo, kuinka
  yhteneväisiksi mallit ovat tulleet. Ehdotus on varhaisessa vaiheessa.
- **Stack Overflow Developer Survey ja State of JS.** Vuosittaiset
  kyselyt kehysten yleisyydestä; hyödyllisiä suuntien, eivät
  paremmuuden, arviointiin.

Esimerkkikoodi on tämän tutoriaalin omaa ja samalla lisenssillä kuin
teksti. Käytettyjen kirjastojen lisenssit ovat yllä olevassa taulukossa;
lukitustiedosto `esimerkit/package-lock.json` kertoo tarkat versiot.
