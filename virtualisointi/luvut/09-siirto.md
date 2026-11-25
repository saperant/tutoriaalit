# Tilannevedokset ja siirto

Virtuaalikoneen koko tila on dataa: muistin sisältö, suorittimen
rekisterit ja laitteiden tila. Sen voi tallentaa, kopioida ja palauttaa.
Tällä perustuvat tilannevedokset, varmuuskopiointi, koneen
kloonaaminen ja elävä siirto, jossa käynnissä oleva kone siirretään
toiseen isäntään käyttäjän huomaamatta.

## Levy- ja konevedokset

| Vedos | Sisältö | Palautuksen jälkeen |
|-------|---------|---------------------|
| Levyvedos | levyn tila | vieras käynnistyy kuin virran katkettua |
| Levyvedos vieraan avulla | levyn tila, tiedostojärjestelmät tyhjennetty | puhdas tila (vierasagentti `fsfreeze`) |
| Konevedos (`savevm`) | levy, muisti, suoritin, laitteet | kone jatkaa täsmälleen samasta kohdasta |

Luvun 4 qcow2-esimerkki teki levyvedoksen. Pelkkä levyvedos käynnissä
olevasta koneesta on **kaatumisen kestävä** (crash-consistent): se on
sama kuin levy virran katketessa. Tietokanta toipuu siitä
lokinsa avulla, mutta puoliksi kirjoitettu tiedosto ei. Siksi
varmuuskopiointi pyytää vierasta ensin tyhjentämään puskurit
(QEMU:n vierasagentti, VMware Tools).

## Siirto

Siirrossa (migration) koneen tila lähetetään toiselle
QEMU-prosessille, joka on käynnistetty valitsimella `-incoming`.
Kohteen laitteiston on oltava sama: sama koneen tyyppi, samat
laitteet, sama suoritinmalli. Siksi klustereissa käytetään yhteistä
suoritinmallia (luku 3).

**Elävä siirto** (live migration) tehdään koneen käydessä:

1. **Esikopiointi** (pre-copy). Koko muisti kopioidaan kohteeseen kone
   käynnissä. Hypervisor merkitsee sivut likaisiksi, kun vieras
   kirjoittaa niihin (EPT:n kirjoitussuojaus tai dirty-bitit).
2. **Iterointi.** Likaiset sivut kopioidaan uudelleen. Kierrokset
   jatkuvat, kunnes likaisia sivuja on niin vähän, että ne ehditään
   siirtää sallitussa katkossa (oletuksena noin 300 ms).
3. **Pysäytys ja kopio.** Kone pysäytetään, viimeiset sivut ja
   suorittimen ja laitteiden tila siirretään.
4. **Jatko.** Kohde jatkaa, ja verkkoa varten lähetetään ARP-ilmoitus,
   jotta kytkimet oppivat MAC-osoitteen uuden paikan.

Jos vieras likaa muistia nopeammin kuin verkko siirtää, esikopiointi
ei suppene. Silloin QEMU voi hidastaa vierasta (**auto-converge**) tai
siirtyä **jälkikopiointiin** (post-copy): kohde käynnistetään heti, ja
puuttuvat sivut haetaan lähteestä sivuvirheinä. Jälkikopiointi suppenee
aina, mutta jos verkko katkeaa kesken, kone menetetään, koska sen tila
on kahdessa paikassa.

## Siirto käytännössä

Seuraava esimerkki siirtää luvun 1 kaltaisen vieraan toiseen
QEMU-prosessiin. Vieras tulostaa A-rivin ja jää odottamaan syötettä
sarjaportista kasvattaen samalla laskuria:

```{.c tiedosto="esimerkit/vieras/lahteet/odota.c"}
```

Lähde pysäytetään, ja sen tila kirjoitetaan siirtovirtana tiedostoon.
Oikeassa siirrossa virta kulkee TCP-yhteyttä pitkin
(`tcp:kohde:4444`):

```{.python tiedosto="esimerkit/09-siirto.py" osa="lahde"}
```

Kohde käynnistetään samalla vieraalla ja valitsimella `-incoming`. Se
lukee tilan, jää pysäytetyksi ja jatkaa komennolla `cont`. Vasta nyt
sarjaporttiin kirjoitetaan merkki:

```{.python tiedosto="esimerkit/09-siirto.py" osa="kohde"}
```

```{.tuloste tiedosto="esimerkit/09-siirto.odotettu"}
```

Kohde ei käynnistänyt vierasta alusta: se ei tulostanut A-riviä
uudelleen, ja laskurin arvo säilyi siirron yli (paluuarvo
$(5 \ll 1) \mid 1 = 11$). Esimerkki pysäytti lähteen ennen siirtoa,
eli se teki **kylmän siirron**. Elävässä siirrossa muisti kopioidaan
jo ennen pysäytystä, mutta lopputulos on sama.

## Konttien siirto

Konteilla vastaava on vaikeampi, koska kontin tila on isännän ytimessä:
avoimet tiedostot, pistokkeet, ajastimet ja prosessipuu. **CRIU**
(Checkpoint/Restore In Userspace) tallentaa prosessipuun tilan ja
palauttaa sen, ja Podman ja Kubernetes osaavat käyttää sitä
(`podman container checkpoint`). Käytännössä konttien maailmassa
siirto korvataan yleensä uudelleenkäynnistyksellä: tilaton kontti
käynnistetään uudessa paikassa, ja tila on tietokannassa tai
taltiossa.

## Käytännössä

- **Vedos ei ole varmuuskopio.** qcow2:n sisäinen vedos on samassa
  tiedostossa kuin levy. Varmuuskopio on toisessa paikassa
  (ks. taito *Palvelinympäristöt*: 3-2-1-sääntö).
- **Siirto vaatii yhteensopivuuden.** Sama QEMU-koneversio
  (`-machine pc-q35-8.2`), sama suoritinmalli ja sama laitejoukko.
  Läpivientilaitteita ei voi siirtää.
- **Seuraa siirron suppenemista.** `query-migrate` kertoo likaantumis-
  ja siirtonopeuden. Muistia kirjoittava kuorma (tietokanta,
  välimuisti) vaatii nopean siirtoverkon, kaistarajan nostamisen tai
  auto-converge-hidastuksen.
- **Siirrä huoltokatkojen sijaan.** Elävä siirto mahdollistaa isännän
  päivityksen ilman palvelukatkoa: koneet siirretään pois, isäntä
  päivitetään, ja koneet palaavat.

## Itsearviointi

- Osaat erottaa levyvedoksen, kaatumisen kestävän vedoksen ja
  konevedoksen ja kertoa, milloin kukin riittää.
- Osaat kuvata elävän siirron vaiheet ja selittää, miksi esikopiointi
  ei aina suppene ja mitä jälkikopiointi muuttaa.
- Osaat siirtää QEMU-koneen QMP:n `migrate`-komennolla ja käynnistää
  kohteen valitsimella `-incoming`.
- Osaat perustella, miksi kontteja yleensä käynnistetään uudelleen
  siirtämisen sijaan.
