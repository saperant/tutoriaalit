# Pohjapiirros ja sijoittelu

Netlistan jälkeen piiri saa fyysisen muodon. Pohjapiirros päättää
piirin koon ja rakenteen, sijoittelu antaa jokaiselle solulle paikan,
kellopuu ja reititys (luku 8) yhdistävät ne. Näistä vaiheista syntyy
suurin osa johdinviiveestä, ja johdin on pienissä prosesseissa usein
hitaampi kuin portti.

## Pohjapiirros

Pohjapiirros (floorplan) määrittelee:

- **Ytimen koon ja muodon.** Käyttöaste (utilization) on solujen
  pinta-alan osuus ytimestä; tyypillisesti 60–80 %. Täysi ydin ei
  reitity.
- **IO-renkaan** ja nastojen järjestyksen piirilevyn ja koteloinnin
  mukaan (luku 11).
- **Makrot**, kuten muistit ja analogialohkot, sijoitetaan käsin
  reunoille, ja niiden ympärille jätetään reititystilaa.
- **Tehoverkon**: rengas ytimen ympäri ja pystysuuntaiset liuskat,
  joista syöttö jakautuu solurivien reunoille (luku 10).
- **Solurivit**: standardisolut asettuvat riveihin, joissa joka
  toinen rivi on peilattu, jotta vierekkäiset rivit jakavat
  syöttö- tai maakiskon.

## Sijoittelu

Sijoittelu minimoi johdinpituutta ja pitää samalla ajoituksen ja
ruuhkan kurissa. Kustannuksena käytetään puolipiirin johdinpituutta
(half-perimeter wire length, HPWL): johtimen kaikki pinnit rajaavan
suorakulmion puolikas piiri. Se on halpa laskea ja hyvä arvio
reitityksen pituudelle.

```{.python tiedosto="esimerkit/07-sijoittelu.py" osa="hpwl"}
```

Netlistasta muodostetaan johtimet solujen ja porttien listoina.
Kello jätetään pois, koska kellopuu rakennetaan erikseen:

```{.python tiedosto="esimerkit/07-sijoittelu.py" osa="verkot"}
```

Simuloitu jäähdytys (simulated annealing) on vanha ja havainnollinen
sijoittelualgoritmi: se vaihtaa kahden paikan sisällön ja hyväksyy
myös huononnuksen todennäköisyydellä, joka pienenee lämpötilan
laskiessa. Näin haku pääsee pois paikallisista minimeistä.

```{.python tiedosto="esimerkit/07-sijoittelu.py" osa="jaahdytys"}
```

Lopuksi arvioidaan ruuhkaisuutta RUDY-menetelmällä (rectangular
uniform wire density): jokaisen johtimen pituus levitetään sen
rajaavan suorakulmion alueelle.

```{.python tiedosto="esimerkit/07-sijoittelu.py" osa="ruuhka"}
```

```{.python tiedosto="esimerkit/07-sijoittelu.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/07-sijoittelu.odotettu"}
```

Jäähdytys yli puolittaa johdinpituuden. Ruuhkakartta näyttää,
mihin johtimet kasautuvat: kuumissa kohdissa reitittimellä on vähiten
tilaa, ja sijoittelija harventaa niitä tarvittaessa.

Nykyiset sijoittelijat ovat analyyttisiä: ne mallintavat johdinpituuden
derivoituvana funktiona ja solujen tiheyden sähköstaattisena
potentiaalina (esim. OpenROADin RePlAce) ja ratkaisevat miljoonien
solujen sijoittelun gradienttimenetelmillä. Globaalin sijoittelun
jälkeen *laillistus* siirtää solut riveihin ilman päällekkäisyyttä, ja
*yksityiskohtainen sijoittelu* parantaa paikallisesti.

## Ajoitusohjattu sijoittelu

Sijoittelu ei minimoi pelkkää pituutta. Kriittisen polun johtimille
annetaan suurempi paino, ja sijoittelun jälkeen ajetaan optimointi,
joka puskuroi pitkät johtimet, vaihtaa solujen kokoja ja kopioi
suuren haarautuman rekisterit (luvun 5 `vaihe`-signaali). OpenROADissa
tämä on `repair_design` ja `repair_timing`.

## Käytännössä

- **Pohjapiirros ratkaisee eniten.** Huonosti sijoitettu makro tai
  liian täysi ydin pilaa ajoituksen ja reitittyvyyden, eikä mikään
  myöhempi vaihe korjaa sitä.
- **Datavuo näkyviin.** Lohkot, jotka keskustelevat paljon,
  sijoitetaan vierekkäin. Väylät kulkevat makrojen välissä suoraan.
- **Ruuhka ennen ajoitusta.** Ruuhkaisessa kohdassa reititin kiertää,
  johtimet pitenevät ja ajoitus huononee. Paikallista tiheyttä
  rajoitetaan (placement density) tai lisätään tilaa.
- **Käyttöaste on kompromissi.** Matala käyttöaste helpottaa
  reititystä mutta pidentää johtimia ja kasvattaa piiriä.

## Itsearviointi

- Osaat kertoa, mitä pohjapiirros päättää ja miksi käyttöaste ei voi
  olla 100 %.
- Osaat laskea HPWL:n ja selittää, miksi sitä käytetään sijoittelun
  kustannuksena.
- Osaat kuvata simuloidun jäähdytyksen periaatteen ja sen, miksi
  huononnuksia hyväksytään.
- Osaat arvioida ruuhkaisuutta ja kertoa, miten se vaikuttaa
  ajoitukseen.
