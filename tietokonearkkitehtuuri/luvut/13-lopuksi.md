# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. Aika = käskyt × CPI × jakso. Jokainen optimointi muuttaa yhtä
   tekijää, ja usein toista vastakkaiseen suuntaan.
2. Optimoi siihen, mihin aika kuluu (Amdahl). Mittaa ensin: `perf stat`
   kertoo IPC:n, välimuisti- ja TLB-hudit sekä ohiennustukset.
3. Riippuvuusketjut määräävät nopeuden. Leveä ydin auttaa vain
   koodia, jossa on monta riippumatonta ketjua.
4. Latauksen tulos on aina myöhässä. Kääntäjä ajoittaa sen piiloon;
   osoitinjahti ei piiloudu.
5. Haaran hinta on sen ennustettavuus, ei sen suunta. Datasta riippuvat
   haarat kuumassa silmukassa kannattaa tehdä haarattomiksi.
6. Välimuisti siirtää 64 tavun lohkoja. Kulje muistissa peräkkäin, pidä
   työjoukko pienenä ja käsittele data paloina, jotka mahtuvat.
7. Kahden potenssin askeleet tuottavat ristiriitahuteja. Täyte tai
   lohkominen poistaa ne.
8. TLB:n ulottuvuus on pieni. Suuret työjoukot hyötyvät suurista
   sivuista.
9. Poikkeukset ovat tarkkoja ja keskeytykset asynkronisia. Käsittelijä
   tallentaa tilan, on lyhyt ja siirtää työn muualle.
10. MMIO on välimuistin ohi, järjestetty `fence`:llä ja `volatile`-
    osoittimen takana. DMA vaatii koherenssin tai välimuistin hallinnan.
11. Koherenssi toimii lohkoittain. Erota säikeiden kuumat muuttujat
    eri lohkoihin ja vältä kilpailtuja lukkoja.
12. NUMA-järjestelmässä data kuuluu sen säikeen solmuun, joka sitä
    käyttää: alusta se samassa säikeessä.
13. Käskykanta on sopimus, mikroarkkitehtuuri toteutus. Optimoi
    mikroarkkitehtuurille, mutta luota vain sopimukseen.

## Jatkotaidot

- *Käyttöjärjestelmät*: mitä ydin tekee tässä kuvatuilla
  mekanismeilla: sivutaulut, ansat, keskeytykset ja kontekstinvaihto.
- *Suorituskyvyn analyysi ja optimointi*: samat ilmiöt (välimuistit,
  ennustus, vektorointi) mitattuina oikealla laitteistolla ja
  ohjelmoijan keinot vaikuttaa niihin.
- *Rinnakkaisohjelmointi*: säikeet, lukot ja atomiset operaatiot
  koherenssin ja muistimallin päällä.
- *RTL-suunnittelu SystemVerilogilla*: tämän tutoriaalin datapolku ja
  liukuhihna synteesikelpoisena laitteistona. Jälkiohjattu malli on
  hyvä viitemalli RTL:n verifioinnille (*Laitteiston verifiointi*).
- *SoC-integraatio*: väylät, keskeytysohjaimet ja oheislaitteet
  järjestelmäpiirin tasolla.
- *GPU-ohjelmointi: OpenGL ja Vulkan* ja *GPU-laskenta*: suoritin, joka
  uhraa yksittäisen säikeen viiveen läpäisyn hyväksi.
- *C ja assembly yhteen* ja *Objektitiedostot, linkitys ja ABI*: miten
  kääntäjän tuottama koodi käyttää tässä kuvattuja rakenteita.

## Lähteet

Kirjat:

- John L. Hennessy ja David A. Patterson: *Computer Architecture: A
  Quantitative Approach*, 6. painos. Morgan Kaufmann, 2017. Alan
  perusteos: liukuhihnat, ILP, muistihierarkia, moniytimet ja
  kvantitatiivinen menetelmä.
- David A. Patterson ja John L. Hennessy: *Computer Organization and
  Design RISC-V Edition*, 2. painos. Morgan Kaufmann, 2020. Datapolku,
  ohjaus ja viisivaiheinen liukuhihna RISC-V:llä; luvut 3 ja 4 seuraavat
  sen rakennetta.
- David Patterson ja Andrew Waterman: *The RISC-V Reader: An Open
  Architecture Atlas*. Strawberry Canyon, 2017. Lyhyt johdatus
  käskykantaan ja sen suunnitteluperusteisiin.
- Daniel J. Sorin, Mark D. Hill ja David A. Wood: *A Primer on Memory
  Consistency and Cache Coherence*, 2. painos. Morgan & Claypool, 2020.
  MESI, hakemistot ja muistimallit perusteellisesti.
- John Paul Shen ja Mikko H. Lipasti: *Modern Processor Design:
  Fundamentals of Superscalar Processors*. McGraw-Hill, 2005.
- Bruce Jacob, Spencer Ng ja David Wang: *Memory Systems: Cache, DRAM,
  Disk*. Morgan Kaufmann, 2007.

Spesifikaatiot:

- RISC-V International: *The RISC-V Instruction Set Manual, Volume I:
  Unprivileged ISA* ja *Volume II: Privileged Architecture*.
  <https://riscv.org/technical/specifications/>. Käskymuodot (luku 2),
  CSR:t, ansat ja Sv32/Sv39 (luvut 8 ja 9).
- Intel: *Intel 64 and IA-32 Architectures Optimization Reference
  Manual*. <https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html>.
  µop-purku, fuusio ja µop-välimuisti.

Artikkelit:

- R. M. Tomasulo: An Efficient Algorithm for Exploiting Multiple
  Arithmetic Units. *IBM Journal of Research and Development* 11(1), 1967.
- James E. Smith: A Study of Branch Prediction Strategies. ISCA 1981.
  Kaksibittinen laskuri.
- Scott McFarling: *Combining Branch Predictors*. DEC WRL Technical Note
  TN-36, 1993. gshare ja turnausennustin.
- André Seznec ja Pierre Michaud: A Case for (Partially) TAgged
  GEometric History Length Branch Prediction. *Journal of
  Instruction-Level Parallelism* 8, 2006.
- Mark D. Hill ja Alan Jay Smith: Evaluating Associativity in CPU
  Caches. *IEEE Transactions on Computers* 38(12), 1989. 3C-malli.
- David W. Wall: Limits of Instruction-Level Parallelism. ASPLOS 1991.
- Paul Kocher ym.: Spectre Attacks: Exploiting Speculative Execution.
  IEEE S&P 2019. <https://spectreattack.com/>.
- Ulrich Drepper: *What Every Programmer Should Know About Memory*. 2007.
  <https://people.freebsd.org/~lstewart/articles/cpumemory.pdf>.

Työkalut ja verkkoaineistot:

- gem5-simulaattori: <https://www.gem5.org/>. Tutkimuskäytön
  täysjärjestelmäsimulaattori, BSD-lisenssi.
- Spike, RISC-V:n viitesimulaattori:
  <https://github.com/riscv-software-src/riscv-isa-sim>.
- Valgrind Cachegrind: <https://valgrind.org/docs/manual/cg-manual.html>.
  Välimuistisimulaattori oikeille ohjelmille.
- Linux `perf`: <https://perf.wiki.kernel.org/>.
- Agner Fog: *Instruction tables* ja *The microarchitecture of Intel,
  AMD and VIA CPUs*. <https://www.agner.org/optimize/>.
- uops.info: x86-käskyjen mitatut viiveet ja µop-määrät.
  <https://uops.info/>.
- Compiler Explorer: <https://godbolt.org/>. Kääntäjän tuottama
  assembly useille käskykannoille.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkien koodi on samalla
lisenssillä.
