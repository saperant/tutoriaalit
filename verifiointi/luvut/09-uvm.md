# UVM:n käsitteet

Luvun 3 testipenkin rakenne (transaktio, generaattori, ajuri,
monitori, tulostaulu) on keksitty uudelleen jokaisessa
verifiointitiimissä. *Universal Verification Methodology* (UVM)
vakioi sen: se on SystemVerilogin luokkakirjasto ja menetelmä, joka
määrittelee osien nimet, rajapinnat, elinkaaren ja tavan yhdistää ne.
Kun kaksi yritystä käyttää UVM:ää, toisen tekemä väylän agentti
kytkeytyy toisen ympäristöön ilman muutoksia, ja verifioija tunnistaa
vieraan testipenkin rakenteen heti.

UVM syntyi kahden aiemman menetelmän (Synopsysin VMM ja Mentorin ja
Cadencen OVM) yhdistelmänä. Accellera julkaisi version 1.0 vuonna
2011, ja nykyinen määrittely on standardi IEEE 1800.2. Se on
teollisuuden vallitseva tapa rakentaa testipenkkejä ASIC-projekteissa.

## Rakenne

```text
uvm_test
 └── uvm_env
      ├── uvm_agent (aktiivinen)
      │    ├── uvm_sequencer  <── uvm_sequence (uvm_sequence_item)
      │    ├── uvm_driver
      │    └── uvm_monitor ──── analyysiportti ──┐
      ├── uvm_scoreboard  <──────────────────────┤
      └── uvm_subscriber (kattavuus)  <──────────┘
```

| UVM-luokka | Tehtävä |
|------------|---------|
| `uvm_sequence_item` | transaktio: kentät, satunnaistus, vertailu, tulostus |
| `uvm_sequence` | tuottaa transaktioita; voi käynnistää muita sekvenssejä |
| `uvm_sequencer` | välittää sekvenssien transaktiot ajurille ja sovittelee useiden sekvenssien välillä |
| `uvm_driver` | ottaa transaktion (`get_next_item`), ajaa sen liitäntään ja kuittaa (`item_done`) |
| `uvm_monitor` | havainnoi liitäntää ja julkaisee havainnot analyysiporttiin |
| `uvm_agent` | kokoaa sekvensserin, ajurin ja monitorin yhden liitännän ympärille |
| `uvm_scoreboard` | vertaa havaintoja referenssimalliin |
| `uvm_subscriber` | kuuntelee analyysiporttia, tyypillisesti kattavuutta varten |
| `uvm_env` | kokoaa agentit, tulostaulut ja kattavuuden |
| `uvm_test` | valitsee ympäristön asetukset ja ajettavat sekvenssit |

Agentti voi olla *aktiivinen* (sekvensseri, ajuri ja monitori) tai
*passiivinen* (vain monitori). Lohkotasolla agentti ajaa liitäntää.
Järjestelmätasolla saman liitännän ajaa toinen lohko, ja agentti
muutetaan passiiviseksi: sen monitori, tulostaulu ja kattavuus
toimivat edelleen. Tämä on luvun 3 periaate "vain ajuri ja monitori
tuntevat signaalit" vietynä loppuun.

## Elinkaari ja mekanismit

UVM:n komponentit eivät luo toisiaan konstruktoreissa vaan
**vaiheissa** (phases), jotka kirjasto ajaa järjestyksessä koko
hierarkialle:

| Vaihe | Tehtävä |
|-------|---------|
| `build_phase` | luo lapsikomponentit ylhäältä alas |
| `connect_phase` | kytkee portit, esimerkiksi monitorin analyysiportin tulostauluun |
| `run_phase` | aikaa kuluttava osa: sekvenssit, ajurit ja monitorit |
| `extract_phase`, `check_phase`, `report_phase` | lopputarkistukset ja raportit |

`run_phase` päättyy, kun kaikki **vastalauseet** (objections) on
peruttu: testi nostaa vastalauseen ennen sekvenssin käynnistämistä ja
laskee sen, kun sekvenssi on valmis. Se korvaa käsin kirjoitetut
"odota, kunnes jono on tyhjä" -silmukat.

**Tehdas** (factory) luo komponentit ja transaktiot nimen perusteella
(`type_id::create`). Testi voi korvata
tyypin toisella (`set_type_override`) muuttamatta ympäristön koodia,
esimerkiksi vaihtaa ajurin versioon, joka injektoi virheitä.
**Asetustietokanta** (`uvm_config_db`) välittää asetuksia ja
virtuaaliliitäntöjen kahvoja hierarkian läpi. **Raportointi**
(`` `uvm_info``, `` `uvm_error``) lisää viesteihin tunnisteen ja
lähteen ja laskee virheet testin lopputulosta varten.

Lisäksi UVM sisältää rekisterimallin (RAL), jolla testit lukevat ja
kirjoittavat lohkon rekistereitä nimillä, ja joka voidaan generoida
samasta rekisterikuvauksesta kuin RTL (taito *SoC-integraatio*).

Ajurin runko näyttää UVM:ssä tältä:

```text
class arb_ajuri extends uvm_driver #(arb_kohde);
    `uvm_component_utils(arb_ajuri)
    virtual arb_if vif;
    task run_phase(uvm_phase phase);
        forever begin
            seq_item_port.get_next_item(req);
            @(negedge vif.clk) vif.pyynto <= vif.pyynto | req.uudet;
            seq_item_port.item_done();
        end
    endtask
endclass
```

## UVM ja avoimet työkalut

UVM-kirjasto vaatii lähes koko SystemVerilogin luokka- ja
satunnaistusominaisuudet. Kaupalliset simulaattorit ajavat sen, mutta
Verilator 5.020 ei pysty kääntämään sitä, ja Icarus Verilog tukee
luokkia vain osittain. Verilatorin kehittäjät ovat lisänneet UVM:n
vaatimia piirteitä uusiin versioihin, mutta tuki on vielä kesken.

UVM on kuitenkin ennen kaikkea arkkitehtuuri, ja sen voi rakentaa
millä tahansa kielellä. Python-kirjasto *pyuvm* toteuttaa UVM:n
luokat ja vaiheet cocotb:n päälle. Tämän luvun esimerkki rakentaa
saman arkkitehtuurin suoraan cocotb:llä ilman kirjastoa, jotta jokainen
mekanismi näkyy koodissa.

## Arbiterin ympäristö

Ympäristön tiedosto alkaa vastaavuustaulukolla:

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="vastaavuus"}
```

Transaktiot ovat muuttumattomia tietoluokkia. Sekvenssin kohde on
niiden pyytäjien bittimaski, jotka nostavat pyynnön tällä jaksolla, ja
havainto on se, mitä monitori näki:

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="kohde"}
```

Sekvensseri on jono, jonka koko on yksi. Sekvenssi voi laittaa jonoon
seuraavan kohteen vasta, kun ajuri on ottanut edellisen. Tämä on
UVM:n `get_next_item`/`item_done`-kättely: sekvenssi ei tuota
kohteita etukäteen, vaan se voi reagoida siihen, mitä liitännässä
tapahtui.

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="sekvensseri"}
```

Ajuri pitää yllä voimassa olevia pyyntöjä. Myönnetty pyyntö poistuu,
ja uudet kohteet lisäävät pyyntöjä. Ajuri toteuttaa siis ympäristön
lupauksen, jonka formaali tarkistus kirjoitti oletukseksi (luku 8):
pyyntö pysyy, kunnes se myönnetään.

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="ajuri"}
```

Monitori julkaisee jokaisen havainnon kaikille tilaajille. Lista
funktioita on Pythonin vastine UVM:n analyysiportille: monitori ei
tiedä, kuka havaintoja kuuntelee.

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="monitori"}
```

Referenssimalli on puhdas funktio, joka laskee seuraavan myönnön
määrittelystä: ensimmäinen pyytäjä viimeksi palvellun jälkeen.

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="malli"}
```

Tarkastaja tekee kolme tarkistusta: yksikuumuus, vertailu malliin ja
odotusaika. Myöntö on rekisteröity, joten tämän jakson havainto
verrataan edellisen jakson pyynnöistä laskettuun ennusteeseen. Jokainen
virheviesti alkaa luokalla hakasulkeissa; luku 10 ryhmittelee
epäonnistumiset sen perusteella.

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="tarkastaja"}
```

Kattavuus seuraa, montako pyyntöä oli voimassa yhtä aikaa ja kuka sai
myönnön:

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="kattavuus"}
```

Ympäristö kokoaa osat ja kytkee monitorin tilaajat. Konstruktori
vastaa UVM:n vaiheita `build_phase` ja `connect_phase`, ja `aja`
vaihetta `run_phase`. Vastalauseen sijaan ajo päättyy, kun sekvenssi
on loppu ja ajuri on palauttanut liitännän lepotilaan.

```{.python tiedosto="esimerkit/pythonpenkit/arbiteri_ymparisto.py" osa="ymparisto"}
```

## Testit ja sekvenssit

Testit eroavat toisistaan vain sekvenssin osalta. Satunnainen
sekvenssi nostaa kunkin pyynnön todennäköisyydellä 0,2, kuormitus
pitää kaikki pyynnöt jatkuvasti voimassa:

```{.python tiedosto="esimerkit/pythonpenkit/test_arbiteri.py" osa="sekvenssit"}
```

```{.python tiedosto="esimerkit/pythonpenkit/test_arbiteri.py" osa="testi"}
```

Ehjä arbiteri läpäisee molemmat. Kuormitustestin kattavuus kertoo,
että siinä ei ole koskaan yhtä, kahta tai kolmea pyyntöä, mikä on
sen tarkoitus; satunnainen testi kattaa ne.

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-arbiteri.odotettu"}
```

Kiinteä etusija paljastuu heti, kun kaksi pyytäjää kilpailee.
Kuormitustestin kattavuus näyttää saman suoraan: vain pyytäjä 0 sai
myönnön.

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-arbiteri-kiintea.odotettu"}
```

Kahden myönnön vika vaatii neljä samanaikaista pyyntöä.
Kuormitustesti löytää sen ensimmäisellä mahdollisella jaksolla,
satunnainen testi vasta jaksolla 173, kun neljä pyyntöä sattui
olemaan voimassa yhtä aikaa:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-arbiteri-kaksi.odotettu"}
```

## Käytännössä

- **Agentti liitäntää kohden.** Jokaisella liitäntätyypillä on oma
  agenttinsa, jota käytetään kaikissa testipenkeissä, joissa liitäntä
  esiintyy. Väylä-agentit ostetaan usein valmiina (*verification IP*).
- **Passiivinen tila alusta asti.** Agentti suunnitellaan niin, että
  monitori, tulostaulu ja kattavuus toimivat ilman ajuria. Silloin ne
  siirtyvät järjestelmätason testipenkkiin sellaisinaan.
- **Testi valitsee, ympäristö ei muutu.** Uusi testi on uusi
  sekvenssi tai asetus, ei muutos ympäristöön. Tehdas ja
  asetustietokanta ovat UVM:n keinot tähän.
- **Sekvenssit kerroksina.** Perussekvenssit (yksi siirto, purske)
  yhdistetään testikohtaisiksi sekvensseiksi. Virtuaalinen sekvenssi
  ohjaa usean agentin sekvenssejä samasta paikasta.
- **UVM on raskas pienille lohkoille.** Sen hyöty on
  uudelleenkäytössä ja yhteisessä kielessä. Yksittäisen pienen lohkon
  testipenkki voi olla luvun 3 kaltainen, kunhan osat on erotettu.
- **Virheviesteille tunniste.** UVM:n viestitunnisteet ja tämän luvun
  hakasulkeiset luokat tekevät regressioiden luokittelusta helppoa.

## Itsearviointi

- Osaat nimetä UVM:n komponentit ja kertoa, mitä kukin tekee ja
  miten ne kytkeytyvät toisiinsa.
- Osaat selittää sekvenssin, sekvensserin ja ajurin kättelyn
  (`get_next_item` ja `item_done`).
- Osaat selittää UVM:n vaiheet, vastalauseet, tehtaan ja
  asetustietokannan tarkoituksen.
- Osaat rakentaa UVM:n arkkitehtuurin mukaisen ympäristön cocotb:llä
  ja tunnistaa vastaavuudet.
- Osaat selittää aktiivisen ja passiivisen agentin eron ja sen
  merkityksen järjestelmätason verifioinnissa.
