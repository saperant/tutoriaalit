# Rekursio

Funktionaalisessa ohjelmassa ei ole silmukkamuuttujia, joita
päivitettäisiin. Toisto ilmaistaan **rekursiolla**: funktio ratkaisee
tehtävän pienemmän osatehtävän avulla. Rekursio ei ole temppu vaan suora
seuraus datan rakenteesta. Kun data on määritelty rekursiivisesti, sitä
käsittelevä funktio voidaan kirjoittaa samaan muotoon.

## Rakenteellinen rekursio

Lista on joko tyhjä tai pari, jonka loppu on lista. Listaa käsittelevä
funktio saa siksi kaksi haaraa:

- **perustapaus** tyhjälle listalle
- **rekursiivinen tapaus**, joka yhdistää ensimmäisen alkion ja loppuosan
  tuloksen.

```{.scheme tiedosto="esimerkit/03-summa.rkt" osa="rekursio"}
```

Tätä **suunnittelureseptiä** (*design recipe*, kirjasta *How to Design
Programs*) noudattava funktio on oikein, jos haarat ovat oikein.
Päättyminen on taattu, koska jokainen kutsu saa aidosti pienemmän osan
datasta. Kun dataa on monta lajia, kuten puussa, haaroja on yksi kutakin
lajia kohti.

## Häntärekursio

`summa` jättää jokaisella tasolla kesken yhteenlaskun `(+ (first lista)
...)`, joka odottaa rekursiivisen kutsun tulosta. Kesken jääneet
laskut vievät tilaa pinosta, ja muisti kasvaa listan pituuden mukana.

**Häntäkutsussa** kutsu on funktion viimeinen teko, eikä mitään jää
odottamaan. Scheme ja Racket **takaavat**, että häntäkutsu ei kasvata
pinoa (*proper tail calls*), joten häntärekursio on silmukka. Välitulos
kuljetetaan **kertymässä** eli akkumulaattorissa.

```{.scheme tiedosto="esimerkit/03-summa.rkt" osa="hanta"}
```

Eron näkee, kun laskenta kirjoitetaan auki askel kerrallaan. Esimerkki
`03-jaljitys.rkt` tulostaa saman summan molemmilla tavoilla.
Tavallisessa rekursiossa lauseke ensin kasvaa, koska jokainen taso
jättää yhteenlaskun odottamaan, ja kutistuu vasta, kun perustapaus on
saavutettu. Häntärekursiossa rivi pysyy samankokoisena: koko tila on
argumenteissa.

```{.tuloste tiedosto="esimerkit/03-jaljitys.odotettu"}
```

Jäljittävä versio saa kesken olevan työn parametrina, jotta sen voi
tulostaa. Tavallisesti saman tiedon säilyttää kutsupino:

```{.scheme tiedosto="esimerkit/03-jaljitys.rkt" osa="tavallinen"}
```

**Nimetty `let`** on Racketin tavallisin silmukka. `(let silmukka
([xs lista] ...) ...)` määrittelee paikallisen funktion `silmukka` ja
kutsuu sitä heti alkuarvoilla.

```{.scheme tiedosto="esimerkit/03-summa.rkt" osa="syva"}
```

```{.tuloste tiedosto="esimerkit/03-summa.odotettu"}
```

Racket kasvattaa pinoa tarvittaessa keon puolelle, joten miljoonan tason
tavallinen rekursio ei kaadu. Useimmissa kielissä kaatuisi: Pythonin
rekursioraja on oletuksena 1000, ja C:n, Javan ja Rustin pinot loppuvat
kymmenien tai satojen tuhansien tasojen kohdalla.

## Puurekursio

Kun data haarautuu, myös rekursio haarautuu. Hakemistopuussa solmu on
tiedosto tai hakemisto, jolla on lapsia. Koon laskeminen kutsuu itseään
jokaiselle lapselle ja yhdistää tulokset.

```{.scheme tiedosto="esimerkit/03-puu.rkt" osa="data"}
```

```{.scheme tiedosto="esimerkit/03-puu.rkt" osa="koko"}
```

Rekursion parametri voi kuljettaa kontekstia alaspäin. Tässä se on polun
etuliite:

```{.scheme tiedosto="esimerkit/03-puu.rkt" osa="polut"}
```

```{.tuloste tiedosto="esimerkit/03-puu.odotettu"}
```

`λ` on sama kuin `lambda`, eli nimetön funktio (luku 4). DrRacketissa
sen saa näppäinyhdistelmällä Ctrl+\\.

## Kustannus: osatehtävien toistuminen

Puurekursio on luonteva, mutta jos osatehtävät toistuvat, työ voi kasvaa
eksponentiaalisesti. Fibonaccin lukujen suora määritelmä laskee
`(fib 23)`:n kahdesti, `(fib 22)`:n kolmesti ja niin edelleen.

```{.scheme tiedosto="esimerkit/03-fib.rkt" osa="naivi"}
```

```{.scheme tiedosto="esimerkit/03-fib.rkt" osa="iteratiivinen"}
```

```{.tuloste tiedosto="esimerkit/03-fib.odotettu"}
```

Kutsupuusta näkee, mistä kutsujen määrä tulee. Puu on piirretty
ohjelmalla `03-kutsupuu.rkt`, joka käy kutsut läpi samassa
järjestyksessä kuin `fib` ja merkitsee harmaalla ne, joiden argumentti
on jo kertaalleen laskettu:

```{.dot tiedosto="esimerkit/03-kutsupuu.odotettu" otsikko="`(fib 5)`:n kutsupuu. Viidestätoista kutsusta yhdeksän laskee arvon, joka on jo laskettu."}
```

```{.scheme tiedosto="esimerkit/03-kutsupuu.rkt" osa="puu"}
```

Korjauksia on kaksi. Iteratiivinen versio kuljettaa kahta edellistä
arvoa kertymissä. Muistaminen (*memoization*, luku 9) säilyttää
rekursiivisen muodon ja tallentaa lasketut tulokset. Molemmat ovat
dynaamisen ohjelmoinnin muotoja (taito *Algoritmit*).

## Käytännössä

- **Rakenteellinen rekursio on kaikkien puiden käsittelyn malli.**
  Kääntäjän syntaksipuut, JSON, DOM, hakemistot ja tiedostomuodot
  käsitellään funktiolla, jossa on haara kutakin solmulajia kohti.
  Visitor-suunnittelumalli on sama asia oliokielen keinoin.
- **Häntäkutsujen optimointia ei voi olettaa.** Python ja Java eivät
  optimoi häntäkutsuja lainkaan, eikä JavaScript käytännössä.
  C- ja C++-kääntäjät optimoivat ne usein mutta eivät takuulla,
  ja Rustissa sitä ei taata. Niissä syvä rekursio kirjoitetaan
  silmukaksi tai eksplisiittisen pinon avulla. Scala (`@tailrec`) ja
  Kotlin (`tailrec`) tarkistavat häntäkutsun käännösaikana.
- **Kertymä on silmukkamuuttuja.** Häntärekursiivinen funktio vastaa
  suoraan silmukkaa, jossa parametrit ovat silmukan muuttujat. Kun
  muunnat rekursion silmukaksi jossakin toisessa kielessä, kertymistä
  tulee muuttujia ja perustapauksesta silmukan lopetusehto.
- **Rekursion syvyys on syötteen funktio.** Tasapainoisen puun syvyys
  on O(log n), mutta linkitetyn listan tai vinon puun syvyys on O(n).
  Kun syöte tulee ulkopuolelta, rekursiivinen jäsennin tai puun
  läpikäynti on palvelunestohaavoittuvuus kielissä, joissa pino on
  rajallinen.
- **Toistuvat osatehtävät kannattaa tunnistaa ajoissa.** Jos
  rekursiopuussa sama argumentti esiintyy monesti, käytä muistamista tai
  kirjoita laskenta alhaalta ylös.

## Itsearviointi

- Osaat kirjoittaa listaa tai puuta käsittelevän funktion datan
  määritelmän mukaan: haara kutakin tapausta kohti.
- Osaat muuttaa tavallisen rekursion häntärekursioksi kertymän avulla
  ja kirjoittaa sen nimetyllä `let`-lausekkeella.
- Osaat kirjoittaa pienen kutsun laskennan auki askel askeleelta ja
  näyttää siitä, kasvaako odottavien laskujen määrä.
- Osaat selittää, milloin rekursio on turvallinen Pythonissa, Javassa
  tai C:ssä ja milloin se pitää kirjoittaa silmukaksi.
- Osaat tunnistaa eksponentiaalisen puurekursion ja korjata sen
  iteraatiolla tai muistamisella.
