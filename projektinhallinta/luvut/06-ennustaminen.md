# Ennustaminen historiasta

Edellisen luvun arviot perustuivat siihen, mitä tekijät ajattelevat
työstä. Tässä luvussa ennuste rakennetaan siitä, mitä tiimi on
todella saanut aikaan. Menetelmä on Monte Carlo -simulointi: historiasta
arvotaan tuhansia mahdollisia tulevaisuuksia, ja tulos on jakauma, josta
valitaan haluttu varmuustaso. Luvun lopussa testataan, pitävätkö
varmuustasot paikkansa, ja verrataan pisteisiin ja kappalemääriin
perustuvia ennusteita.

## Läpäisy ennusteen pohjana

**Läpäisy** (*throughput*) on valmistuneiden töiden määrä aikayksikössä,
esimerkiksi viikossa. Se saadaan suoraan tehtävienhallinnasta
laskemalla, montako työtä siirtyi valmiiksi kullakin viikolla. Mitään
ei tarvitse arvioida.

Esimerkkitiimin 20 viikon historia on moduulissa `ennuste.py`. Läpäisy
vaihtelee nollasta kahdeksaan ja on keskimäärin 4,15 työtä viikossa.
Naiivi ennuste 60 työlle on 60 / 4,15 eli noin 15 viikkoa. Se on yksi
luku eikä kerro, kuinka varma se on.

Simulointi tekee saman laskun toisin. Yksi mahdollinen tulevaisuus
saadaan arpomalla jokaiselle tulevalle viikolle läpäisy historian
viikoista, kunnes työt on tehty. Kun tämä toistetaan kymmenentuhatta
kertaa, saadaan viikkomäärien jakauma.

```{.python tiedosto="esimerkit/ennuste.py" osa="ennuste"}
```

Moduulin oma pääohjelma tarkistaa rajatapauksen: tiimi, joka tekee
tasan yhden työn viikossa, tarvitsee kymmeneen työhön aina kymmenen
viikkoa.

```{.tuloste tiedosto="esimerkit/ennuste.odotettu"}
```

## Kaksi kysymystä

Ennusteelta kysytään käytännössä kahta asiaa: milloin tämä joukko töitä
on valmis, ja montako työtä ehtii valmistua tiettyyn päivään mennessä.

```{.python tiedosto="esimerkit/06-ennuste.py" osa="milloin"}
```

```{.python tiedosto="esimerkit/06-ennuste.py" osa="paljonko"}
```

```{.tuloste tiedosto="esimerkit/06-ennuste.odotettu"}
```

![Monte Carlo -ennusteen jakauma: viikko, jolla 60 työtä on valmiina.
Pystyviivat ovat 50, 85 ja 95 prosentin varmuustasot.](kuvat/ennuste.png){width=62%}

Tuloksen lukeminen vaatii huolellisuutta:

- ”85 %:n varmuudella viikolla 17” tarkoittaa, että 85 % simuloiduista
  tulevaisuuksista päättyi viikkoon 17 mennessä. Jäljelle jää 15 %:n
  mahdollisuus myöhästyä.
- Määräkysymyksessä varma lupaus haetaan jakauman alapäästä: 85 %:n
  varmuudella valmistuu *vähintään* 43 työtä, vaikka mediaani on 50.
- Varmuustason valinta on liiketoimintapäätös. Jos myöhästyminen maksaa
  sakon, valitaan 95 %. Jos kyse on sisäisestä suunnitelmasta, 70–85 %
  riittää. 50 %:n varmuudella annettu lupaus pettää joka toisella
  kerralla.

Viimeinen tulosrivi näyttää, että keskiarvosta laskettu 15 viikkoa
pitää noin kahdessa tapauksessa kolmesta. Luku on yli puolen vain
siksi, että 14,5 pyöristettiin ylöspäin.

## Pitävätkö varmuustasot

Ennusteen väite ”85 %” on testattavissa: kun samalla menetelmällä
tehdään monta ennustetta, 85 % niistä pitäisi toteutua. Tätä kutsutaan
kalibroinniksi. Oikeassa projektissa testi tehdään omalla historialla:
palataan menneisyyteen, tehdään ennuste sen hetken tiedoilla ja
verrataan siihen, mitä todella tapahtui.

Esimerkki tekee tämän keinotekoisella historialla, jotta toistoja
saadaan satoja. Joka viides viikko ennustetaan 40 työn valmistuminen
edellisten 20 viikon perusteella.

```{.python tiedosto="esimerkit/06-takautuva.py" osa="testi"}
```

Testi ajetaan kahdelle prosessille. Vakaan tiimin läpäisy vaihtelee
satunnaisesti saman keskiarvon ympärillä. Muuttuvasta tiimistä
kolmannes on poissa puolet ajasta.

```{.python tiedosto="esimerkit/06-takautuva.py" osa="prosessit"}
```

```{.tuloste tiedosto="esimerkit/06-takautuva.odotettu"}
```

Vakaalla tiimillä varmuustasot pitävät: 85 %:n ennuste toteutuu 88
prosentissa ja 95 %:n ennuste 95 prosentissa tapauksista. Keskiarvoon
perustuva luku pitää alle puolessa.

Muuttuvalla tiimillä samat ennusteet pitävät enää 77 ja 85 prosentissa
tapauksista. Menetelmä ei mennyt rikki, vaan sen oletus petti: se
olettaa, että tuleva muistuttaa historiaa. Kun tiimin koko, työn laatu
tai ympäristö muuttuu, historia ei enää edusta tulevaa. Tämä koskee
kaikkia ennustemenetelmiä, myös asiantuntija-arvioita, mutta
simuloinnissa oletus on ainakin näkyvissä.

## Tarinapisteet vai kappalemäärä

Edellä ennuste laski töitä kappaleina välittämättä niiden koosta. Onko
se perusteltua, vai pitäisikö työt painottaa arvioidulla koolla? Tästä
on kiistelty nimellä **#NoEstimates**. Liikkeen väite on, että
kappalemäärään perustuva ennuste on yhtä hyvä kuin pisteisiin
perustuva, jolloin arviointiin käytetty aika on hukkaa. Vastaväite on,
että työt eivät ole samankokoisia ja koon sivuuttaminen hukkaa tietoa.

Kumpikin voi olla oikeassa, ja ratkaisevan ehdon voi näyttää
simuloimalla. Tiimi tekee töitä, joiden arvioitu koko on 1–8 pistettä
ja joiden todellinen työmäärä hajoaa arvion ympärille.

```{.python tiedosto="esimerkit/06-pisteet.py" osa="tyot"}
```

Jäljellä olevien 60 työn kesto ennustetaan 20 viikon historiasta
kahdella tavalla, ja ennustetta verrataan toteumaan:

```{.python tiedosto="esimerkit/06-pisteet.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/06-pisteet.odotettu"}
```

Tuloksen kolme riviä kertovat kolme eri tarinaa:

1. Kun jäljellä olevat työt ovat samanlaista sekoitusta kuin tehdyt,
   menetelmät ovat lähes yhtä hyviä (virhe 9 % ja 12 %). Suuret ja
   pienet työt tasaavat toisensa, eikä kokoarvio tuo juuri lisää.
2. Kun jäljellä on vain suuria töitä, kappalemäärä erehtyy pahasti (42
   %), koska se olettaa töiden olevan keskikokoisia. Pisteet korjaavat
   tämän, jos arviot kertovat todellisesta koosta jotain.
3. Jos arviot eivät osu, pisteistä ei ole apua silloinkaan.

Johtopäätös ei ole, että arviointi olisi turhaa tai välttämätöntä.
Kappalemäärään perustuva ennuste toimii, kun työt pilkotaan suunnilleen
samankokoisiksi tai kun tuleva työ on samaa sekoitusta kuin mennyt.
Näistä ensimmäinen on tiimin omissa käsissä: jos jokainen työ pilkotaan
enintään muutaman päivän mittaiseksi, kokoarvioksi riittää kysymys
”onko tämä tarpeeksi pieni”. Jos taas edessä on selvästi erilaista
työtä kuin takana, koko on otettava huomioon tavalla tai toisella.
Arvioinnin toinen hyöty, yhteisen ymmärryksen syntyminen (luku 5), ei
riipu ennusteen tarkkuudesta lainkaan.

## Ennusteen rajat

Monte Carlo -ennuste on vain niin hyvä kuin sen oletukset:

- **Historia edustaa tulevaa.** Lomakausi, uusi tiimin jäsen tai uusi
  tekniikka muuttavat läpäisyä. Käytä tuoretta historiaa (2–3 kuukautta)
  ja päivitä ennuste viikoittain.
- **Työn määrä tiedetään.** Ennuste koskee tunnettua työjoukkoa.
  Projektin aikana löytyy uutta työtä, ja sen voi ottaa mukaan
  kasvattamalla työmäärää historian mukaisella osuudella (jos jonoon on
  tullut 20 % lisää joka kuukausi, niin tulee jatkossakin).
- **Viikot ovat riippumattomia.** Arvonta olettaa, että huono viikko ei
  ennusta seuraavaa huonoa. Jos tiimi on jumissa saman ongelman kanssa
  kolme viikkoa, todellinen hajonta on simuloitua suurempi.
- **Työt ovat valmiita, kun ne lasketaan.** Jos ”valmis” ei tarkoita
  julkaistavaa, läpäisy mittaa väärää asiaa.

Ennuste ei myöskään korvaa ajattelua. Jos kriittinen riippuvuus
(toimittaja, viranomaispäätös, laitetoimitus) määrää valmistumisen,
läpäisyyn perustuva ennuste on merkityksetön. Silloin tarvitaan luvun
5 tehtäväverkkoa ja luvun 8 riskitarkastelua.

## Käytännössä

- **Kerää läpäisy ja läpimenoajat heti.** Tieto on jo
  tehtävienhallinnassa. Muutaman viikon historia riittää ensimmäiseen
  ennusteeseen, ja se on parempi kuin ei mitään.
- **Kerro ennuste varmuustasoineen.** ”85 %:n varmuudella viikolla 17,
  todennäköisimmin viikolla 15” antaa kuulijalle sekä odotuksen että
  riskin.
- **Päivitä ennuste säännöllisesti ja näytä sen muutos.** Ennuste, joka
  siirtyy joka viikko viikolla eteenpäin, on tärkein yksittäinen
  varoitusmerkki.
- **Testaa ennusteesi takautuvasti.** Jos 85 %:n ennusteesi ovat
  pitäneet 60 %:n osuudella, tiedät, paljonko niihin pitää lisätä.
- **Pilko työt samankokoisiksi.** Se parantaa virtausta, pienentää
  riskiä ja tekee kappalemäärään perustuvasta ennusteesta pätevän.
- **Älä piiloudu mallin taakse.** Kun tiedät jotain, mitä historia ei
  tiedä (puolet tiimistä lomalla, suuri integraatio edessä), sano se ja
  säädä ennustetta.

## Itsearviointi

- Osaat selittää, miten Monte Carlo -ennuste rakennetaan
  läpäisyhistoriasta ja mitä sen varmuustasot tarkoittavat.
- Osaat vastata ennusteella sekä kysymykseen ”milloin” että kysymykseen
  ”montako” ja tiedät, kummasta päästä jakaumaa varma lupaus luetaan.
- Osaat kuvata takautuvan testin ja selittää, miksi ennuste pettää, kun
  tiimi tai työ muuttuu.
- Osaat kertoa, millä ehdoilla kappalemäärään perustuva ennuste on yhtä
  hyvä kuin kokoarvioihin perustuva.
- Osaat luetella ennusteen oletukset ja tunnistaa tilanteen, jossa
  läpäisyyn perustuva ennuste ei sovi.
