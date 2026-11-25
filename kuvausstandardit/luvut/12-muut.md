# Muut kuvaukset suunnitteluvuossa

Tämä luku on liitteenomainen katsaus, eikä muu taito nojaa siihen.
Rekisterikuvaukset ovat vain yksi suunnitteluvuon koneluettavista
kuvauksista. Laitteiston toteutus kulkee RTL:stä piiriksi joukon
standardoituja tiedostomuotoja kautta, ja jokainen niistä on jonkin
työkalun syöte ja toisen tuote. Tämän luvun tarkoitus on tunnistaa ne:
mitä kukin kuvaa, kuka sen kirjoittaa ja missä vuon vaiheessa sitä
käytetään. Tarkemmin niitä käytetään taidoissa *ASIC-toteutus* ja
*FPGA-toteutus*; tehoalueiden simuloitu sekvenssi on taidossa
*SoC-integraatio* ja aaltomuotojen ohjelmallinen käsittely taidossa
*EDA-työkaluketjujen automatisointi*.

## Yleiskuva

| Muoto | Ylläpitäjä | Mitä kuvaa | Kirjoittaja | Käyttäjä |
|-----------|-----------|----------------------------|---------------|----------------|
| SDC | Synopsys, avoin muoto | ajoitusrajoitteet: kellot, tulo- ja lähtöviiveet, poikkeukset | suunnittelija | synteesi, sijoittelu, ajoitusanalyysi |
| UPF | IEEE 1801 | virranhallinnan aikomus: tehoalueet, kytkimet, eristys | suunnittelija | synteesi, simulointi, sijoittelu |
| Liberty (.lib) | Synopsys, avoin muoto | standardisolujen ajoitus, teho ja toiminta | piirivalmistaja | synteesi, ajoitusanalyysi |
| LEF | Cadence, avoin muoto | solujen ja makrojen fyysiset muodot ja kerrokset | piirivalmistaja | sijoittelu ja reititys |
| DEF | Cadence, avoin muoto | sijoitettu ja reititetty piiri | sijoittelutyökalu | reititys, tarkistukset |
| SPEF | IEEE 1481 | reitityksen parasiittiset resistanssit ja kapasitanssit | parasiittien eristys | ajoitusanalyysi |
| GDSII, OASIS | (de facto), SEMI | piirin geometria valmistukseen | sijoittelutyökalu | valmistaja |
| VCD, FST | IEEE 1364, GTKWave | simuloidut aaltomuodot | simulaattori | aaltomuotokatselin, tehoanalyysi |

Kaksi ryhmää erottuu. SDC ja UPF ovat *suunnittelijan aikomuksia*: ne
kirjoitetaan käsin tai tuotetaan, ja ne kulkevat RTL:n rinnalla koko
vuon läpi. Liberty, LEF, DEF, SPEF ja GDSII ovat *toteutuksen
kuvauksia*: ne tulevat piirivalmistajalta tai työkaluilta, eikä niitä
yleensä muokata käsin.

## SDC: ajoitusrajoitteet

SDC (Synopsys Design Constraints) kertoo työkaluille, millä
taajuudella piirin on toimittava ja mitä signaalipolkuja ei tarvitse
ajoittaa. Se on Tcl-kieltä, joten kaikki Tcl:n rakenteet ovat
käytettävissä. Ajastinlohkon rajoitteet:

```{.tcl tiedosto="esimerkit/muut/ajastin.sdc" osa="sdc"}
```

Rajoitteet voivat seurata rekisterikuvauksesta: väyläliitännän portit
ja niiden kellotoimialue ovat generaattorin tiedossa. Kellot,
viiveet ja poikkeukset ovat kuitenkin järjestelmätason päätöksiä, ja
ne kirjoitetaan yleensä käsin lohkon ja piirin tasolla.

## UPF: virranhallinta

UPF (Unified Power Format, IEEE 1801) kuvaa virranhallinnan erillään
RTL:stä: mitkä osat piiristä ovat omia tehoalueitaan, millä kytkimellä
alue sammutetaan ja mitä sammutetun alueen lähdöille tehdään. Taidossa
*SoC-integraatio* tehoalueet esiteltiin periaatteena. UPF on niiden
standardi kuvaus, ja simulaattori, synteesi ja sijoittelu käyttävät
samaa tiedostoa:

```{.tcl tiedosto="esimerkit/muut/ajastin.upf" osa="upf"}
```

Eristys (*isolation*) pakottaa sammutetun alueen lähdöt tunnettuun
arvoon, jotta päällä oleva logiikka ei näe kelluvia signaaleja.
Säilytysrekisterit (*retention*) ja jännitetason muuntimet (*level
shifter*) kuvataan samaan tapaan.

## Tarkistus ilman työkalua

SDC ja UPF ovat Tcl:ää, joten niiden syntaksi ja komentojen nimet voi
tarkistaa Tcl-tulkissa ilman kaupallista työkalua. Tarkistin korvaa
tunnetut komennot proseduureilla, jotka tulostavat komennon ja
valitsimien määrän, ja tuntematon komento kaataa tarkistuksen:

```{.tcl tiedosto="esimerkit/muut/tarkista.tcl"}
```

```{.python tiedosto="esimerkit/13-muut.py" osa="kirjoitusvirhe"}
```

```{.tuloste tiedosto="esimerkit/13-muut.odotettu"}
```

Kirjoitusvirhe `set_flase_path` jäisi muuten huomaamatta siihen asti,
kun synteesityökalu ajetaan, ja jotkin työkalut vain varoittavat
tuntemattomasta komennosta. Puuttuva poikkeus näkyy silloin
ajoitusraportissa virheellisenä rikkeenä, ja sen syytä etsitään
väärästä paikasta. Kevyt tarkistus jokaisessa muutoksessa on halpa.

## Aaltomuodot

VCD (Value Change Dump) on Verilog-standardin tekstimuoto
simuloiduille aaltomuodoille: otsakkeessa on signaalien hierarkia, ja
sen jälkeen aikaleimat ja arvojen muutokset. Se on yksinkertainen
lukea omalla ohjelmalla, mutta suurissa simulaatioissa tiedostot
kasvavat gigatavuihin. FST on GTKWaven tiivis binäärimuoto, jota
Verilator ja Icarus Verilog osaavat kirjoittaa (Verilatorissa `--trace-fst`).
Aaltomuotoja käyttävät katselimien lisäksi tehoanalyysityökalut, jotka
laskevat signaalien kytkentäaktiivisuuden simuloinnista.

## Käytännössä

- **Tunne vuon tiedostot.** Kun työkalu valittaa, tiedä, mikä kuvaus on
  sen syöte ja kuka sen on kirjoittanut.
- **SDC ja UPF ovat lähdekoodia.** Ne versioidaan, katselmoidaan ja
  tarkistetaan kuten RTL, koska niiden virheet näkyvät vasta myöhään.
- **Tarkista Tcl-kuvaukset kevyesti jokaisessa muutoksessa.**
  Komentojen nimet ja syntaksi tarkistuvat sekunnissa, vaikka
  varsinainen työkalu olisi vain lisenssipalvelimen takana.
- **Älä muokkaa valmistajan kuvauksia.** Liberty-, LEF- ja
  GDSII-tiedostot ovat piirivalmistajan sopimusaineistoa; poikkeamat
  kuvataan omissa tiedostoissa.

## Itsearviointi

- Osaat kertoa, mitä SDC, UPF, Liberty, LEF, DEF, SPEF, GDSII ja VCD
  kuvaavat ja missä vuon vaiheessa niitä käytetään.
- Osaat lukea ja kirjoittaa perus-SDC-rajoitteet (kello, tulo- ja
  lähtöviiveet, väärä polku).
- Osaat selittää UPF:n tehoalueen, kytkimen ja eristyksen.
- Osaat tarkistaa Tcl-pohjaisen kuvauksen syntaksin ja komentojen
  nimet ilman varsinaista työkalua.
