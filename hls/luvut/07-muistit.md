# Muistit ja taulukoiden jako

C++:ssa taulukon alkioihin pääsee käsiksi rajattomasti. Laitteistossa
taulukko on muisti, jolla on kiinteä määrä portteja, ja jokainen portti
käsittelee yhden alkion jaksossa. Kun silmukka avataan tai
liukuhihnoitetaan, muistiporteista tulee lähes aina ensimmäinen
pullonkaula. Tämä luku näyttää, miten muistikaistaa lisätään jakamalla
taulukko useaan muistiin.

## Muistit ja portit

| Muisti | Portit | Lukuviive | Käyttö |
|-----------------------------|----------------------|---------------|------------------------------|
| lohko-RAM (FPGA, esim. 18 kb) | 2, kumpikin luku tai kirjoitus | 1–2 jaksoa | suuret taulukot |
| hajautettu RAM (LUTRAM) | 1 kirjoitus, useita lukuja | 0–1 jaksoa | pienet taulukot |
| rekisterit | rajaton | 0 | hyvin pienet taulukot, viivelinjat |
| piirin ulkoinen muisti | väylä (AXI) | kymmeniä jaksoja | suuret aineistot |

minihls mallintaa jokaisen taulukon yksinkertaisena kaksiporttisena
RAMina: yksi lukuportti ja yksi kirjoitusportti, ja luettu data tulee
seuraavalla jaksolla. Ajoituksessa portti on resurssi kuten kertoja:

```{.python tiedosto="esimerkit/minihls/ajoitus.py" osa="resurssit"}
```

Vitis HLS:n parametritaulukon oletusrajapinta on yksiporttinen
`ap_memory`, ja muistin tyyppi valitaan pragmalla
`bind_storage variable=a type=ram_2p` (kaksiporttinen) tai
`ram_1p` (yksiporttinen).

## Matriisitulo

4 × 4 -matriisitulossa liukuhihnoitetaan sarakesilmukka. Sen
sisäsilmukka avataan silloin automaattisesti kokonaan, joten jokainen
kierros laskee yhden tulosalkion neljän tulon summana:

```{.cpp tiedosto="esimerkit/07-matriisi/matmul.cpp" osa="ydin"}
```

```{.tuloste tiedosto="esimerkit/07-matriisi/odotettu" osa="ajo1"}
```

Kierros lukee neljä alkiota kummastakin taulukosta, ja lukuportteja on
yksi, joten ResMII on 4. Liukuhihna on olemassa, mutta se aloittaa
kierroksen vain joka neljäs jakso, ja neljä kertolaskua jakavat yhden
kertojan. Summaimia on kymmenen, koska indeksilaskut `i * N + k` ovat
nekin yhteenlaskuja; vakiokertolasku `i * 4` on siirto.

## Taulukon jako

Pragma `array_partition` jakaa taulukon *pankkeihin* (*banks*), joista
kullakin on omat porttinsa:

| Tapa | Alkio *i* pankissa | Paikka pankissa | Sopii, kun |
|--------------------------------|----------------------------|---------------------|----------------------------------|
| `type=cyclic factor=F` | *i mod F* | *i / F* | peräkkäiset alkiot luetaan yhtä aikaa |
| `type=block factor=F` | *i / (koko / F)* | *i mod (koko / F)* | taulukon eri osat luetaan yhtä aikaa |
| `type=complete` | jokainen alkio oma rekisterinsä | – | pieni taulukko, kaikki alkiot yhtä aikaa |

Matriisi A luetaan riveittäin: kierros tarvitsee alkiot `a[4i]`,
`a[4i+1]`, `a[4i+2]` ja `a[4i+3]`, eli neljä peräkkäistä alkiota.
Syklinen jako neljällä vie ne eri pankkeihin. Matriisi B luetaan
sarakkeittain: alkiot `b[j]`, `b[4+j]`, `b[8+j]` ja `b[12+j]` ovat
neljän alkion välein, ja lohkojako neljään vie ne eri pankkeihin:

```{.cpp tiedosto="esimerkit/07-matriisi/matmul_jaettu.cpp" osa="jako"}
```

```{.tuloste tiedosto="esimerkit/07-matriisi/odotettu" osa="ajo2"}
```

II on nyt 1, ja neljä kertolaskua tehdään rinnakkain neljällä
kertojalla. Funktion latenssi laski 81 jaksosta 25 jaksoon. Jokaisella
ulomman silmukan kierroksella liukuhihna täyttyy ja tyhjenee, mikä on
näissä luvuissa merkittävä osa ajasta: 16 tulosalkiota vievät 24
jaksoa. Ulomman silmukan litistäminen sarakesilmukan kanssa poistaisi
tämän.

## Pankin on oltava tiedossa

Jotta jako auttaisi, työkalun on tiedettävä käännösaikana, mihin
pankkiin kukin luku osuu. minihls laskee indeksin *affiinin muodon*:
vakio plus silmukoiden kierroslaskurien monikerrat. Syklisessä jaossa
pankki on vakio, jos jokainen kerroin on jaollinen pankkien määrällä;
lohkojaossa pankki on vakio, jos indeksin pienin ja suurin arvo ovat
samassa lohkossa:

```{.python tiedosto="esimerkit/minihls/dfg.py" osa="muisti"}
```

Pankkien määrän on oltava kahden potenssi, jolloin pankin sisäinen
paikka saadaan siirrolla tai bittimaskilla ilman logiikkaa. Jos B
jaetaan syklisesti, alkion `b[4k + j]` pankki on *j mod 4*, joka
muuttuu kierroksittain:

```{.tuloste tiedosto="esimerkit/07-matriisi/odotettu" osa="ajo3"}
```

Oikea työkalu ei kieltäydy vaan lisää multiplekserin, joka valitsee
pankin ajon aikana. Tulos toimii, mutta jokainen luku tarvitsee kaikkien
pankkien portit, joten II ei parane ja logiikkaa tulee lisää. Siksi
jakotapa valitaan sen mukaan, miten silmukka taulukkoa lukee.

## Jaon hinta

- **Muistilohkoja kuluu enemmän.** FPGA:n lohko-RAM on kiinteän
  kokoinen (esimerkiksi 18 kb). 1 024 alkion 32-bittinen taulukko mahtuu
  kahteen lohkoon, mutta 16 pankkia vie 16 lohkoa, joista suurin osa on
  tyhjää. Pienet pankit toteutetaan LUTRAMina tai rekistereinä.
- **Täysi jako tekee rekistereitä.** `complete` on oikea valinta
  viivelinjoille ja pienille kerroinlistoille (luku 9), mutta 1 024
  alkion taulukko rekistereinä on hyvin suuri, ja muuttuvalla indeksillä
  sen lukeminen vaatii 1 024 syötteen multiplekserin.
- **Muotoilu on vaihtoehto.** Vitis HLS:n `array_reshape` yhdistää
  useita alkioita yhdeksi leveäksi sanaksi: neljä 32-bittistä alkiota
  luetaan yhdellä 128-bittisellä luvulla. Muistilohkoja ei kulu
  enempää, mutta yhtä aikaa luettavien alkioiden on oltava samassa
  sanassa.

## Ulkoiset muistit

Piirin ulkopuolinen DRAM liitetään HLS-ytimeen AXI-väylällä
(`interface m_axi`). Väylä siirtää dataa purskeina, ja yksittäisen
luvun viive on kymmeniä jaksoja. Siksi ydin kopioi datan ensin
paikalliseen muistiin purskeina, laskee paikallisesta muistista ja
kirjoittaa tuloksen takaisin, ja nämä kolme vaihetta limitetään
tietovuolla (`dataflow`) tai kaksoispuskuroinnilla. Taito
*SoC-integraatio* käsittelee AXI-väylän.

## Käytännössä

- **Laske muistikaista ensin.** Kuinka monta alkiota kustakin
  taulukosta luetaan kierroksessa? Se kertoo tarvittavan pankkien
  määrän ennen kuin ajat työkalua.
- **Valitse jakotapa käyttötavan mukaan.** Peräkkäiset alkiot:
  `cyclic`. Kaukana toisistaan olevat alkiot: `block`. Pieni taulukko:
  `complete`.
- **Tarkista, että pankit ovat vakioita.** Jos raportti näyttää
  multipleksereitä muistien edessä tai II ei parane, indeksi ei jakaudu
  pankkeihin käännösaikana.
- **Älä jaa kaikkea.** Jako kannattaa vain taulukoille, joiden portit
  rajoittavat II:tä.

## Itsearviointi

- Osaat laskea, montako muistiporttia silmukan kierros tarvitsee, ja
  päätellä siitä ResMII:n.
- Osaat valita syklisen, lohko- ja täyden jaon välillä taulukon
  käyttötavan mukaan.
- Osaat laskea alkion pankin ja paikan pankissa kummallakin
  jakotavalla.
- Osaat selittää, miksi pankin on oltava käännösaikana tiedossa ja mitä
  tapahtuu, jos se ei ole.
