# Lopuksi {.runko-lahteet}

## Työnkulku

Arkkitehtuurin tutkiminen etenee samoin vaihein kysymyksestä riippumatta:

1. **Kysymys ja päätös.** Mitä päätetään, millä tavoitteilla ja
   rajoitteilla? Mikä tarkkuus riittää päätökseen?
2. **Kuormat.** Mitä laitteistolla ajetaan? Karakterisoi ne koneesta
   riippumatta: jakaumat, hutikäyrät, vaiheet (luku 2).
3. **Analyyttinen malli.** Rajat ja suuruusluokat: Amdahl, roofline,
   Littlen laki, CPI-pino, jonoteoria, teho (luvut 3, 4 ja 8).
4. **Simulointi.** Ilmiöt, joita kaavat eivät näe: kilpailu,
   riippuvuudet, limitys. Valitse taso kysymyksen mukaan, ja nopeuta
   abstraktiolla tai näytteistyksellä (luvut 5–7).
5. **Validointi.** Vertaa malleja toisiinsa ja mittauksiin. Kalibroi ja
   validoi eri datalla (luku 10).
6. **Tutkiminen.** Koko tila nopealla mallilla, parhaat tarkalla.
   Pareto-rintama ja herkkyys (luku 9).
7. **Raportointi.** Tulos, epävarmuus, oletukset ja se, mistä päätös
   riippuu (luku 10).

## Nyrkkisääntöjä

- Malli on oikea vain oletuksissaan. Kirjoita ne näkyviin.
- Yksinkertainen malli, jonka ymmärtää, on alussa arvokkaampi kuin
  tarkka malli, jota ei ymmärrä.
- Kaksi mallia samasta järjestelmästä paljastaa enemmän kuin yksi
  tarkka.
- Kuormitettu järjestelmä on kiinnostavin ja vaikein mallintaa: viive
  kasvaa kuten $1/(1-\rho)$, ja malli, joka ei tunne kilpailua, on
  siellä aina liian optimistinen.
- Energia on datan liikettä.
- Kiinteät kulut määräävät kiihdyttimen tasapisteen.
- Optimi tilan reunalla tarkoittaa, että tila on liian pieni.
- Lähes yhtä hyvät, erilaiset suunnitelmat tarkoittavat, että malli ei
  pysty valitsemaan.
- Yksi ajo ei kerro epävarmuutta.
- Kalibroitu parametri, joka on fysikaalisesti mahdoton, kantaa mallin
  muut virheet.

## Mihin seuraavaksi

Taitopuussa tämä taito johtaa kohti toteutusta. *Korkean tason
synteesi* tekee C++-mallista laitteistoa, jolloin luvun 7 kiihdytin
voidaan toteuttaa ja sen todellinen pinta-ala ja teho mitata. *ASIC-toteutus*
antaa ne luvut, joita tämän paketin tehomallit arvioivat.
*Rinnakkaisohjelmointi* ja *GPU-laskenta* kertovat, miten ohjelmisto
käyttää moniytimiä ja kiihdyttimiä, joita täällä mitoitettiin.

## Lähteet

Kirjat:

- Hennessy, J. L. ja Patterson, D. A.: *Computer Architecture: A
  Quantitative Approach*, 6. painos. Morgan Kaufmann, 2017.
  Arkkitehtuurin kvantitatiivinen arviointi, mukaan lukien
  välimuistien ja moniytimien mallit.
- Eeckhout, L.: *Computer Architecture Performance Evaluation Methods*.
  Synthesis Lectures on Computer Architecture, Morgan & Claypool, 2010.
  Mallit, simulointi ja näytteistys tiiviisti.
- Harchol-Balter, M.: *Performance Modeling and Design of Computer
  Systems: Queueing Theory in Action*. Cambridge University Press, 2013.
- Jain, R.: *The Art of Computer Systems Performance Analysis*. Wiley,
  1991. Kokeiden suunnittelu, simulointi ja tulosten esittäminen.

Kuormat ja jäljet (luku 2):

- Mattson, R. L., Gecsei, J., Slutz, D. R. ja Traiger, I. L.:
  Evaluation techniques for storage hierarchies. *IBM Systems Journal*
  9(2), 1970.
- Denning, P. J.: The working set model for program behavior.
  *Communications of the ACM* 11(5), 1968.

Analyyttiset mallit (luvut 3 ja 4):

- Hill, M. D. ja Marty, M. R.: Amdahl's law in the multicore era.
  *IEEE Computer* 41(7), 2008.
- Williams, S., Waterman, A. ja Patterson, D.: Roofline: an insightful
  visual performance model for multicore architectures.
  *Communications of the ACM* 52(4), 2009.
- Little, J. D. C.: A proof for the queuing formula L = λW.
  *Operations Research* 9(3), 1961.
- Reiser, M. ja Lavenberg, S. S.: Mean-value analysis of closed
  multichain queuing networks. *Journal of the ACM* 27(2), 1980.

Simulointi (luvut 5 ja 6):

- Lowe-Power, J. ym.: The gem5 simulator: version 20.0+. arXiv
  2007.03152, 2020. <https://www.gem5.org/>
- Karkhanis, T. S. ja Smith, J. E.: A first-order superscalar
  processor model. *ISCA* 2004.
- Eyerman, S., Eeckhout, L., Karkhanis, T. ja Smith, J. E.: A
  mechanistic performance model for superscalar out-of-order
  processors. *ACM Transactions on Computer Systems* 27(2), 2009.
- Carlson, T. E., Heirman, W. ja Eeckhout, L.: Sniper: exploring the
  level of abstraction for scalable and accurate parallel multi-core
  simulation. *SC* 2011.
- Sherwood, T., Perelman, E., Hamerly, G. ja Calder, B.: Automatically
  characterizing large scale program behavior. *ASPLOS* 2002.
- Wunderlich, R. E., Wenisch, T. F., Falsafi, B. ja Hoe, J. C.: SMARTS:
  accelerating microarchitecture simulation via rigorous statistical
  sampling. *ISCA* 2003.

Teho, energia ja pinta-ala (luku 8):

- Horowitz, M.: Computing's energy problem (and what we can do about
  it). *ISSCC* 2014.
- Sakurai, T. ja Newton, A. R.: Alpha-power law MOSFET model and its
  applications to CMOS inverter delay and other formulas. *IEEE Journal
  of Solid-State Circuits* 25(2), 1990.
- Hartstein, A., Srinivasan, V., Puzak, T. R. ja Emma, P. G.: Cache miss
  behavior: is it √2? *Computing Frontiers* 2006.
- Muralimanohar, N., Balasubramonian, R. ja Jouppi, N. P.: CACTI 6.0: a
  tool to model large caches. HP Laboratories, 2009.
- Li, S. ym.: McPAT: an integrated power, area, and timing modeling
  framework for multicore and manycore architectures. *MICRO* 2009.
- Parashar, A. ym.: Timeloop: a systematic approach to DNN accelerator
  evaluation. *ISPASS* 2019; Wu, Y. N., Emer, J. S. ja Sze, V.:
  Accelergy: an architecture-level energy estimation methodology for
  accelerator designs. *ICCAD* 2019.

Suunnittelutila ja raportointi (luvut 9 ja 10):

- McKay, M. D., Beckman, R. J. ja Conover, W. J.: A comparison of three
  methods for selecting values of input variables in the analysis of
  output from a computer code. *Technometrics* 21(2), 1979.
- Deb, K., Pratap, A., Agarwal, S. ja Meyarivan, T.: A fast and elitist
  multiobjective genetic algorithm: NSGA-II. *IEEE Transactions on
  Evolutionary Computation* 6(2), 2002.
- Fleming, P. J. ja Wallace, J. J.: How not to lie with statistics: the
  correct way to summarize benchmark results. *Communications of the
  ACM* 29(3), 1986.

Muut taitopuun paketit: *Korkean tason mallinnus* (SystemC ja TLM),
*Suorituskyvyn analyysi ja optimointi* (Amdahl ja roofline ohjelmiston
näkökulmasta), *Todennäköisyys ja tilastot* (jakaumat ja luottamusvälit)
ja *Tietokonearkkitehtuuri* (mallinnettavat rakenteet).
