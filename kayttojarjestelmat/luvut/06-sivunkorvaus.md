# Sivunkorvaus

Fyysistä muistia on vähemmän kuin prosessien yhteenlaskettua
osoiteavaruutta. Kun vapaat kehykset loppuvat ja uusi sivu
tarvitaan, ydin valitsee *uhrin*: sivun, jonka kehys otetaan
uuteen käyttöön. Muuttumaton sivu voidaan hylätä, koska se löytyy
tiedostosta; likainen sivu kirjoitetaan ensin tiedostoon tai
heittovaihtoalueelle. Jos uhri tarvitaan pian uudelleen, siitä tulee
suuri sivuvirhe ja levyhaku – tuhansia kertoja hitaampi kuin
muistihaku. Sivunkorvausalgoritmin tehtävä on arvata, mitä sivuja ei
tarvita.

Sama ongelma esiintyy kaikkialla, missä nopea ja pieni muisti on
hitaan ja suuren välimuistina: suorittimen välimuistit (taito
*Tietokonearkkitehtuuri*), tietokannan puskuripooli ja verkkosivujen
välityspalvelin. Algoritmit ovat samat.

## Algoritmit

Simulaattori pitää kirjaa kehyksistä ja niiden sivuista. Käyttöhetki
on LRU:ta varten ja käyttöbitti Clockia varten:

```{.c tiedosto="esimerkit/06-sivunkorvaus.c" osa="tila"}
```

Kukin algoritmi on vain eri tapa valita uhri:

```{.c tiedosto="esimerkit/06-sivunkorvaus.c" osa="uhri"}
```

- **FIFO** korvaa sivun, joka tuli muistiin ensimmäisenä. Toteutus on
  kiertävä osoitin, mutta sivun ikä ei kerro sen käytöstä: usein
  käytetty sivu korvautuu siinä missä kertakäyttöinenkin.
- **LRU** (least recently used) korvaa sivun, jota on käytetty
  pisimpään sitten. Menneisyys ennustaa tulevaa hyvin, koska ohjelmat
  käyttävät samoja sivuja toistuvasti (ajallinen paikallisuus). Tarkka
  LRU vaatisi aikaleiman jokaisessa muistiviittauksessa, mikä on
  laitteistolle liian kallista.
- **Clock** (toinen mahdollisuus) on LRU:n halpa likiarvo. MMU asettaa
  sivutaulumerkinnän käyttöbitin (RISC-V:n A-bitti), kun sivua
  käytetään. Osoitin kiertää kehyksiä: jos bitti on asetettu, se
  nollataan ja sivu saa toisen mahdollisuuden; ensimmäinen sivu,
  jonka bitti on nolla, on uhri.
- **OPT** (Béládyn optimaalinen) korvaa sivun, jota tarvitaan
  seuraavan kerran kauimpana tulevaisuudessa. Se on todistetusti
  paras mahdollinen, mutta vaatii tulevaisuuden tuntemista. Sitä
  käytetään mittapuuna: kuinka lähelle optimia toteutettava algoritmi
  pääsee.

Sivuvirhe syntyy, kun viitattu sivu ei ole missään kehyksessä.
Aluksi kehykset täytetään järjestyksessä, ja uhri valitaan vasta, kun
tyhjiä ei ole. Jokaisessa viittauksessa päivitetään käyttöhetki ja
käyttöbitti. Kolme viittausjonoa: oppikirjojen perusjono, Béládyn anomaliaa
havainnollistava jono ja silmukka, joka käy läpi yhtä useamman sivun
kuin kehyksiä on:

```{.c tiedosto="esimerkit/06-sivunkorvaus.c" osa="jonot"}
```

```{.tuloste tiedosto="esimerkit/06-sivunkorvaus.odotettu"}
```

## Tulosten tulkinta

Perusjonolla kolmella kehyksellä FIFO tekee 15 sivuvirhettä, Clock
14, LRU 12 ja OPT 9. LRU:n ja optimin väliin jää eroa, mutta FIFO on
selvästi huonoin. Clockin jäljessä näkyy toinen mahdollisuus: kun
sivu 3 tulee, sivun 0 bitti on asetettu (se luettiin juuri), joten
osoitin ohittaa sen ja korvaa sivun 1.

### Béládyn anomalia

Toisella jonolla FIFO tekee kolmella kehyksellä 9 sivuvirhettä mutta
neljällä 10 – lisämuisti pahensi tilannetta. Tämä *Béládyn anomalia*
on mahdollinen algoritmeille, joiden muistissa oleva sivujoukko $k$
kehyksellä ei ole aina $k + 1$ kehyksen joukon osajoukko. LRU ja OPT
ovat *pinoalgoritmeja*: $k$ viimeksi käytettyä sivua sisältyvät aina
$k + 1$ viimeksi käytettyyn, joten lisämuisti ei voi lisätä
sivuvirheitä. Clock perii FIFO:n kiertojärjestyksen, ja sekin
näyttää anomalian tällä jonolla.

### Silmukka ja ruuhkautuminen

Kolmas jono käy läpi neljää sivua kolmella kehyksellä. LRU korvaa
juuri sen sivun, jota tarvitaan seuraavaksi, ja jokainen viittaus on
sivuvirhe. OPT selviää puolella. Neljällä kehyksellä kaikki
algoritmit tekevät vain neljä pakollista virhettä. Siirtymä on jyrkkä:
kun *työjoukko* (engl. working set), eli viime aikoina käytettyjen
sivujen joukko, ei mahdu muistiin, sivuvirheiden määrä räjähtää.

Koko järjestelmän tasolla ilmiö on *ruuhkautuminen* (engl. thrashing).
Jos prosessien yhteenlasketut työjoukot ylittävät muistin, ne
varastavat toistensa sivuja, suoritin odottaa levyä, ja läpäisy romahtaa
juuri silloin, kun kuormaa on eniten. Ratkaisu ei ole parempi
korvausalgoritmi vaan vähemmän samanaikaisia prosesseja tai lisää
muistia. Linuxissa viimeinen keino on OOM killer.

## Linuxin sivunkorvaus

Linux käyttää LRU:n likiarvoa kahdella listalla: *aktiivisella* ja
*inaktiivisella*. Uusi sivu aloittaa inaktiiviselta listalta; jos sitä
käytetään siellä uudelleen, se siirtyy aktiiviselle. Uhrit otetaan
inaktiivisen listan hännästä, ja aktiivisesta listasta siirretään
sivuja inaktiiviseen, kun tasapaino vaatii. Kertakäyttöinen data –
esimerkiksi suuren tiedoston kertaluku – ei siksi syrjäytä toistuvasti
käytettyä. Uudemmat ytimet (6.1 alkaen) tarjoavat myös monisukupolvisen
LRU:n (MGLRU), joka jakaa sivut useampaan ikäluokkaan.

Tiedoston puhtaan sivun hylkääminen on halpaa, anonyymin sivun on
mentävä heittovaihtoon (`swappiness` säätää painotusta). `kswapd`
vapauttaa sivuja ennakoivasti, ja `mlock` estää sivun korvaamisen.

## Käytännössä

- **Paikallisuus ratkaisee:** sama algoritmi on erinomainen tai
  surkea viittausjonon mukaan. Ohjelma, joka käy dataa läpi
  järjestyksessä ja pienissä paloissa, sopii kaikille algoritmeille.
- **Varo silmukoita, jotka ovat hieman muistia suurempia:** LRU:n
  pahin tapaus on toistuva läpikäynti, joka ei mahdu muistiin.
- **Vertaa optimiin:** OPT on toteuttamaton, mutta simulaatiossa se
  kertoo, kuinka paljon parannettavaa on.
- **Ruuhkautuminen on kapasiteettiongelma:** kun suuria sivuvirheitä
  on jatkuvasti, lisää muistia tai vähennä kuormaa.

## Itsearviointi

- Osaat laskea FIFO-, LRU-, Clock- ja OPT-algoritmien sivuvirheet
  annetulle viittausjonolle ja kehysmäärälle.
- Osaat selittää, miksi LRU:ta approksimoidaan käyttöbitillä ja miten
  Clock toimii.
- Osaat selittää Béládyn anomalian ja pinoalgoritmin käsitteen.
- Osaat kuvata työjoukon ja ruuhkautumisen sekä niiden yhteyden
  sivuvirheiden määrään.
