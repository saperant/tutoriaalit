# Johdanto {.runko-johdanto}

Perusalgoritmit, eli lajittelu, binäärihaku, dynaaminen ohjelmointi ja
leveys- ja syvyyshaku, ratkaisevat suuren osan ohjelmoinnin
tehtävistä. Toiset tehtävät vaativat rakenteen, joka pitää lupauksensa
pahimmallakin syötteellä, tai algoritmin, joka hyödyntää ongelman
rakennetta. Ja joskus on parasta tunnistaa, ettei tehokasta tarkkaa
ratkaisua todennäköisesti ole. Tämä tutoriaali käsittelee nämä
tilanteet:

- **Tasapainotetut hakupuut:** punamusta puu, treap ja B-puu. Ne
  takaavat korkeuden $O(\log n)$ syötteen järjestyksestä riippumatta.
  B-puu minimoi lisäksi levylohkojen ja välimuistirivien luvut.
- **Tasoitettu analyysi:** potentiaalimenetelmä. Sillä todistetaan,
  että kalliit operaatiot ovat harvinaisia.
- **Erikoistuneet rakenteet:** union-find, Fenwick-puu,
  segmenttipuu ja trie.
- **Merkkijonoalgoritmit:** Knuthin–Morrisin–Prattin algoritmi,
  Z-algoritmi, Rabinin–Karpin hajautushaku sekä suffiksi- ja
  LCP-taulukot.
- **Verkkovirtaukset:** Edmondsin–Karpin ja Dinicin algoritmit,
  minimileikkaus ja kaksijakoinen paritus.
- **Satunnaistetut algoritmit ja rakenteet:** skip-lista,
  pikavalinta, Freivaldsin tarkistus, Bloom-suodatin, Count-Min-luonnos
  ja säiliöotanta.
- **Laskennallinen vaativuus:** P, NP, polynomiset reduktiot,
  NP-täydellisyys sekä approksimointi, heuristiikat ja haarautuminen
  ja karsinta.

Tutoriaali jatkaa taidosta *Algoritmit*. Sen menetelmät oletetaan
tunnetuiksi: vaativuusanalyysi, lajittelut ja niiden alaraja,
binäärihaku, ahneet algoritmit, dynaaminen ohjelmointi sekä Dijkstran,
Bellmanin–Fordin, Kruskalin ja Primin algoritmit. Kruskalin algoritmin
yhteydessä käytetty union-find käsitellään tässä tarkemmin.
Tietorakenteista oletetaan tavallinen hakupuu, keko, hajautustaulu ja
verkkojen esitystavat (taito *Tietorakenteet*). Matematiikasta
tarvitaan induktiota ja invariantteja (*Diskreetti matematiikka*) sekä
odotusarvoa ja riippumattomuutta (*Todennäköisyys*).

## Kieli ja testaus

Esimerkit ovat C++23:a. Kieli antaa tietorakenteille omistuksen
(`std::unique_ptr`), malliparametrit ja standardikirjaston valmiit
rakenteet, joita käytetään vertailun malleina (`std::set`,
`std::string::find`, `std::sort`). Kieli on tuttu taidosta *Moderni
C++*. Esimerkit käännetään GCC 14:llä ja Clang 20:llä
(`-std=c++23 -Wall -Wextra -Wpedantic -Werror`) AddressSanitizerin ja
UndefinedBehaviorSanitizerin kanssa. Sanitoijat havaitsevat
roikkuvat osoittimet ja taulukon ohi indeksoinnin, jotka ovat
osoitinrakenteiden yleisimmät virheet.

Edistyneen rakenteen toteutus on pitkä, ja sen virheet piiloutuvat
harvinaisiin tapauksiin, kuten kiertoon tietyssä värityksessä tai
tyhjentyvään solmuun. Siksi jokainen tämän tutoriaalin rakenne
testataan samalla tavalla. Satunnainen operaatiosarja ajetaan
rakenteelle ja yksinkertaiselle mallille, jonka oikeellisuus on
ilmeinen, ja tuloksia verrataan jokaisen operaation jälkeen. Lisäksi
tarkistetaan rakenteen sisäiset invariantit. Luku 2 esittelee
menetelmän ja näyttää, miten se löytää virheen ja pienentää sen
aiheuttavan syötteen.

Satunnaisuus tulee omasta generaattorista kiinteällä siemenellä, joten
tulosteet ovat samat joka koneella. Työmäärää mitataan laskureilla
(vertailuja, kuljettuja linkkejä, hakupuun solmuja) eikä kellolla:
laskuri on toistettava ja mittaa juuri sitä, mitä analyysi ennustaa.
Todellinen nopeus, välimuistit ja vektorointi kuuluvat taitoon
*Suorituskyvyn analyysi ja optimointi*.

## Lukuohje

Luvut 3–7 käsittelevät tietorakenteita, luvut 8–9 merkkijonoja ja
luku 10 virtauksia. Luvut 11–12 käsittelevät satunnaisuutta ja luvut
13–14 vaativuutta. Luku 2 kannattaa lukea ensin. Muut luvut ovat
pääosin itsenäisiä, mutta luku 6 käyttää luvun 5 tasoitettua
analyysia, ja luku 10 käyttää samaa virtausverkkoa kahdessa
esimerkissä. Jokaisen luvun lopussa on itsearviointi. Jos osaat kaikki
sen väitteet, voit ohittaa luvun.
