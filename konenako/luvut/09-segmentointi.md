# Segmentointi ja seuranta

**Segmentointi** jakaa kuvan alueisiin, joista kukin on yksi kappale tai
tausta. Kynnystys ja yhtenäiset alueet (luvut 2 ja 4) ovat yksinkertaisin
segmentointi, mutta ne eivät erota toisiaan koskettavia kappaleita.
**Seuranta** taas yhdistää saman kappaleen peräkkäisissä kuvissa ja
arvioi sen liikettä. Tässä luvussa erotellaan kosketuksissa olevat
kappaleet watershed-menetelmällä, mitataan liike optisella virtauksella
ja tasoitetaan kohinaista rataa Kalman-suotimella.

## Kosketuksissa olevat kappaleet: watershed

Kuusi kiekkoa, joista kaksi paria koskettaa toisiaan, tuottaa
kynnystyksen jälkeen vain neljä yhtenäistä aluetta.

```{.python tiedosto="esimerkit/09-watershed.py" osa="kuva"}
```

**Watershed** (vedenjakaja) tulkitsee kuvan maastoksi ja täyttää sitä
vedellä merkityistä lähteistä. Kun kahdesta lähteestä levinneet vedet
kohtaavat, niiden väliin rakennetaan pato. Menetelmä on vain niin hyvä
kuin sen lähteet eli **merkit** (*markers*). Kiekkojen keskustat
löydetään **etäisyysmuunnoksella**: jokaisen kohdepikselin arvo on
etäisyys lähimpään taustapikseliin, ja se on suurin kiekkojen keskellä.
Kosketuskohta on kapea, joten etäisyys on siinä pieni, ja kynnystys
erottaa keskustat toisistaan.

```{.python tiedosto="esimerkit/09-watershed.py" osa="watershed"}
```

```{.tuloste tiedosto="esimerkit/09-watershed.odotettu"}
```

![Kosketuksissa olevat kiekot, etäisyysmuunnos ja watershedin jako.
Mustat rajat ovat patoja.](kuvat/watershed.png){width=100%}

Etäisyysmuunnoksen kynnys on menetelmän herkkä kohta. Kynnyksellä 0,6
kertaa suurin etäisyys keskustat sulautuivat vielä pareittain, ja
tuloksena oli neljä aluetta. Kynnys 0,75 erottaa kaikki kuusi. Kun
kappaleet ovat eri kokoisia, yksi kynnys ei riitä, ja merkit haetaan
paikallisina maksimeina tai muulla tiedolla.

**GrabCut** on toinen klassinen menetelmä. Käyttäjä tai ilmaisin antaa
suorakaiteen kappaleen ympärille, ja menetelmä mallintaa etualan ja
taustan värijakaumat ja leikkaa kuvan graafileikkauksella. Se on
vuorovaikutteisten taustanpoistotyökalujen perusta. Nykyään yleisimmät
segmentoinnit ovat neuroverkkoja, ja luku 11 käsittelee niiden
rajapintaa.

## Optinen virtaus

**Optinen virtaus** on kuvan näennäinen liike pikselistä toiseen.
Perusoletus on, että pisteen kirkkaus säilyy liikkeessä:
$I(x + u, y + v, t + 1) = I(x, y, t)$. Taylorin kehitelmällä saadaan
**virtausyhtälö**

$$
I_x u + I_y v + I_t = 0,
$$

joka on yksi yhtälö kahdelle tuntemattomalle. **Lucas–Kanade** olettaa,
että liike on sama pienessä ikkunassa, ja ratkaisee $(u, v)$ ikkunan
kaikkien pikselien yhtälöistä pienimmällä neliösummalla. Ratkaisun
matriisi on luvun 5 rakennetensori: virtaus on luotettava juuri kulmissa,
joten seurattavat pisteet valitaan `goodFeaturesToTrack`-funktiolla.
**Kuvapyramidi** laajentaa menetelmän suuriin liikkeisiin: liike
arvioidaan ensin karkeasta, pienennetystä kuvasta ja tarkennetaan
tasolta toiselle.

Testissä teksturoitua kuvaa siirretään tunnetulla alipikseliliikkeellä.

```{.python tiedosto="esimerkit/09-virtaus.py" osa="kuvat"}
```

```{.python tiedosto="esimerkit/09-virtaus.py" osa="lk"}
```

```{.tuloste tiedosto="esimerkit/09-virtaus.odotettu"}
```

Mediaani on tärkeä yksityiskohta. Yksittäiset pisteet voivat seurata
väärin esimerkiksi kuvan reunalla tai toistuvassa tekstuurissa, ja
mediaani sietää ne, kun keskiarvo ei.

## Kalman-suodin seurannassa

Ilmaisin antaa kohteen sijainnin jokaisesta kuvasta, mutta mittaus on
kohinainen ja joskus puuttuu kokonaan, kun kohde peittyy. **Kalman-suodin**
yhdistää kaksi tietolähdettä: liikemallin ennusteen ja mittauksen. Kumpaakin
painotetaan sen epävarmuuden mukaan. Tila on $(x, y, v_x, v_y)$, ja
tasaisen nopeuden malli ennustaa seuraavan sijainnin nykyisestä
sijainnista ja nopeudesta.

Suotimella on kaksi vaihetta. **Ennuste** (`predict`) siirtää tilaa
mallin mukaan ja kasvattaa epävarmuutta prosessikohinan verran.
**Korjaus** (`correct`) yhdistää ennusteen ja mittauksen
Kalman-vahvistuksella, joka riippuu niiden kovariansseista. Kun mittaus
puuttuu, korjaus jätetään väliin, ja ennuste jatkaa yksin.

```{.python tiedosto="esimerkit/09-kalman.py" osa="malli"}
```

```{.python tiedosto="esimerkit/09-kalman.py" osa="seuranta"}
```

```{.tuloste tiedosto="esimerkit/09-kalman.odotettu"}
```

Suodin pienentää virheen alle puoleen mittausten virheestä ja kantaa
kohteen kymmenen kuvan peiton yli. Kovarianssit ovat suotimen säätönupit:
mittauskohina $R$ kertoo, kuinka paljon mittauksiin luotetaan, ja
prosessikohina $Q$, kuinka paljon kohde voi poiketa mallista. Liian pieni
$Q$ tekee suotimesta hitaan reagoimaan käännöksiin, liian suuri
kohinaisen. Taito *Todennäköisyys ja tilastot* antaa pohjan kovariansseille,
ja suodin on sama, jota käytetään navigoinnissa ja anturifuusiossa.

## Käytännössä

- **Panosta watershedin merkkeihin.** Menetelmä on vain niin hyvä kuin
  lähteensä. Etäisyysmuunnos toimii pyöreille kappaleille, muille
  tarvitaan muotoon sopivat merkit.
- **Seuraa kulmia, älä reunoja.** Lucas–Kanade tarvitsee gradientteja
  kahteen suuntaan. Valitse pisteet `goodFeaturesToTrack`-funktiolla
  ja hylkää ne, joiden tila (`status`) on nolla.
- **Käytä vankkoja tunnuslukuja.** Mediaani tai RANSAC liikkeen
  arviointiin; yksi väärin seurattu piste voi muuten viedä keskiarvon.
- **Säädä Kalman-suodin mitatuilla kohinoilla.** Mittauskohinan voi
  arvioida paikallaan olevasta kohteesta. Prosessikohina säädetään
  oikeilla radoilla, ei arvaamalla.
- **Erota havainto ja tila.** Seuranta tarvitsee tunnisteet, joilla
  havainnot liitetään radoille (esimerkiksi unkarilainen algoritmi
  etäisyysmatriisilla), sekä säännöt uusien ratojen aloittamiselle ja
  vanhojen lopettamiselle.

## Itsearviointi

- Osaat erottaa toisiaan koskettavat kappaleet etäisyysmuunnoksella ja
  watershedilla ja selittää merkkien merkityksen.
- Osaat johtaa virtausyhtälön ja selittää, miksi Lucas–Kanade tarvitsee
  ikkunan ja kulmapisteitä.
- Osaat mitata kuvan liikkeen pyramidimuotoisella Lucas–Kanadella ja
  arvioida sen vankasti.
- Osaat rakentaa tasaisen nopeuden Kalman-suotimen, käsitellä puuttuvat
  mittaukset ja selittää kovarianssien vaikutuksen.
