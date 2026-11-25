# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Jaa olemalla jakamatta.** Säie käsittelee omaa dataansa, ja tulokset
   yhdistetään lopuksi. Paras synkronointi on se, jota ei tarvita.
2. **Ei datakilpailuja.** Jokainen jaettu muuttuja on joko lukon alla tai
   atominen. Datakilpailu on määrittelemätöntä käyttäytymistä, ei
   pelkkä väärä tulos.
3. **`seq_cst` oletuksena**, heikommat järjestykset vain perusteltuina ja
   mitattuina, aina release/acquire-pareina.
4. **Elinajat määrittelyjärjestyksellä.** Säikeet määritellään
   viimeisinä, jotta ne odotetaan ennen kuin niiden käyttämä data tuhoutuu.
   Sieppaukset nimetään.
5. **Yksi lukko ensin**, hienojakoisempi vain mitatusti kilpailtuun
   kohtaan. Usea lukko yhdellä `scoped_lock`illa.
6. **Ehtomuuttuja aina predikaatin kanssa**, tila muuttuu lukon alla.
7. **Rajaa jonot ja tee sulkemisesta rajapinta.**
8. **Valmis väline ennen omaa**: standardin primitiivit, säiepooli,
   rinnakkaiset algoritmit ja testatut lukottomat kirjastot.
9. **Lukoton rakenne tarvitsee takaisinottosuunnitelman.**
10. **Testaa invariantteja ThreadSanitizerilla, stressillä ja
    deterministisillä lomituksilla.** Tulosteet eivät saa riippua
    lomituksesta.

## Jatkotaidot

- *C++:n suorituskyky*: allokaattorit, siirtosemantiikka ja datan asettelu
  rinnakkaisen koodin nopeuttamiseksi.
- *GPU-laskenta*: tuhansia säikeitä, oma muistihierarkia ja
  datarinnakkaiset algoritmit.
- *Hajautetut järjestelmät*: rinnakkaisuus ilman jaettua muistia, viestit,
  osittaiset viat ja yhteisymmärrys.
- *Suorituskyvyn analyysi ja optimointi*: rinnakkaisen ohjelman
  mittaaminen ja väärän jakamisen kaltaisten ilmiöiden etsintä.
- *Verkko-ohjelmointi*: samanaikaisuus asynkronisella I/O:lla ja
  korutiineilla.
- *Reaaliaikakäyttöjärjestelmät*: prioriteetit, ajoitusanalyysi ja
  prioriteetin periytyminen.

Hyviä harjoituksia ovat työnvarastava säiepooli, epookkipohjainen
takaisinotto Treiberin pinolle, lukoton jono Michaelin ja Scottin
algoritmilla sekä tämän tutoriaalin litmus-testien ajaminen
AArch64-koneella.

## Lähteet ja jatkolukeminen

Kirjat:

- Anthony Williams: *C++ Concurrency in Action*, 2. painos. Manning 2019.
- Maurice Herlihy, Nir Shavit, Victor Luchangco, Michael Spear: *The Art
  of Multiprocessor Programming*, 2. painos. Morgan Kaufmann 2020.
- Paul E. McKenney: *Is Parallel Programming Hard, And, If So, What Can
  You Do About It?* Vapaasti saatavilla:
  <https://mirrors.edge.kernel.org/pub/linux/kernel/people/paulmck/perfbook/perfbook.html>
- Mara Bos: *Rust Atomics and Locks*. O'Reilly 2023. Muistimalli ja
  lukkojen toteutus laitteistotasolla; sama malli kuin C++:ssa.
  <https://marabos.nl/atomics/>

Muistimalli:

- Leslie Lamport: How to Make a Multiprocessor Computer That Correctly
  Executes Multiprocess Programs. *IEEE Transactions on Computers*
  C-28(9), 1979.
- Hans-J. Boehm, Sarita V. Adve: Foundations of the C++ Concurrency
  Memory Model. *PLDI* 2008.
- Mark Batty, Scott Owens, Susmit Sarkar, Peter Sewell, Tjark Weber:
  Mathematizing C++ Concurrency. *POPL* 2011.
- Peter Sewell, Susmit Sarkar, Scott Owens, Francesco Zappa Nardelli,
  Magnus O. Myreen: x86-TSO: A Rigorous and Usable Programmer's Model for
  x86 Multiprocessors. *Communications of the ACM* 53(7), 2010.
- Jade Alglave, Luc Maranget, Michael Tautschnig: Herding Cats.
  *ACM TOPLAS* 36(2), 2014. Litmus-testien työkalut `herd7` ja `litmus7`.

Algoritmit:

- R. Kent Treiber: *Systems Programming: Coping with Parallelism*. IBM
  Research Report RJ 5118, 1986.
- Maged M. Michael, Michael L. Scott: Simple, Fast, and Practical
  Non-Blocking and Blocking Concurrent Queue Algorithms. *PODC* 1996.
- Maged M. Michael: Hazard Pointers: Safe Memory Reclamation for
  Lock-Free Objects. *IEEE TPDS* 15(6), 2004.
- Keir Fraser: *Practical Lock-Freedom*. Väitöskirja, University of
  Cambridge 2004.
- Dmitry Vyukov: Bounded MPMC queue. 1024cores.net.
- Robert D. Blumofe, Charles E. Leiserson: Scheduling Multithreaded
  Computations by Work Stealing. *Journal of the ACM* 46(5), 1999.
- Gene M. Amdahl: Validity of the Single Processor Approach to Achieving
  Large Scale Computing Capabilities. *AFIPS* 1967.
- John L. Gustafson: Reevaluating Amdahl's Law. *Communications of the
  ACM* 31(5), 1988.
- Herb Sutter: The Free Lunch Is Over. *Dr. Dobb's Journal* 30(3), 2005.

Työkalut ja dokumentaatio:

- Konstantin Serebryany, Timur Iskhodzhanov: ThreadSanitizer: Data Race
  Detection in Practice. *WBIA* 2009.
- Clang: *ThreadSanitizer* ja *Thread Safety Analysis*.
  <https://clang.llvm.org/docs/ThreadSanitizer.html>
- cppreference: *Concurrency support library*.
  <https://en.cppreference.com/w/cpp/thread>
- C++-standardi, luvut [intro.multithread] ja [thread], sekä
  C++26:n ehdotukset P2530 (vaaraosoittimet) ja P2545 (RCU).
