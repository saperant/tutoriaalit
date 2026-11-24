# UVM-rekisterimalli

Taidossa *Laitteiston verifiointi* esiteltiin UVM:n rakenne: sekvenssit,
ajurit, monitorit ja tulostaulut. UVM:ssä on lisäksi
rekisterikerros (*register abstraction layer*, RAL), jolla testit
käsittelevät rekistereitä niminä eivätkä osoitteina: `regs.CTRL.write`
eikä väylän kirjoitus osoitteeseen 0. Kerroksen malli on rekisterikartan
kopio testipenkissä, ja se tuotetaan samasta kuvauksesta kuin RTL.

## Mallin rakenne

| Luokka | Vastaa | Tehtävä |
|------------------|----------------|-------------------------------------------|
| `uvm_reg_field` | kenttä | leveys, sijainti, pääsy, nollausarvo, ennustettu arvo |
| `uvm_reg` | rekisteri | kentät, luku ja kirjoitus |
| `uvm_reg_block` | osoitekartta | rekisterit ja alilohkot |
| `uvm_reg_map` | osoitteistus | rekisterien osoitteet ja väyläsovitin |
| `uvm_reg_adapter` | väylä | rekisteritoimenpide väylän transaktioksi ja takaisin |

`peakrdl uvm` tuottaa jokaisesta rekisteristä luokan. Ajastimen
`STATUS`:

```{.systemverilog tiedosto="esimerkit/tuotettu/otteet/uvm_status.sv"}
```

Kentän `configure`-kutsun parametrit ovat järjestyksessä vanhempi,
leveys, alin bitti, pääsy, haihtuvuus (*volatile*), nollausarvo,
onko nollausarvoa, satunnaistettavuus ja erillinen saavutettavuus.
Pääsy on sama UVM-lyhenne kuin luvussa 3. `VALMIS` on haihtuva, koska
laitteisto voi muuttaa sitä (`hwset`): malli ei voi ennustaa sen arvoa
pelkistä ohjelmiston kirjoituksista.

Lohkoluokka luo rekisterit ja liittää ne osoitekarttaan:

```{.systemverilog tiedosto="esimerkit/tuotettu/otteet/uvm_lohko.sv"}
```

## Mitä mallilla tehdään

Malli pitää kirjaa jokaisen kentän *ennustetusta* arvosta. Kun testi
kirjoittaa `CTRL`-rekisteriin, malli päivittää ennusteen. Kun testi
lukee rekisterin, malli vertaa luettua arvoa ennusteeseen
(`mirror(UVM_CHECK)`), ja ero on virhe. Pääsytapa ratkaisee
ennusteen: W1C-kentän ykkösen kirjoitus nollaa ennusteen, RO-kentän
kirjoitus ei muuta sitä, ja RC-kentän luku nollaa sen.

UVM:ssä on valmiita rekisterisekvenssejä, jotka käyttävät pelkkää
mallia, joten ne saa jokaiselle lohkolle ilman omaa koodia:

| Sekvenssi | Mitä se tarkistaa |
|------------------------|--------------------------------------------|
| `uvm_reg_hw_reset_seq` | jokaisen rekisterin nollausarvo |
| `uvm_reg_bit_bash_seq` | jokaisen kirjoitettavan bitin voi asettaa ja nollata erikseen |
| `uvm_reg_access_seq` | väylän kautta ja suoraan (*backdoor*) luettu arvo täsmäävät |
| `uvm_mem_walk_seq` | muistialueen jokainen osoite |

Bit bash -testi löytää esimerkiksi bittikenttien päällekkäisyydet ja
väärin kytketyt lukumultiplekserit. Kenttä, jota sekvenssi ei saa
koskea (esimerkiksi käynnistysbitti, joka käynnistäisi
laitteiston), suljetaan pois mallin attribuutilla.

## Mallin tarkistus ilman simulaattoria

Verilator 5.020 ei tue UVM:ää, joten mallia ei voi ajaa tämän paketin
työkaluilla. Ajettavat UVM-testit vaativat kaupallisen simulaattorin
tai uudemman Verilatorin. Malli voidaan silti tarkistaa: esimerkki
`08-uvm.py` lukee tuotetun luokkakuvauksen ja vertaa jokaisen kentän
tietoja kuvaukseen:

```{.python tiedosto="esimerkit/08-uvm.py" osa="configure"}
```

```{.python tiedosto="esimerkit/08-uvm.py" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/08-uvm.odotettu"}
```

Vertailu on tarkoituksella toisesta suunnasta kuin generaattori: se
lukee tuotetun tekstin eikä mallia. Näin se löytää myös generaattorin
virheet ja version vaihdoksen jälkeiset muutokset tuotoksessa.

## Käytännössä

- **Tuota UVM-malli kuvauksesta,** älä kirjoita sitä käsin. Käsin
  kirjoitettu malli on testipenkin oma tulkinta rekistereistä, ja
  silloin testi ja RTL voivat olla samaa mieltä väärästä asiasta.
- **Aja valmiit rekisterisekvenssit jokaiselle lohkolle.** Nollaus- ja
  bit bash -testit ovat ilmaisia, kun malli on tuotettu.
- **Merkitse haihtuvat kentät kuvaukseen.** Kun laitteisto voi muuttaa
  kenttää, `hw`-pääsy ja toiminnot kertovat sen generaattorille, ja
  malli osaa olla vertaamatta niitä ennusteeseen.
- **Sulje vaaralliset bitit pois automaattisista testeistä.**
  Käynnistys- ja nollausbitit voivat viedä lohkon tilaan, josta testi
  ei palaa.

## Itsearviointi

- Osaat kertoa, mitä UVM:n rekisterikerros tekee ja mistä luokista
  malli koostuu.
- Osaat lukea tuotetun `configure`-kutsun ja selittää sen parametrit.
- Osaat selittää, miten pääsytapa ja haihtuvuus vaikuttavat mallin
  ennusteeseen.
- Osaat nimetä UVM:n valmiit rekisterisekvenssit ja mitä ne
  tarkistavat.
