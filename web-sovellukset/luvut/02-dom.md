# DOM ja tapahtumat

Selain jäsentää HTML:n oliopuuksi, **DOM**:ksi (*Document Object
Model*). Kaikki selainsovellukset, myös kehyksillä tehdyt, muuttavat
lopulta tätä puuta. Siksi DOM:n perusteet kannattaa osata ennen
kehystä: kehyksen virheet ja hinnat ymmärtää vasta, kun tietää, mitä se
tekee pinnan alla.

## Elementtien luominen

Elementin voi luoda kahdella tavalla: merkkijonona `innerHTML`-
ominaisuuteen tai olioina `createElement`-kutsuilla. Kun sisältö tulee
käyttäjältä tai palvelimelta, vain jälkimmäinen on turvallinen.
`textContent` asettaa tekstin, ja selain näyttää sen merkkeinä, vaikka
siinä olisi HTML:ää.

```{.typescript tiedosto="esimerkit/src/02-dom/luettelo.ts" osa="piirra"}
```

`replaceChildren` korvaa juuren sisällön yhdellä operaatiolla. Lista
rakennetaan ensin irrallaan ja liitetään dokumenttiin kerralla, joten
selain laskee asettelun vain kerran. `data-*`-attribuutit
(`dataset.tila`) ovat oikea paikka kytkeä elementti sovelluksen dataan:
ne eivät vaikuta ulkoasuun eivätkä saavutettavuuspuuhun.

## Tapahtumat ja delegointi

Tapahtuma kulkee kohde-elementistä ylöspäin dokumentin juureen
(*kupliminen*, *bubbling*). Siksi yksi kuuntelija yhteisessä
esivanhemmassa riittää kaikille napeille. Tämä on **tapahtumien
delegointi**:

```{.typescript tiedosto="esimerkit/src/02-dom/luettelo.ts" osa="delegointi"}
```

Delegoinnilla on kolme etua. Kuuntelijoita on yksi eikä sata, joten
muistia kuluu vähemmän. Myöhemmin luodut napit toimivat ilman uutta
rekisteröintiä. Kun luettelo piirretään uudelleen, vanhoja kuuntelijoita
ei tarvitse poistaa. `closest` hakee lähimmän ehdon täyttävän
esivanhemman, joten napin sisällä oleva kuvake tai teksti kelpaa
kohteeksi. Funktio palauttaa kuuntelijan poistavan funktion, mikä on
yleinen malli: resurssin varaaja palauttaa sen vapauttajan.

Testi luo DOM:n happy-domilla, joka toteuttaa selaimen rajapinnat
Nodessa. Se varmistaa sekä delegoinnin että sen, että nimessä oleva
HTML näkyy tekstinä:

```{.typescript tiedosto="esimerkit/src/02-dom/luettelo.test.ts" osa="testi"}
```

## Lomakkeet

Lomake on syötteen luonteva yksikkö: selain hoitaa Enter-näppäimen,
pakolliset kentät, numerorajat ja saavutettavat virheilmoitukset.
Sovellus kuuntelee `submit`-tapahtumaa, ei napin klikkausta, ja estää
sivun latauksen `preventDefault`-kutsulla. Arvot luetaan `FormData`-
oliosta kenttien nimillä:

```{.typescript tiedosto="esimerkit/src/02-dom/lomake.ts" osa="lomake"}
```

`FormData` palauttaa merkkijonon, tiedoston tai `null`-arvon, joten
tyypit muunnetaan ja tarkistetaan lukiessa. Testi luo lomakkeen,
lähettää `submit`-tapahtuman ja tarkistaa, että sivun lataus estettiin
(`defaultPrevented`).

## Käytännössä

- **`textContent`, ei `innerHTML`.** `innerHTML` epäluotettavalla
  datalla on yleisin selaimen tietoturva-aukko (XSS, luku 10). Jos
  merkintää tarvitaan, rakennetaan elementit tai käytetään
  `<template>`-elementtiä.
- **Delegointi listoihin ja taulukoihin.** Yksi kuuntelija juuressa ja
  `closest` kohteen tunnistamiseen. Elementin ja datan yhteys
  `data-*`-attribuutilla, ei sulkeumilla jokaiseen elementtiin.
- **`submit`, ei `click`.** Lomakkeen lähetys kuunnellaan lomakkeesta,
  jolloin Enter, ruudunlukijan toiminnot ja selaimen validointi
  toimivat. Painikkeille, jotka eivät lähetä, `type="button"`.
- **Kuuntelijan elinkaari.** Kuuntelija, joka lisätään pitkäikäiseen
  kohteeseen (`window`, `document`), poistetaan, kun näkymä poistuu.
  Muuten vanhat näkymät pysyvät muistissa ja reagoivat yhä
  (muistivuoto). Palauta poistofunktio tai käytä `AbortSignal`-
  valintaa: `addEventListener("click", f, { signal })`.
- **Asettelun hinta.** DOM-muutokset ovat halpoja, mutta asettelun
  lukeminen (`offsetHeight`, `getBoundingClientRect`) muutosten välissä
  pakottaa selaimen laskemaan asettelun heti (*layout thrashing*).
  Kirjoita ja lue erikseen, ja rakenna isot rakenteet irrallaan.

## Itsearviointi

- Osaat luoda ja päivittää elementtejä turvallisesti ilman
  `innerHTML`-ominaisuutta.
- Osaat selittää tapahtuman kuplimisen ja toteuttaa delegoinnin
  `closest`-metodilla.
- Osaat käsitellä lomakkeen `submit`-tapahtumassa ja lukea arvot
  `FormData`-oliosta tyypit tarkistaen.
- Osaat testata DOM-koodia Vitestillä ja happy-domilla.
