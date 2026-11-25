# Kantataajuus ja kaistanpäästö

Radiosignaali on reaalinen jännite, joka värähtelee kantoaallon
taajuudella $f_c$: WLAN 2,4 tai 5 GHz:llä, matkapuhelin noin 0,7–3,5
GHz:llä. Tieto ei kuitenkaan ole kantoaallossa vaan sen hitaissa
muutoksissa: amplitudissa ja vaiheessa. Siksi lähes kaikki
tiedonsiirron laskenta tehdään **kantataajuudella**, jossa kantoaalto on
poistettu ja signaali esitetään kompleksilukujen jonona. Tämä luku
näyttää, miksi esitys on tarkka eikä vain kätevä, ja miten siitä
siirrytään kaistanpäästösignaaliin ja takaisin.

## IQ-esitys

Mikä tahansa kapeakaistainen reaalinen signaali voidaan kirjoittaa
muodossa

$$s(t) = I(t)\cos(2\pi f_c t) - Q(t)\sin(2\pi f_c t)
       = \operatorname{Re}\{x(t)\,e^{i 2\pi f_c t}\},$$

missä $x(t) = I(t) + iQ(t)$ on **kompleksinen verhokäyrä** eli
kantataajuussignaali. $I$ on samavaiheinen (*in-phase*) ja $Q$
kvadratuurikomponentti: ne moduloivat kahta kantoaaltoa, jotka ovat 90
astetta eri vaiheessa ja siksi toisistaan erotettavissa. Lähetin
tarvitsee kaksi sekoitinta ja kaksi D/A-muunninta, ja vastaanotin
kaksi sekoitinta ja kaksi A/D-muunninta.

```{.python tiedosto="esimerkit/02-sekoitus.py" osa="ylos"}
```

Kantataajuussignaalin spektri on mitä tahansa, eikä se ole
symmetrinen, koska signaali on kompleksinen. Reaalisen
kaistanpäästösignaalin spektri on aina symmetrinen: kantataajuuden
spektri siirtyy taajuudelle $+f_c$ ja sen peilikuva taajuudelle $-f_c$.

```{.python tiedosto="esimerkit/02-sekoitus.py" osa="spektri"}
```

## Sekoitus alas

Vastaanotin kertoo signaalin paikallisen oskillaattorin
kompleksikonjugaatilla $2e^{-i2\pi f_c t}$. Tulossa on haluttu
kantataajuussignaali ja kopio taajuudella $-2f_c$, joka poistetaan
alipäästösuotimella. Käytännössä kerrotaan erikseen kosinilla ja
sinillä, mikä on sama asia kahtena reaalihaarana.

```{.python tiedosto="esimerkit/02-sekoitus.py" osa="alas"}
```

Verhokäyrä on kantataajuussignaalin itseisarvo, ja sen saa myös
suoraan kaistanpäästösignaalista analyyttisen signaalin avulla
(Hilbert-muunnos). Teho puolittuu kaistalle siirryttäessä, koska
kosinin neliön keskiarvo on 1/2.

```{.python tiedosto="esimerkit/02-sekoitus.py" osa="verho"}
```

```{.tuloste tiedosto="esimerkit/02-sekoitus.odotettu"}
```

Suurin virhe 0,009 johtuu alipäästösuotimen siirtymäkaistasta ja
reunoista, ei menetelmästä. Kantataajuusmalli on siis tarkka:
kaistanpäästösignaalin kaikki tieto on kompleksisessa verhokäyrässä,
ja kaikki lineaariset operaatiot (suodatus, kanava, sovitettu suodin)
voi laskea kantataajuudella. Siksi tutoriaalin muut luvut toimivat
kantataajuudella. Näytetaajuuden riittää olla verhokäyrän kaistan
luokkaa, ei kantoaallon kaksinkertainen.

## Miksi kompleksinen? Peilikuva

Jos vastaanotin käyttää vain yhtä sekoitinta, se ei erota
oskillaattorin ylä- ja alapuolella olevia taajuuksia toisistaan:
molemmat päätyvät samalle välitaajuudelle. Tämä on **peilitaajuus**
(*image*). Kompleksinen sekoitus erottaa ne, koska positiivinen ja
negatiivinen taajuus ovat kantataajuudella eri asioita.

```{.python tiedosto="esimerkit/02-kuva.py" osa="kuva"}
```

```{.tuloste tiedosto="esimerkit/02-kuva.odotettu"}
```

Reaalisessa sekoituksessa haluttu 210 kHz:n ja häiritsevä 190 kHz:n
signaali tuottavat täsmälleen saman tuloksen. IQ-sekoituksessa ne
päätyvät eri puolille nollataajuutta. Superheterodyynivastaanotin
poistaa peilitaajuuden suotimella ennen sekoitusta. Suoramuunnos- ja
nollavälitaajuusvastaanotin (*zero-IF*), jota ohjelmistoradiot ja
matkapuhelimet käyttävät, luottaa IQ-haarojen tasapainoon. Jos haarojen
vahvistus tai vaihe eroaa (*IQ-epätasapaino*), peilikuva vuotaa
osittain läpi. Taito *Ohjelmistoradio* käsittelee sen korjaamisen.

## Käytännössä

- **Simuloi kantataajuudella.** Kantoaalto lisätään vain, kun
  tutkitaan nimenomaan radioteknisiä ilmiöitä, kuten peilitaajuutta
  tai epälineaarisuutta. Näytetaajuuden tarve putoaa
  gigahertseistä megahertseihin.
- **Muista tehon kerroin.** Reaalisen kaistanpäästösignaalin teho on
  puolet verhokäyrän tehosta. Sekoittajan kerroin 2 palauttaa
  amplitudin. Väärä kerroin on tyypillinen 3 dB:n virhe linkkibudjetissa.
- **Kantataajuussignaali on kompleksinen.** Sen spektri ei ole
  symmetrinen, joten FFT:n negatiiviset taajuudet ovat oikeaa tietoa,
  eivät peilikuvaa. Piirrä spektri `fftshift`-funktion avulla.
- **Taajuusvirhe on kantataajuudella kierto.** Jos vastaanottimen
  oskillaattori on $\Delta f$ väärässä, kantataajuussignaali kerrotaan
  tekijällä $e^{i2\pi\Delta f t}$ (luku 7).

## Itsearviointi

- Osaat kirjoittaa kaistanpäästösignaalin kompleksisen verhokäyrän
  avulla ja selittää I- ja Q-komponentit.
- Osaat sekoittaa signaalin kantataajuudelta kantoaallolle ja takaisin
  sekä perustella alipäästösuotimen tarpeen.
- Osaat selittää, miksi kantataajuinen simulaatio on tarkka kaikille
  lineaarisille operaatioille.
- Osaat selittää peilitaajuuden ja sen, miksi IQ-sekoitus erottaa
  positiiviset ja negatiiviset taajuudet.
