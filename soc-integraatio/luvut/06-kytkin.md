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

```{.dot otsikko="Kolme kytkentärakennetta. I on isäntä ja O orja. Jaetussa väylässä kaikki siirrot kulkevat yhden välittäjän läpi, ristikytkimessä jokaisella orjalla on oma välittäjänsä, ja hierarkiassa hitaat orjat ovat sillan takana."}
digraph {
  rankdir=LR; nodesep=0.18; ranksep=0.3;
  node [shape=box, fontsize=9, width=0.35, height=0.28];
  subgraph cluster_j { label="jaettu väylä"; fontsize=9; color=gray;
    ja [label="I"]; jb [label="I"]; jv [label="välittäjä ja\ndekooderi"];
    jo [label="O"]; jp [label="O"];
    ja -> jv; jb -> jv; jv -> jo; jv -> jp; }
  subgraph cluster_r { label="ristikytkin"; fontsize=9; color=gray;
    ra [label="I"]; rb [label="I"];
    rv [label="välittäjä"]; rw [label="välittäjä"];
    ro [label="O"]; rp [label="O"];
    ra -> rv; ra -> rw; rb -> rv; rb -> rw; rv -> ro; rw -> rp; }
  subgraph cluster_h { label="hierarkia"; fontsize=9; color=gray;
    ha [label="I"]; hb [label="I"]; hx [label="risti-\nkytkin"];
    hm [label="muisti"]; hs [label="silta"];
    hu [label="O"]; hv [label="O"]; hw [label="O"];
    ha -> hx; hb -> hx; hx -> hm; hx -> hs; hs -> hu; hs -> hv; hs -> hw; }
}
```

Pikku-SoC:n kytkin on jaettu väylä: se välittää yhden siirron
kerrallaan ja on siksi pieni ja helppo varmentaa. Kun DMA kopioi
muistia, ytimen pitää odottaa vuoroaan, ja hinta näkyy luvussa 10.
Ristikytkimessä ydin voisi lukea APB-laitetta samaan aikaan, kun DMA
käyttää RAMia.

Kytkimen sisällä on neljä osaa, jotka seuraavat osiot käyvät läpi:

```{.dot otsikko="Pikku-SoC:n kytkin. Välittäjä valitsee isännän, dekooderi orjan, ja reititys kytkee valitun parin yhteen siirron ajaksi. Osoite, joka ei osu mihinkään alueeseen, päätyy oletusorjalle."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.4;
  node [shape=box, fontsize=10];
  ydin [label="ydin\n(silta)"]; dma [label="DMA"];
  subgraph cluster_k { label="kytkin.sv"; fontsize=10; color=gray;
    val [label="välittäjä\n(vuorottelu)"];
    dek [label="dekooderi\n(kanta ja maski)"];
    rei [label="reititys"];
    ole [label="oletusorja\n(DECERR)"];
    val -> dek -> rei; dek -> ole [style=dashed]; }
  ram [label="RAM\n0x0000_0000"]; apb [label="APB-silta\n0x1000_0000"];
  ydin -> val; dma -> val; rei -> ram; rei -> apb;
}
```

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
