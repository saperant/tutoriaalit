# Kytkentäverkot ja muistikartta

Kun isäntiä ja orjia on useita, tarvitaan lohko, joka päättää, kuka
saa väylän (välitys, arbitration) ja kenelle siirto menee (dekoodaus).
Pikku-SoC:ssa se on `kytkin.sv`: kaksi isäntää (ydin ja DMA), kaksi
orjaa (RAM ja APB-silta) ja sisäinen oletusorja.

## Rakenteet

Kytkennän voi toteuttaa monella tavalla, ja valinta on hinnan ja
rinnakkaisuuden välinen kompromissi:

| Rakenne | Rinnakkaisuus | Hinta | Käyttö |
|---------|---------------|-------|--------|
| Jaettu väylä | yksi siirto kerrallaan | pienin | pienet mikrokontrollerit |
| Ristikytkin (crossbar) | jokainen isäntä eri orjaan yhtä aikaa | kasvaa tulona isännät × orjat | keskikokoiset SoC:t |
| Hierarkia | nopeat ristikytkimellä, hitaat siltojen takana | kohtuullinen | lähes kaikki SoC:t |
| Verkko piirillä (NoC) | pakettikytkentäinen, skaalautuva | suuri suunnittelutyö | suuret moniydinpiirit |

Pikku-SoC:n kytkin on jaettu väylä: se välittää yhden siirron
kerrallaan ja on siksi pieni ja helppo varmentaa. Kun DMA kopioi
muistia, ytimen pitää odottaa vuoroaan, ja hinta näkyy luvussa 10.
Ristikytkimessä ydin voisi lukea APB-laitetta samaan aikaan, kun DMA
käyttää RAMia.

## Dekoodaus

Osoite muutetaan orjan numeroksi vertaamalla sitä orjien alueisiin:

```{.systemverilog tiedosto="esimerkit/rtl/kytkin.sv" osa="dekoodaus"}
```

Alueet kuvataan kanta-osoitteena ja maskina. Kun alueen koko on kahden
potenssi ja kanta on tasattu koon mukaan, vertailu on pelkkiä
bittivertailuja, eikä dekooderissa tarvita vertailijoita tai
vähennyslaskuja. Osoite, joka ei osu mihinkään alueeseen, ohjataan
oletusorjalle.

## Välitys

Kun useampi isäntä pyytää väylää samaan aikaan, välittäjä valitsee
yhden. Pikku-SoC käyttää vuorottelevaa välittäjää (round robin):

```{.systemverilog tiedosto="esimerkit/rtl/kytkin.sv" osa="valittaja"}
```

Siirron jälkeen vuoro siirtyy valitusta isännästä seuraavaan. Näin
mikään isäntä ei näänny (starvation), vaikka toinen pyytäisi koko ajan.
Muita yleisiä välitystapoja ovat:

- **Kiinteä prioriteetti.** Yksinkertainen ja ennustettava, mutta
  korkean prioriteetin isäntä voi estää matalan kokonaan.
- **Painotettu vuorottelu.** Isäntä saa useita vuoroja kierrosta kohden,
  esimerkiksi näytönohjain kaksi ja DMA yhden.
- **QoS-perusteinen.** Isäntä ilmoittaa siirron kiireellisyyden
  (`AxQOS`), ja välittäjä huomioi sen. Reaaliaikaiset isännät
  (näyttö, ääni) saavat taatun kaistan.

## Reititys

Kun isäntä ja orja on valittu, kytkin kytkee ne yhteen siirron ajaksi.
Muut isännät eivät näe vastauksia, eivätkä muut orjat pyyntöjä:

```{.systemverilog tiedosto="esimerkit/rtl/kytkin.sv" osa="reititys"}
```

Reititys on kombinatorista: orjan `READY` kulkee kytkimen läpi isännälle
samalla jaksolla. Pienessä piirissä se on hyvä, koska kytkin ei lisää
viivettä. Suuressa piirissä polku on liian pitkä, ja kytkimen
liitäntöihin lisätään rekisteriviipaleet (luku 4).

## Oletusorja

Osoite, jossa ei ole orjaa, ei saa jättää isäntää odottamaan ikuisesti.
Kytkimen sisäinen *oletusorja* (default slave) hyväksyy siirron ja
vastaa DECERR-koodilla. Ydin muuttaa virhevastauksen poikkeukseksi, ja
ohjelmisto näkee, mihin osoitteeseen yritettiin (luku 12).
Kytkimen tilakoneessa oletusorjalla on oma tilansa `VASTAUS`, ja sen
kättelysignaalit tuotetaan kytkimessä itsessään.

## Järjestys ja yhtenäisyys

Kytkin päättää myös siirtojen järjestyksen eri isäntien välillä. Jos
ydin kirjoittaa puskuriin ja käynnistää sitten DMA:n, DMA:n on nähtävä
kirjoitettu data. Pikku-SoC:ssa tämä on automaattista, koska kytkin
käsittelee siirrot yksi kerrallaan ja RAM kirjoittaa ennen
vastaamistaan. Oikeassa järjestelmässä kirjoitus voi olla vielä
puskurissa (kirjoituspuskuri, välimuisti) silloin, kun ydin saa
vastauksen, joten ohjelmiston on käytettävä muistiesteitä ja
tyhjennettävä välimuistit tai järjestelmän on oltava koherentti
(luku 10).

## Käytännössä

- **Aloita yksinkertaisesta.** Jaettu väylä riittää, kunnes mittaus
  osoittaa sen pullonkaulaksi. Ristikytkimen ja NoC:n monimutkaisuus
  maksetaan varmennuksessa.
- **Kahden potenssin alueet.** Tasatut alueet tekevät dekoodauksesta
  halvan ja muistinsuojauksesta helpon. Kartan aukot jätetään
  laajennuksille.
- **Välittäjä valitaan kuorman mukaan.** Vuorottelu on hyvä oletus.
  Reaaliaikaiset isännät tarvitsevat taatun kaistan, ja se lasketaan
  pahimman tapauksen mukaan, ei keskiarvosta.
- **Oletusorja aina.** Yksikään osoite ei saa jäädä vastaamatta, ja
  virhevastaus on parempi kuin hiljainen nolla.
- **Generoi kytkin.** Kytkimen dekooderi, välittäjät ja
  rekisteriviipaleet generoidaan tavallisesti työkalulla tai
  parametroidusta IP:stä (esimerkiksi OpenTitanin `tlgen`, PULPin AXI-
  kirjasto, valmistajien kytkin-IP:t). Käsin kirjoitettu kytkin on
  harvoin oikein ensimmäisellä kerralla.

## Itsearviointi

- Osaat vertailla jaettua väylää, ristikytkintä, hierarkiaa ja NoC:ia.
- Osaat toteuttaa osoitedekoodauksen kanta–maski-pareilla ja
  perustella tasatut alueet.
- Osaat toteuttaa vuorottelevan välittäjän ja kertoa, miksi se estää
  nääntymisen.
- Osaat selittää oletusorjan tehtävän.
- Osaat kertoa, miksi kirjoituksen ja DMA:n käynnistyksen järjestys
  vaatii huomiota järjestelmässä, jossa on puskureita.
