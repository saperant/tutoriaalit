# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

- **Nimeä vikamalli.** Kaatuvatko solmut pysyvästi vai palautuen,
  voiko viesti monistua, voiko verkko jakautua? Algoritmi on oikein vain
  jonkin mallin suhteen.
- **Turvallisuus ensin, eteneminen sitten.** Hyvä protokolla pysähtyy
  mieluummin kuin tekee väärän päätöksen.
- **Aikakatkaisu on epäily, ei tieto.** Kuittaamaton pyyntö on voinut
  tapahtua. Tee toistosta vaaraton idempotenssiavaimella.
- **Kuittaa vasta pysyvän kirjoituksen jälkeen.** Ryhmäkirjoitus antaa
  pysyvyyden halvalla, kunhan kuittaus odottaa sitä.
- **Älä järjestä seinäkelloilla.** Käytä loogista kelloa, hybridikelloa
  tai johtajan järjestysnumeroa.
- **Enemmistö ratkaisee.** Leikkaavat kvoorumit tekevät vaaleista ja
  sitoutumisesta turvallisia, ja pariton määrä solmuja sietää
  enemmistön verran vähemmän vikoja.
- **Valitse konsistenssi tiedon mukaan.** Linearisoituvuus lukoille ja
  rahalle, istuntotakuut käyttöliittymille, CRDT:t yhdisteltävälle
  tiedolle.
- **Vältä hajautettuja transaktioita.** Kun niitä tarvitaan,
  koordinaattorin päätös replikoidaan konsensuksella.
- **Simuloi, pienennä, tallenna siemen.** Deterministinen simulointi
  löytää virheet, delta-debuggaus tekee niistä ymmärrettäviä, ja siemen
  pitää ne korjattuina.

## Mitä tuotantojärjestelmä tekee toisin

Tämän tutoriaalin simulaattori on yksinkertainen: levy kirjoittaa
välittömästi ja atomisesti, viestit ovat muistissa olevia olioita, ja
kellot ajautuvat tasaisesti. Tuotannossa simulaattorin pitää mallintaa
myös levyn viat (osittaiset kirjoitukset, `fsync`in epäonnistuminen,
korruptoituneet lohkot), muistin ja levyn loppuminen, hitaat solmut
(*gray failure*) ja yksisuuntaiset jaot. TigerBeetlen simulaattori
ruiskuttaa levylle bittivirheitä ja tarkistaa, että replikat korjaavat
ne toisiltaan.

Raft-toteutuksesta puuttuvat esiäänestys, tilannevedokset, kokoonpanon
muutokset ja linearisoituvat luvut. Johtajattomasta replikoinnista
puuttuvat anti-entropia ja löysät kvoorumit, ja CRDT:istä hautakivien
karsinta. Jokainen niistä on oma virhelähteensä, ja jokainen testataan
samalla menetelmällä.

## Mihin seuraavaksi

- *Skaalautuvien järjestelmien suunnittelu*: osittaminen, välimuistit,
  kuormantasaus ja kapasiteetin mitoitus tämän tutoriaalin periaatteiden
  päälle.
- *Palveluarkkitehtuurit*: SAGA, viestinvälittäjät ja mikropalvelut,
  joissa hajautetun järjestelmän ongelmat näkyvät palveluiden
  rajapinnoissa.
- *SQL*: transaktiot ja eristystasot yhden tietokannan sisällä, joihin
  hajautetut transaktiot vertautuvat.
- *Rinnakkaisohjelmointi*: muistimallit ja lukottomat rakenteet, jotka
  ovat jaetun muistin vastine tämän tutoriaalin viestipohjaisille
  ratkaisuille.

## Lähteet ja jatkolukeminen

Kirjat:

- Martin Kleppmann: *Designing Data-Intensive Applications*. O'Reilly
  2017. Replikoinnin, konsistenssin ja konsensuksen selkein yleisesitys.
- Martin Kleppmann: *Concurrent and Distributed Systems*.
  Luentomuistiinpanot, Cambridgen yliopisto 2020. Vapaasti saatavilla.
- Maarten van Steen, Andrew S. Tanenbaum: *Distributed Systems*. 4. painos,
  2023. Vapaasti saatavilla tekijöiden sivuilta.
- Christian Cachin, Rachid Guerraoui, Luís Rodrigues: *Introduction to
  Reliable and Secure Distributed Programming*. Springer 2011.
- Nancy Lynch: *Distributed Algorithms*. Morgan Kaufmann 1996.

Artikkelit:

- Leslie Lamport: Time, Clocks, and the Ordering of Events in a
  Distributed System. *Communications of the ACM* 21(7), 1978.
- Michael J. Fischer, Nancy A. Lynch, Michael S. Paterson: Impossibility
  of Distributed Consensus with One Faulty Process. *Journal of the ACM*
  32(2), 1985.
- Maurice Herlihy, Jeannette Wing: Linearizability: A Correctness
  Condition for Concurrent Objects. *ACM TOPLAS* 12(3), 1990.
- Jeannette Wing, Chun Gong: Testing and Verifying Concurrent Objects.
  *Journal of Parallel and Distributed Computing* 17(1–2), 1993.
- Gavin Lowe: Testing for Linearizability. *Concurrency and Computation:
  Practice and Experience* 29(4), 2017.
- Hagit Attiya, Amotz Bar-Noy, Danny Dolev: Sharing Memory Robustly in
  Message-Passing Systems. *Journal of the ACM* 42(1), 1995.
- Douglas B. Terry ym.: Session Guarantees for Weakly Consistent
  Replicated Data. *PDIS* 1994.
- Giuseppe DeCandia ym.: Dynamo: Amazon's Highly Available Key-value
  Store. *SOSP* 2007.
- Marc Shapiro, Nuno Preguiça, Carlos Baquero, Marek Zawirski:
  Conflict-free Replicated Data Types. *SSS* 2011.
- Sandeep Kulkarni ym.: Logical Physical Clocks. *OPODIS* 2014.
- Joseph M. Hellerstein, Peter Alvaro: Keeping CALM: When Distributed
  Consistency Is Easy. *Communications of the ACM* 63(9), 2020.
- Diego Ongaro, John Ousterhout: In Search of an Understandable Consensus
  Algorithm. *USENIX ATC* 2014. Sekä Diego Ongaro: *Consensus: Bridging
  Theory and Practice*. Väitöskirja, Stanford 2014.
- Leslie Lamport: The Part-Time Parliament. *ACM TOCS* 16(2), 1998, ja
  Paxos Made Simple. *ACM SIGACT News* 32(4), 2001.
- Seth Gilbert, Nancy Lynch: Brewer's Conjecture and the Feasibility of
  Consistent, Available, Partition-Tolerant Web Services. *ACM SIGACT
  News* 33(2), 2002.
- Daniel Abadi: Consistency Tradeoffs in Modern Distributed Database
  System Design. *IEEE Computer* 45(2), 2012.
- James C. Corbett ym.: Spanner: Google's Globally-Distributed Database.
  *OSDI* 2012.
- Hector Garcia-Molina, Kenneth Salem: Sagas. *SIGMOD* 1987.
- Andreas Zeller, Ralf Hildebrandt: Simplifying and Isolating
  Failure-Inducing Input. *IEEE TSE* 28(2), 2002.
- Alex Groce ym.: Swarm Testing. *ISSTA* 2012.
- Chris Newcombe ym.: How Amazon Web Services Uses Formal Methods.
  *Communications of the ACM* 58(4), 2015.
- Melissa E. O'Neill: *PCG: A Family of Simple Fast Space-Efficient
  Statistically Good Algorithms for Random Number Generation*. Tekninen
  raportti, Harvey Mudd College 2014.

Verkossa:

- Jepsen-analyysit ja Knossos- sekä Elle-tarkistimet: jepsen.io.
- FoundationDB: *Testing Distributed Systems w/ Deterministic Simulation*
  (Will Wilson, Strange Loop 2014) ja FoundationDB:n dokumentaatio
  simulaattorista.
- TigerBeetle: VOPR-simulaattorin dokumentaatio, github.com/tigerbeetle.
- Raftin sivusto ja visualisointi: raft.github.io.
- Leslie Lamport: TLA+-materiaalit, lamport.azurewebsites.net/tla.
