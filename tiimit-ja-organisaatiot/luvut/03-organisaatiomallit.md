# Organisaatiomallit ja luovutukset

Conwayn laki kertoo, että rakenteella on väliä. Tämä luku käy läpi
rakenteet, joista useimmat organisaatiot ovat lähteneet liikkeelle, ja
laskee, mistä luovutusten hinta oikeasti tulee.

## Neljä perusmallia

Organisaatio ryhmittelee ihmiset jonkin perusteen mukaan, ja peruste
kertoo, mitä optimoidaan.

| Malli | Ryhmittelyperuste | Vahvuus | Heikkous |
|--------------|----------------|--------------------|---------------------|
| funktionaalinen | osaaminen | syvä erikoisosaaminen, tasainen kuorma | työ kulkee osastolta toiselle |
| projekti | toimitus | selkeä tavoite ja vastuu | osaaminen hajoaa projektin jälkeen |
| matriisi | molemmat | joustava resursointi | kaksi esihenkilöä, ristiriitaiset prioriteetit |
| tuote | tuote tai asiakasvirta | nopea palaute, pysyvä omistajuus | päällekkäistä tekemistä, yhtenäisyys vaatii työtä |

```{.dot otsikko="Funktionaalisessa mallissa muutos kulkee osastojen läpi, tuotemallissa tiimi vie sen alusta loppuun"}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.35;
  subgraph cluster_f { label="funktionaalinen"; style=dashed;
    f1 [label="määrittely"]; f2 [label="kehitys"];
    f3 [label="testaus"]; f4 [label="ylläpito"];
    f1 -> f2 -> f3 -> f4 [label="jono"]; }
  subgraph cluster_t { label="tuote"; style=dashed;
    t1 [label="tiimi A\nmäärittely, kehitys,\ntestaus, tuotanto"];
    t2 [label="tiimi B\nmäärittely, kehitys,\ntestaus, tuotanto"];
    t1 -> t2 [style=invis]; }
}
```

**Funktionaalisessa** organisaatiossa ovat käyttöliittymäkehittäjät
yhdessä, tietokanta-asiantuntijat yhdessä, testaajat yhdessä ja ylläpito
yhdessä. Erikoisosaaja oppii muilta saman alan ihmisiltä, ja harvinaista
osaamista riittää kaikille. Hinta on, ettei kukaan omista kokonaista
muutosta: se kulkee osastolta toiselle, ja jokaisella osastolla on oma
jononsa ja omat prioriteettinsa.

**Projektiorganisaatio** kokoaa ihmiset toimituksen ajaksi ja purkaa
ryhmän sen jälkeen. Tavoite on selkeä, mutta tiimi ei ehdi hioutua
yhteen ennen hajoamistaan, eikä kukaan jää omistamaan lopputulosta
(ks. *Ohjelmistoprojektin hallinta*).

**Matriisissa** ihmisellä on linjaesihenkilö osaamisen mukaan ja
projektipäällikkö työn mukaan. Malli yrittää saada kummankin edut,
ja sen tavallisin oire on ihminen, joka on ”30 % kolmessa
projektissa”. Tehtävien vaihtaminen maksaa, ja jokainen projekti
odottaa vuoroaan.

**Tuoteorganisaatiossa** pysyvä, monitaitoinen tiimi omistaa tuotteen
tai sen osan alusta tuotantoon. Mallin hinta on päinvastainen kuin
funktionaalisen: tiimit ratkaisevat samoja ongelmia eri tavoin, ja
harvinainen erikoisosaaminen jää ohueksi, ellei sitä tueta erikseen
(luku 4).


## Komponenttitiimit ja ominaisuustiimit

Sama jännite toistuu kehitystiimien sisällä. **Komponenttitiimi**
omistaa teknisen osan, kuten käyttöliittymän, rajapintakerroksen tai
tietokannan. **Ominaisuustiimi** (*feature team*) toteuttaa asiakkaalle
näkyvän ominaisuuden kaikkien kerrosten läpi. Johdannon kerrosjako on
komponenttitiimien malli ja ominaisuusjako ominaisuustiimien.

Komponenttitiimeissä koodin omistajuus on selkeä ja laatu yhden osan
sisällä yleensä hyvä. Asiakkaan näkemä ominaisuus vaatii kuitenkin
usean tiimin työn, joten joku joutuu sovittamaan tiimien työjonot
yhteen, ja valmista syntyy hitaimman tiimin tahtiin. Ominaisuustiimeissä
ominaisuus valmistuu yhden tiimin sisällä, mutta sama komponentti on
usean tiimin käsissä, mikä vaatii yhteisiä käytäntöjä ja hyvää
testiautomaatiota.

## Mistä luovutuksen hinta tulee

**Luovutus** (*hand-off*) on kohta, jossa työ siirtyy tiimiltä
toiselle. Usein sanotaan, että luovutukset ovat hitaita. Tarkempi
väite on, että hitaus tulee odottamisesta, ei erikoistumisesta.
Lasketaan tämä jonomallilla.

Sama työ tehdään kahdella tavalla, kummassakin kaksitoista henkeä ja
sama 80 %:n kuormitusaste. Jokaisessa työssä on kolme vaihetta, joista
kukin kestää keskimäärin päivän. Jonon ydin on sama molemmissa:

```{.python tiedosto="esimerkit/03-luovutukset.py" osa="jono"}
```

Erikoistiimien mallissa työ kulkee kolmen neljän hengen tiimin läpi.
Seuraava tiimi ei aina ota työtä vastaan heti, vaan vasta kun se käy
työjononsa läpi. Ominaisuustiimien mallissa neljä kolmen hengen
tiimiä vie kukin omat työnsä alusta loppuun:

```{.python tiedosto="esimerkit/03-luovutukset.py" osa="mallit"}
```

```{.tuloste tiedosto="esimerkit/03-luovutukset.odotettu"}
```

Tulos on vivahteikkaampi kuin iskulause ”luovutukset pois”.

- **Kitkaton luovutus ei maksa mitään.** Kun työ siirtyy heti
  seuraavan tiimin jonoon, erikoistiimien ketju on lähes yhtä nopea kuin
  ominaisuustiimit. Neljän hengen yhteinen jono jopa tasaa kuormaa:
  hitaimmat työt valmistuvat nopeammin kuin erillisissä jonoissa.
- **Odotus luovutuksessa maksaa paljon.** Jos vastaanottava tiimi
  ottaa uudet työt jonoonsa kerran viikossa, läpimenoaika yli
  kaksinkertaistuu ja virtaustehokkuus putoaa alle neljännekseen:
  työ odottaa kolme neljäsosaa ajastaan. Viikoittainen suunnittelu,
  tikettijono ja ”katsotaan ensi sprintissä” ovat juuri tätä.
- **Monitaitoisuus ei ole ilmaista.** Jos yleisosaaja on 15 %
  hitaampi kuin erikoisosaaja, sama työmäärä nostaa kuormitusasteen
  yli 90 %:n ja jono kasvaa jyrkästi (ks. *Ohjelmistoprojektin
  hallinta*, virtaus). Ominaisuustiimit tarvitsevat tällöin enemmän
  väljyyttä.

![Läpimenoajan keskiarvo viidellä tavalla järjestää sama työ.
Erikoistiimien hinta tulee odotuksesta, ominaisuustiimien hitaammasta
työstä.](kuvat/luovutukset.png){width=55%}

Malli jättää pois asioita, jotka käytännössä painavat vaakaa
ominaisuustiimien suuntaan: tieto katoaa luovutuksessa ja tuottaa
uudelleentyötä, tiimien prioriteetit ovat ristiriidassa, eikä kukaan
näe kokonaista muutosta. Se jättää pois myös asioita, jotka painavat
toiseen suuntaan: harvinaista osaamista ei riitä joka tiimiin, ja
yhtenäisyys kärsii. Mallin opetus on mitata sitä, kuinka kauan työ
odottaa rajalla.

## Siilot

**Siilo** on ryhmä, joka optimoi omaa tulostaan kokonaisuuden
kustannuksella. Siilo ei synny erikoistumisesta vaan kannustimista:
kun kehitystä mitataan ominaisuuksien määrällä ja ylläpitoa
häiriöttömyydellä, toisen onnistuminen on toisen ongelma (luku 7).
Tunnusmerkkejä ovat tikettijono ainoana viestintäkanavana, ”meidän
osuutemme on valmis” ja se, ettei kukaan osaa kertoa, kauanko muutos
kokonaisuutena kestää.

Siiloja ei pureta organisaatiokaaviota muuttamalla, jos tavoitteet ja
mittarit pysyvät ennallaan. Yhteinen tavoite koko arvovirralle ja
läpimenoajan mittaaminen päästä päähän vaikuttavat enemmän.

## Käytännössä

- **Kysy, mitä rakenne optimoi.** Funktionaalinen malli optimoi
  osaamisen käyttöastetta, tuotemalli läpimenoaikaa. Pienessä
  yrityksessä ainoaa tietoturva-asiantuntijaa ei voi jakaa viiteen
  tiimiin.
- **Mittaa odotus rajalla.** Kirjaa, milloin työ oli valmis
  luovutettavaksi ja milloin se aloitettiin.
- **Lyhennä ottoväliä ennen kuin siirrät ihmisiä.** Päivittäinen
  työjonon läpikäynti voi puolittaa läpimenoajan ilman
  organisaatiomuutosta.

## Itsearviointi

- Osaat kuvata neljä organisaatiomallia ja kertoa, mitä kukin optimoi.
- Osaat verrata komponentti- ja ominaisuustiimejä ja nimetä kummankin
  hinnan.
- Osaat selittää jonomallilla, miksi luovutuksen hinta tulee odotuksesta.
- Osaat tunnistaa siilon ja perustella, miksi pelkkä kaavion muutos ei
  pura sitä.
