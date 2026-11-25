# Ihmiset ja viestintä

Ohjelmiston tekevät ihmiset, ja projektin vaikeimmat ongelmat ovat
harvoin teknisiä. DeMarcon ja Listerin *Peopleware* aloittaa juuri tällä
väitteellä: hankkeet epäonnistuvat useammin sosiaalisista kuin
teknisistä syistä. Tämä luku käsittelee sidosryhmäviestintää,
tilanneraportointia, palavereita, retrospektiiveja, tiimin kokoa ja
perehdytystä sekä sitä, mitä versionhallinnan historiasta voi ja ei voi
mitata.

## Sidosryhmäviestintä

Sidosryhmät (luku 2) tarvitsevat eri tietoa eri tiheydellä. Yksinkertainen
jäsennys sijoittaa heidät kahdelle akselille: kuinka paljon heillä on
valtaa hankkeeseen ja kuinka kiinnostuneita he siitä ovat.

| Sidosryhmä | Tarve | Tapa |
|----------------------|------------------------------------|------------------------------------|
| paljon valtaa, kiinnostunut (tilaaja, tuoteomistaja) | päätökset ja suunta | tiivis yhteistyö, viikoittain tai päivittäin |
| paljon valtaa, vähän aikaa (johto, ohjausryhmä) | ennuste, riskit, päätöspyynnöt | lyhyt säännöllinen raportti |
| vähän valtaa, kiinnostunut (käyttäjät, tuki) | mitä on tulossa ja milloin | katselmukset, julkaisutiedotteet |
| vähän valtaa, vähän kiinnostusta | tieto muutoksista, jotka koskevat heitä | tiedote tarvittaessa |

Viestinnän perussääntö on kertoa ensin se, mitä vastaanottajan pitää
tehdä tai päättää, ja vasta sitten taustat. Ohjausryhmä ei tarvitse
luetteloa tehdyistä tehtävistä vaan vastauksen kolmeen kysymykseen:
valmistuuko tämä, mikä sitä uhkaa ja mitä teidän pitää päättää.

## Rehellinen tilanneraportti

Liikennevaloraportti (vihreä, keltainen, punainen) on yleinen ja
helposti harhaanjohtava. Tunnettu vika on **vesimeloniraportti**:
ulkoa vihreä, sisältä punainen. Jokainen taso pyöristää tilannetta
vähän parempaan päin, ja ylimmälle tasolle asti päässyt raportti on
vihreä siihen asti, kun projekti yhtäkkiä onkin kuukausia myöhässä.

Vastalääke on raportoida havaintoja eikä mielipiteitä:

- **Toimiva ohjelmisto.** Katselmuksessa näytetty ominaisuus on
  kiistaton tosiasia. ”80 % valmis” ei ole.
- **Ennuste varmuustasoineen** (luku 6) ja sen muutos edellisestä:
  ”85 %:n varmuudella viikolla 17; viime kuussa viikolla 15”.
- **Laajuuden muutos.** Kertymäkaavio (*burnup*), jossa näkyvät sekä
  valmis työ että kokonaislaajuus, paljastaa, onko myöhästymisen syy
  hidas eteneminen vai kasvava työmäärä.
- **Suurimmat riskit ja niiden muutos** (luku 8).
- **Avoimet päätökset** ja päivä, johon mennessä ne tarvitaan.

Huonot uutiset kerrotaan heti. Viikon myöhästyminen, josta kerrotaan
kaksi kuukautta etukäteen, on suunnittelukysymys. Sama myöhästyminen
julkaisua edeltävänä päivänä on luottamuskriisi. Tämä edellyttää, että
huonojen uutisten tuoja ei joudu rangaistuksi, mihin palataan alla.

## Palaverit

Palaveri on kallis: kahdeksan hengen tunti on työpäivä. Se on
perusteltu, kun tarvitaan keskustelua, päätöstä tai yhteistä
ymmärrystä. Tiedon jakamiseen riittää useimmiten kirjoitettu viesti.

Hyvän palaverin tuntomerkit ovat samat menetelmästä riippumatta:
tarkoitus on sanottu etukäteen, paikalla ovat ne, joita asia koskee,
aika on rajattu ja lopputulos (päätös, tehtävä, omistaja) kirjataan.
Ketterien menetelmien tapahtumat (luku 4) ovat palavereita, joille
nämä asiat on määritelty valmiiksi.

Päivittäinen lyhyt tapaaminen on yleisin ja helpoimmin pilattava. Sen
tarkoitus on, että tiimi sopii päivän työstä: mikä on jumissa, kuka
auttaa ketä. Hyvä tapa on käydä taulu läpi oikealta vasemmalle, lähinnä
valmistumista olevasta työstä alkaen, eikä henkilö kerrallaan.
Jälkimmäinen muuttuu helposti vuorotellen annettavaksi tilanneraportiksi.

## Retrospektiivi

Retrospektiivi on säännöllinen tapaaminen, jossa tiimi tarkastelee
omaa työtapaansa ja päättää, mitä muutetaan. Se on jatkuvan
parantamisen moottori: ilman sitä samat ongelmat toistuvat.

Esther Derbyn ja Diana Larsenin rakenne jakaa tapaamisen viiteen
vaiheeseen:

1. **Avaus:** tarkoitus ja pelisäännöt.
2. **Tiedon keruu:** mitä jakson aikana tapahtui. Mittarit (luku 7) ja
   tapahtumien aikajana pitävät keskustelun tosiasioissa.
3. **Oivallukset:** miksi asiat menivät niin kuin menivät.
4. **Päätökset:** yksi tai kaksi konkreettista kokeilua seuraavalle
   jaksolle, jokaisella omistaja.
5. **Lopetus:** miten tapaaminen itse toimi.

Yleisin vika on, että vaiheet 1–3 tehdään ja 4 jää väliin, jolloin
tapaaminen on purkautumista ilman seurauksia. Toinen on, että päätetään
kymmenen asiaa, joista yksikään ei toteudu. Yksi muutos, joka oikeasti
tehdään ja jonka vaikutus tarkistetaan seuraavalla kerralla, on parempi.

Norman Kerth muotoili retrospektiivin lähtökohdaksi oletuksen, että
jokainen teki parhaansa silloisten tietojen, taitojen ja resurssien
puitteissa. Oletus ei ole naiivi vaan käytännöllinen: syyllisen etsiminen
tyrehdyttää tiedon, jota parantamiseen tarvitaan.

## Psykologinen turvallisuus

Amy Edmondson määritteli **psykologisen turvallisuuden** tiimin
jäsenten yhteiseksi käsitykseksi siitä, että tiimissä on turvallista
ottaa henkilökohtaisia riskejä: kysyä, myöntää virhe, olla eri mieltä.
Hänen tutkimuksensa sairaalatiimeistä tuotti aluksi yllättävän
tuloksen: parhaat tiimit raportoivat eniten virheitä. Ne eivät tehneet
niitä enemmän, vaan niissä virheistä uskallettiin puhua.

Projektinhallinnan kannalta tämä on tiedonkulun edellytys. Rehellinen
tilanneraportti, toimiva retrospektiivi, riskien tunnistaminen ja
realistinen arvio vaativat kaikki, että ikävän asian voi sanoa ääneen.
Jos arvion antaja tietää, että ”liian suuri” luku johtaa
painostukseen, hän antaa toivotun luvun, ja suunnitelma rakentuu sen
varaan.

Turvallisuus ei tarkoita, ettei vaadita mitään. Edmondsonin mukaan
oppiminen vaatii sekä turvallisuutta että korkeita tavoitteita.
Käytännön tekoja ovat esimerkiksi virheiden käsittely syyllistämättä
(tapahtuman jälkiselvitys kysyy, miten järjestelmä salli virheen, eikä
kuka sen teki), esihenkilön omien virheiden myöntäminen ja kysymysten
kiittäminen.

## Tiimin koko ja Brooksin laki

Fred Brooks havaitsi IBM:n OS/360-hankkeessa säännön, joka tunnetaan
hänen nimellään: lisäväen tuominen myöhässä olevaan ohjelmistoprojektiin
myöhästyttää sitä lisää. Syitä on kolme. Uusi tekijä on aluksi
tuottamaton, hänen perehdyttämisensä vie kokeneiden aikaa, ja
yhteydenpidon tarve kasvaa nopeammin kuin tiimi.

Viimeinen on laskettavissa. Jos jokaisen pitää voida sopia asioista
jokaisen kanssa, viestintäpolkuja on $n(n-1)/2$:

```{.python tiedosto="esimerkit/09-brooks.py" osa="polut"}
```

Malli yhdistää kolme tekijää. Jäljellä on 80 henkilötyöviikkoa, tiimissä
on viisi henkeä, uusi tekijä pääsee täyteen tehoon kahdeksassa viikossa
ja vie sinä aikana puolet yhden kokeneen ajasta.

```{.python tiedosto="esimerkit/09-brooks.py" osa="malli"}
```

```{.tuloste tiedosto="esimerkit/09-brooks.odotettu"}
```

Tiimi valmistuisi yksinään viikolla 16,7. Kolme lisätekijää heti alussa
aikaistaa valmistumista lähes kolme viikkoa. Viikolla 8 tuotuina he
eivät enää auta, ja viikolla 10 tai myöhemmin tuotuina he myöhästyttävät
projektia: perehdytyksen hinta maksetaan heti, mutta hyöty ei ehdi
toteutua ennen kuin työ on tehty. Laki ei siis sano, ettei väkeä saa
lisätä, vaan että lisäys on tehtävä ajoissa.

Viestintäpolkujen kasvu selittää myös, miksi tiimit pidetään pieninä.
Viiden hengen tiimissä polkuja on 10, kahdentoista hengen tiimissä 66.
Scrumin enintään kymmenen hengen suositus (luku 4) perustuu tähän.
Suuremmat kokonaisuudet jaetaan useaksi tiimiksi, ja niiden välinen
rajapinta on silloin suunniteltava. Se on taidon *Tiimit ja
organisaatiomallit* aihe.

Mallin parametrit ovat taas havainnollisia. Brooks itse huomauttaa,
että laki on karkea yksinkertaistus: jos työ on helposti jaettavissa
eikä vaadi perehdytystä, lisäväki auttaa. Ohjelmistotyö on harvoin
sellaista.

## Perehdytys ja tiedon jakaminen

Mallin perehdytysaika on tiimin omissa käsissä. Sitä lyhentävät
toimiva kehitysympäristö, jonka saa käyntiin yhdellä komennolla,
ajantasainen dokumentaatio (*Tekninen dokumentaatio*), automaattiset
testit, joiden turvin uusi tekijä uskaltaa muuttaa koodia, sekä
ensimmäinen pieni tehtävä, joka viedään tuotantoon asti ensimmäisellä
viikolla.

Sama asia kääntäen on **bussikerroin**: kuinka monen ihmisen
poistuminen pysäyttäisi työn. Jos vain yksi ihminen osaa julkaisun tai
tuntee laskutusmoduulin, kerroin on yksi. Sitä kasvatetaan
pariohjelmoinnilla, katselmoinnilla, tehtävien kierrättämisellä ja
kirjoittamalla asiat ylös. Luvun 8 avainhenkilöriski on tämän
toteutuma.

## Kestävä tahti ja keskeytykset

Ylityö tuottaa lyhyen pyrähdyksen ja sen jälkeen laskun. Väsynyt
tekijä tekee virheitä, joiden korjaaminen vie enemmän kuin ylityö
tuotti. Ketterän julistuksen periaate kestävästä tahdista ja XP:n
vastaava käytäntö perustuvat tähän kokemukseen.

Keskittymistä vaativa työ kärsii keskeytyksistä. DeMarco ja Lister
kuvaavat, kuinka syvään keskittymiseen pääseminen vie aikaa ja
jokainen keskeytys aloittaa laskennan alusta. Luvun 7 simulaatio
mallinsi saman asian tehtävien vaihtona. Käytännön keinoja ovat
keskeytyksettömät jaksot kalenterissa, yksi vuorollaan päivystävä
henkilö, joka ottaa vastaan kyselyt, ja kirjoitettu viestintä, johon
voi vastata omaan tahtiin.

Hajautetussa ja etätyössä kirjoitetun viestinnän merkitys kasvaa.
Päätökset ja niiden perustelut kirjataan paikkaan, josta ne löytyvät,
koska käytäväkeskustelua ei ole. Aikavyöhykkeiden yli toimiva tiimi
sopii yhteisen ajan synkroniselle työlle ja tekee muun asynkronisesti.

## Mittarit versionhallinnasta

Versionhallinnan historia on valmis tietolähde. Siitä saa muutosten
koon ja tiheyden sekä, jos tehtävätunnus on muutoksen kuvauksessa,
tehtävän kiertoajan. Esimerkki luo ensin pienen repositorion, jotta
tulos on toistettava, ja lukee sitten historian komennolla `git log`:

```{.python tiedosto="esimerkit/09-mittarit.py" osa="loki"}
```

```{.python tiedosto="esimerkit/09-mittarit.py" osa="mittarit"}
```

```{.tuloste tiedosto="esimerkit/09-mittarit.odotettu"}
```

Tuloksesta nousee esiin tehtävä T-3: 20 päivän kiertoaika ja 420 rivin
muutos, kun mediaanit ovat 5,5 päivää ja 38 riviä. Suuri muutos on
vaikea katselmoida, ja pitkään auki oleva työ on riski (luku 7). Tämä
on mittarin oikeaa käyttöä: se osoittaa, mistä kannattaa kysyä.

Väärää käyttöä on yksilöiden vertailu. Rivimäärä ja muutosten määrä
eivät mittaa hyötyä: paras muutos voi poistaa tuhat riviä, ja tiimin
arvokkain jäsen voi olla se, joka auttaa muita. Kun yksilötason luvuista
tehdään tavoite, niitä aletaan tuottaa (Goodhartin laki, luku 5).
Mittarit kuuluvat tiimin tasolle ja tiimin omaan käyttöön. Koko
toimitusputken mittarit käsitellään taidossa *Jatkuva integraatio ja
toimitus*, omistajuuden ja riippuvuuksien analyysi historiasta taidossa
*Tiimit ja organisaatiomallit*.

## Käytännössä

- **Kerro ensin johtopäätös.** Raportin ensimmäinen virke vastaa
  kysymykseen, valmistuuko tämä ja mitä tarvitaan.
- **Näytä toimivaa ohjelmistoa.** Mikään kalvo ei korvaa sitä, ja se
  on ainoa edistymisen mitta, jota ei voi kaunistella.
- **Kerro huonot uutiset heti ja kiitä niiden tuojaa.** Tieto vanhenee
  nopeasti, ja ensimmäinen rangaistu viestintuoja on viimeinen.
- **Yksi parannus kerrallaan.** Retrospektiivin tulos on kokeilu, jolla
  on omistaja ja jonka vaikutus tarkistetaan.
- **Lisää väkeä ajoissa tai älä lainkaan.** Myöhässä olevan projektin
  toimivat keinot ovat laajuuden karsiminen ja esteiden poistaminen.
- **Pidä tiimi pienenä ja vakaana.** Yhdessä pysyvä tiimi oppii
  toimimaan yhdessä, ja sen historia kelpaa ennustamiseen (luku 6).
  Jatkuvasti uudelleen koottava tiimi aloittaa joka kerta alusta.
- **Suojaa keskittyminen.** Sovi keskeytyksettömät ajat ja ohjaa
  kyselyt yhden ihmisen kautta.
- **Mittaa tiimiä, älä yksilöitä.**

## Itsearviointi

- Osaat jäsentää sidosryhmät ja valita kullekin sopivan viestintätavan.
- Osaat laatia tilanneraportin, joka perustuu havaintoihin, ja selittää
  vesimeloniraportin ongelman.
- Osaat kuvata retrospektiivin vaiheet ja sen yleisimmät viat.
- Osaat selittää, mitä psykologinen turvallisuus tarkoittaa ja miksi se
  on arvioinnin ja raportoinnin edellytys.
- Osaat perustella Brooksin lain perehdytyksen ja viestintäpolkujen
  avulla ja kertoa, milloin lisäväki silti auttaa.
- Osaat laskea versionhallinnan historiasta muutosten koon ja tehtävien
  kiertoajan ja tiedät, mihin näitä lukuja ei pidä käyttää.
