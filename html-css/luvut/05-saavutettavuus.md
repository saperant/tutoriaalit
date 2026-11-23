# Saavutettavuus

Saavutettava sivu toimii kaikille: ruudunlukijan ja näppäimistön
käyttäjille, heikkonäköisille ja värisokeille, motorisesti rajoittuneille,
kognitiivisista vaikeuksista kärsiville ja kaikille, joilla on
hetkellinen rajoite, kuten kirkas auringonvalo tai toinen käsi
varattuna. Suomessa digitaalisten palvelujen tarjoamisesta annettu
laki edellyttää saavutettavuutta julkiselta sektorilta, ja
esteettömyysdirektiivi laajensi vaatimukset vuonna 2025 myös moniin
yksityisiin palveluihin, kuten verkkokauppoihin ja pankkeihin.

## WCAG

Vaatimukset määrittelee W3C:n **WCAG 2.2** (*Web Content Accessibility
Guidelines*). Sen periaatteet ovat:

| Periaate | Tarkoittaa | Esimerkkejä |
|----------|------------|-------------|
| Havaittava | sisällön voi havaita jollain aistilla | tekstivastine, kontrasti, tekstitys |
| Hallittava | käyttöliittymää voi käyttää | näppäimistö, riittävä aika, ei välkkymistä |
| Ymmärrettävä | sisältö ja toiminta ovat ymmärrettäviä | kieli, ennustettavuus, virheiden ohjeet |
| Toimintavarma | toimii avustavien teknologioiden kanssa | oikeat roolit, nimet ja tilat |

Jokaisella onnistumiskriteerillä on taso A, AA tai AAA. Lait
edellyttävät tasoa AA. Tämän tutoriaalin säännöt kattavat tavallisimmat
AA-kriteerit.

## Rooli, nimi ja tila

Avustava teknologia näkee jokaisesta elementistä kolme asiaa:
*roolin* (painike, linkki, valintaruutu), *nimen* ("Lisää ostoskoriin")
ja *tilan* (valittu, laajennettu, virheellinen). Natiiveilla
elementeillä kaikki kolme tulevat valmiina. Saavutettavuuspuun rivi
`checkbox "Uutiskirje" [checked]` on juuri tämä kolmikko.

**ARIA:n ensimmäinen sääntö**: älä käytä ARIA-attribuuttia, jos natiivi
elementti tekee saman. `role="button"` muuttaa vain roolin, ei
käyttäytymistä:

```{.html tiedosto="esimerkit/05-painike.ei-kaanny.html" osa="painike"}
```

```text
12:12  error  Prefer to use the native <button> element
              prefer-native-element
```

```{.tuloste tiedosto="esimerkit/05-painike.odotettu"}
```

Div-painikkeelta puuttuu Enter- ja välilyöntinäppäimen käsittely,
lomakkeen lähetys, `disabled`-tila ja tyylien nollaus; ne pitäisi
kirjoittaa JavaScriptillä uudelleen. `<button>` tekee kaiken valmiiksi.
ARIA on tarkoitettu tilanteisiin, joihin HTML:ssä ei ole elementtiä,
kuten välilehtiin ja puunäkymiin. Silloin noudatetaan W3C:n *ARIA
Authoring Practices Guide* -ohjeen malleja.

## Saavutettava nimi

Nimi lasketaan tässä järjestyksessä: `aria-labelledby`, `aria-label`,
nimiö tai `alt`, sisällön teksti ja viimeisenä `title`. Ikonipainikkeille
ja epämääräisille linkeille nimi annetaan tarkoituksella:

```{.html tiedosto="esimerkit/05-nimet.html" osa="nimet"}
```

```{.css tiedosto="esimerkit/05-nimet.html" osa="piilotus"}
```

```{.tuloste tiedosto="esimerkit/05-nimet.odotettu"}
```

- Ikonipainikkeen teksti on *visuaalisesti piilotettu*: luokka
  `vain-ruudunlukijalle` kutistaa sen yhden pikselin kokoiseksi ja
  leikkaa näkyvistä, mutta se jää saavutettavuuspuuhun. `display: none`
  ja `visibility: hidden` poistaisivat sen myös puusta.
- Koristeellinen SVG merkitään `aria-hidden="true"`.
- "Lue lisää" -linkki saa piilotetun jatkon, jolloin linkkiluettelossa
  erottuu, mihin tuotteeseen kukin linkki vie.
- `aria-label` korvaa elementin sisällön nimenä. Sitä käytetään
  säästeliäästi, koska se ei näy näkeville käyttäjille eikä käänny
  selaimen konekäännöksessä. Näkyvä teksti on aina parempi.

## Näppäimistö ja fokus

Kaiken on toimittava pelkällä näppäimistöllä: Tab siirtää fokusta,
Enter aktivoi linkin ja painikkeen, välilyönti painikkeen ja
valintaruudun, nuolinäppäimet liikkuvat ryhmän sisällä.

```{.css tiedosto="esimerkit/05-fokus.html" osa="fokus"}
```

```{.tuloste tiedosto="esimerkit/05-fokus.odotettu"}
```

- **Fokus näkyy aina.** `:focus-visible` on voimassa, kun selain
  arvioi korostuksen tarpeelliseksi (näppäimistö, `autofocus`), mutta
  ei hiiren napsautuksessa. `outline: none` ilman korvaavaa tyyliä on
  yksi yleisimmistä saavutettavuusvirheistä.
- **Ohituslinkki** on näkymän ulkopuolella (raportissa `x=-10000`),
  kunnes se saa fokuksen. Se piilotetaan asemoinnilla eikä
  `display: none` -arvolla, jotta se on kohdistettavissa.
- **Tabulointijärjestys seuraa DOM-järjestystä.** `tabindex="0"`
  lisää elementin järjestykseen, `tabindex="-1"` tekee siitä
  ohjelmallisesti kohdistettavan. Positiivisia arvoja ei käytetä,
  koska ne rikkovat luontevan järjestyksen.
- **Visuaalinen ja DOM-järjestys ovat samat.** CSS:n `order` ja grid-
  sijoittelu voivat muuttaa näkyvää järjestystä, mutta fokus kulkee
  silti DOM-järjestyksessä.

## Kontrasti ja väri

Tekstin ja taustan kontrastisuhteen on oltava vähintään 4,5:1 ja
suuren tekstin (vähintään 24 px tai lihavoituna 18,7 px) sekä
käyttöliittymäkomponenttien reunojen 3:1. Suhde lasketaan värien
suhteellisista luminansseista. Esimerkki laskee sen selaimen laskemista
väreistä:

```{.html tiedosto="esimerkit/05-kontrasti.html" osa="laskenta"}
```

```{.tuloste tiedosto="esimerkit/05-kontrasti.odotettu"}
```

Vaaleanharmaa lisätietoteksti ja valkoinen teksti keltaisella ovat
yleisiä virheitä. Kehittäjätyökalujen värivalitsin näyttää suhteen
suoraan. Väri ei koskaan ole ainoa tiedon välittäjä: linkit erottuvat
tekstistä alleviivauksella ja virheet tekstillä.

## Käytännössä

- **Saavutettavuus suunnitellaan, ei korjata.** Kontrastit
  tarkistetaan suunnittelujärjestelmän väreistä, ja komponenttien
  näppäimistökäyttö kuuluu hyväksymiskriteereihin. Jälkikäteen korjaus
  maksaa moninkertaisesti.
- **Testaa itse kolmella tavalla.** Automaattinen tarkistin (axe,
  Lighthouse) jokaisessa muutoksessa, näppäimistötesti jokaiselle
  uudelle komponentille ja ruudunlukijatesti tärkeimmille
  käyttöpoluille.
- **Natiivi elementti, ei ARIA.** Väärä ARIA on huonompi kuin ei
  ARIA:a: WebAIMin vuosittainen tutkimus on toistuvasti havainnut, että
  ARIA:a käyttävillä sivuilla on keskimäärin enemmän virheitä kuin
  sivuilla ilman sitä.
- **Zoomaus ja tekstin suurennus.** Sivun on toimittava 200 %:n
  zoomauksella ja 320 pikselin levyisenä. Mitat `rem`-yksiköissä ja
  joustavat asettelut (luvut 7–10) hoitavat tämän.
- **Liike ja ajastus.** Animaatiot kunnioittavat käyttäjän asetusta
  `prefers-reduced-motion` (luku 10), ja automaattisesti vaihtuvat
  karusellit voi pysäyttää.
- **Saavutettavuusseloste.** Julkisen sektorin sivustolla on seloste,
  joka kertoo tunnetut puutteet ja palautekanavan.

## Itsearviointi

- Osaat kertoa WCAG:n neljä periaatetta ja vaatimustason AA keskeiset
  vaatimukset.
- Osaat selittää, miksi natiivi elementti on parempi kuin ARIA-rooli,
  ja tunnistaa div-painikkeen puutteet.
- Osaat antaa ikonipainikkeelle ja linkille saavutettavan nimen ja
  piilottaa tekstin visuaalisesti oikein.
- Osaat tehdä näkyvän fokustyylin ja ohituslinkin ja tarkistaa
  kontrastisuhteen.
