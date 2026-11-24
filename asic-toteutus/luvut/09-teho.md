# Tehonkulutus

CMOS-piirin teho koostuu kolmesta osasta:

- **Dynaaminen teho** syntyy, kun johtimen kapasitanssi varataan ja
  puretaan: $P = \alpha \cdot C \cdot V^2 \cdot f$, missä $\alpha$ on
  aktiivisuus (siirtymiä jaksossa).
- **Oikosulkuteho** syntyy hetkestä, jolloin sekä ylös- että
  alasvetotransistori johtavat siirtymän aikana; hitaat siirtymät
  kasvattavat sitä.
- **Vuoto** on transistorien läpi kulkeva virta, vaikka mikään ei
  vaihda tilaa. Pienissä prosesseissa se voi olla puolet
  kokonaistehosta.

Jännite on tehon kaavassa toisessa potenssissa, joten jännitteen
laskeminen on tehokkain keino; sen hinta on hitaampi logiikka.

## Aktiivisuudesta tehoksi

Teho arvioidaan simuloimalla piiriä todellisella kuormalla ja
laskemalla jokaisen johtimen siirtymät. Porttitason simulointi
tallentaa ne VCD-tiedostoon (value change dump):

```{.python tiedosto="esimerkit/09-teho.py" osa="vcd"}
```

Jokainen nouseva siirtymä vie käyttöjännitteestä energian $C V^2$.
Kuormat tulevat samasta mallista kuin ajoitusanalyysissa, vuoto
kirjastosta:

```{.python tiedosto="esimerkit/09-teho.py" osa="teho"}
```

Laskurin sallinta on päällä neljäsosan ajasta, mutta kello vaihtaa
tilaa joka jaksolla: kellon teho on lähes kaksinkertainen logiikkaan
verrattuna. Tämä on tyypillistä; kellopuu kuluttaa usein 30–50 %
piirin dynaamisesta tehosta.

## Kellon portitus

Kun rekisteri ei päivity, sen kelloa ei tarvita. Kellon portitus
pysäyttää kellon lohkolta, jonka sallinta on pois:

```{.python tiedosto="esimerkit/09-teho.py" osa="portitus"}
```

```{.tuloste tiedosto="esimerkit/09-teho.odotettu"}
```

Portitusta ei tehdä JA-portilla. Jos sallinta muuttuu kellon ollessa
ylhäällä, JA-portin lähtöön syntyy lyhennetty pulssi, joka voi
kellottaa kiikut väärin. Integroitu portituslohko (integrated clock
gate, ICG) salpaa sallinnan, kun kello on alhaalla:

```{.systemverilog tiedosto="esimerkit/09-portitus.sv" osa="icg"}
```

```{.systemverilog tiedosto="esimerkit/09-portitus.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/09-portitus.odotettu"}
```

Kaavio on piirretty saman testipenkin simulaatiosta nanosekunnin
tarkkuudella (`make -C esimerkit`):

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/portitus.json" otsikko="JA-portti ja ICG simulaatiosta, 0–40 ns"}
```

JA-portti tuottaa 3 ns:n ja 2 ns:n pulssit, ICG vain täysiä 5 ns:n
pulsseja. Kirjastoissa ICG on valmis solu, ja synteesityökalu lisää
sen automaattisesti, kun rekisteriryhmällä on yhteinen sallinta.

## Tehoalueet ja UPF

Suuremmat säästöt saadaan sammuttamalla lohkoja kokonaan (power
gating) tai ajamalla niitä eri jännitteellä (multi-voltage). Tämä
vaatii lisälogiikkaa: eristyssolut (isolation) pitävät sammutetun
lohkon lähdöt tunnetussa tilassa, tasonsiirtimet (level shifter)
muuntavat signaalin jännitealueelta toiselle ja säilytysrekisterit
(retention) muistavat tilan sammutuksen yli. Tehoarkkitehtuuri
kuvataan erillisessä UPF-tiedostossa (Unified Power Format, IEEE
1801), jota synteesi, sijoittelu ja verifiointi lukevat:

```text
create_power_domain PD_YDIN -include_scope
create_power_domain PD_DSP  -elements {u_dsp}
create_supply_net VDD_DSP
create_power_switch sw_dsp -domain PD_DSP \
    -input_supply_port {vin VDD} -output_supply_port {vout VDD_DSP} \
    -control_port {en dsp_paalla} -on_state {paalla vin {en}}
set_isolation iso_dsp -domain PD_DSP -isolation_signal dsp_eristys \
    -clamp_value 0 -applies_to outputs
```

Lisäksi kynnysjännitteiltään erilaiset solut (multi-Vt) vaihtavat
nopeutta vuotoon: matalan kynnyksen nopeat solut vain kriittisille
poluille, korkean kynnyksen hitaat muualle.

## Käytännössä

- **Aktiivisuus ratkaisee.** Tehoarvio on vain niin hyvä kuin
  simuloitu kuorma. Tyhjäkäynti ja huippukuorma arvioidaan erikseen.
- **Kellon portitus RTL:ssä.** Kirjoita sallinnat näkyviksi
  (`if (sallinta) q <= d;`), niin työkalu löytää portitettavat
  ryhmät. Hienojakoinen portitus säästää eniten, mutta ICG:t
  maksavat pinta-alaa ja vinousta.
- **Turhat siirtymät.** Hasardit ja häiriöpulssit (glitch) kuluttavat
  tehoa; syvä kombinaatiologiikka ja aritmetiikkaketjut ovat
  pahimpia.
- **Tehoalueet ovat arkkitehtuuripäätös.** Sammutettava lohko,
  herätyslogiikka ja tilan säilytys suunnitellaan alusta asti, ja
  verifiointi simuloi myös sammutukset.

## Itsearviointi

- Osaat selittää dynaamisen tehon, oikosulkutehon ja vuodon sekä
  laskea dynaamisen tehon aktiivisuudesta.
- Osaat arvioida tehon porttitason simuloinnin aktiivisuudesta.
- Osaat perustella, miksi kellon portitus tehdään salpaan perustuvalla
  ICG:llä eikä JA-portilla.
- Osaat kuvata tehoalueet, eristyksen ja tasonsiirron sekä UPF:n
  tehtävän.
