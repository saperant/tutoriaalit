# Lopuksi {.runko-lahteet}

Tutoriaalissa rakennettiin kääntäjä, joka kulkee lähdetekstistä
ajettavaan RISC-V-ohjelmaan: selaaja, jäsennin, semanttinen analyysi,
tulkki, välikieli, SSA-muoto, datavuoanalyysi, optimoinnit,
koodingenerointi ja rekisterien varaus. Jokainen vaihe on lyhyt, ja
jokaisella on oma tulostettava tietorakenteensa ja omat testinsä.

## Nyrkkisäännöt

1. **Määrittele kieli ensin.** Kielioppi, tyyppisäännöt ja
   aritmetiikan merkitys ovat testien perusta. Vältä määrittelemätöntä
   käytöstä omassa kielessäsi.
2. **Yksi vaihe, yksi tietorakenne.** Tokenit, syntaksipuu ja välikieli
   ovat erillisiä, ja jokaisen voi tulostaa. Vika paikannetaan
   vaiheeseen katsomalla välitulosteita.
3. **Käsin kirjoitettu jäsennin, Pratt lausekkeisiin.** Ne ovat
   luettavia, nopeita ja antavat hyvät virheilmoitukset.
4. **Virheistä toivutaan, seurannaisvirheet estetään.** Paniikkitila
   lauseen rajalle ja tuntematon tyyppi virheellisille lausekkeille.
5. **Alenna naiivisti, optimoi erikseen.** Yksinkertainen alentaminen
   ja pienet, toistettavat passit ovat helpompia saada oikeiksi kuin
   älykäs alentaminen.
6. **Jokainen optimointi on todistettava.** Sieventämissääntö pätee
   kielen semantiikassa, myös ylivuodossa ja nollalla, tai sitä ei
   käytetä.
7. **Analyysit ovat konservatiivisia.** Epätarkka tulos on sallittu,
   väärä ei.
8. **Noudata kutsukonventiota tarkasti.** Se on ainoa rajapinta
   muuhun maailmaan.
9. **Tulkki on oraakkeli.** Differentiaalitestaus viitetulkkia vastaan
   löytää virheet, joita kukaan ei osannut kirjoittaa testiksi.
10. **Mittaa testien teho.** Istutettu vika, joka jää löytymättä,
    kertoo aukon.

## Harjoituksia ja laajennuksia

- **Välittömät vakiot.** Tuota `addi` ja `slti`, kun toinen operandi
  on pieni vakio, ja yhdistä vertailu ja haara (`blt`, `bge`).
  Differentiaalitestit kertovat, menikö jotain rikki.
- **Taulukot.** Lisää kiinteän kokoiset paikalliset taulukot:
  tyyppijärjestelmään taulukkotyyppi, välikieleen lataus ja tallennus,
  pinokehykseen tilaa ja indeksin rajatarkistus ajonaikaiseen
  kirjastoon.
- **Häntäkutsut.** Tunnista `return f(...)` ja muuta se hypyksi
  funktion alkuun, kun `f` on funktio itse.
- **Upottaminen.** Korvaa pienen funktion kutsu sen rungolla
  välikielessä ja katso, mitä laskostus tekee jäljelle jääneelle.
- **SSA-optimoinnit.** Tee vakioiden eteneminen SSA-muodossa ja poistu
  SSA:sta kopioilla; vertaa tulosta paikalliseen arvonumerointiin.
- **Viennin hinta.** Painota lineaarisen pyyhkäisyn valintaa
  silmukoiden syvyydellä ja mittaa pinolatausten määrä
  `summa`-esimerkissä kahdella rekisterillä.

## Läheiset taidot

- *Suorituskyvyn analyysi ja optimointi* – kääntäjän tuottaman koodin
  mittaaminen ja ohjaaminen.
- *Takaisinmallinnus* – kääntäjän tuottaman koodin lukeminen ilman
  lähdekoodia.
- *Korkean tason synteesi* – C++:n kääntäminen laitteistoksi, jossa
  ajoitus ja resurssien varaus ovat saman ongelman muunnelmia.
- *Laitteiston verifiointi* – sama differentiaali- ja
  mutaatiotestauksen ajattelu laitteistolle.

## Lähteet

Kirjat:

- Aho, Lam, Sethi, Ullman: *Compilers: Principles, Techniques, and
  Tools* (2. painos, 2006). "Lohikäärmekirja", jäsennyksen ja
  datavuoanalyysin klassikko.
- Cooper, Torczon: *Engineering a Compiler* (3. painos, 2022).
  Selkeä esitys välikielistä, SSA:sta, käskyjen valinnasta ja
  rekisterien varauksesta.
- Appel: *Modern Compiler Implementation in ML/Java/C* (1998).
  Kokonainen kääntäjä luku luvulta, kuten tässä tutoriaalissa.
- Nystrom: *Crafting Interpreters* (2021),
  <https://craftinginterpreters.com/>. Vapaasti luettava kirja
  selaajista, Prattin jäsentimestä, puutulkista ja tavukoodista.
- Muchnick: *Advanced Compiler Design and Implementation* (1997).
  Optimointien hakuteos.
- Rastello, Bouchez Tichadou (toim.): *SSA-based Compiler Design*
  (2022). SSA-muodon teoria ja käytäntö.

Artikkelit:

- Pratt: Top Down Operator Precedence. POPL 1973.
- Cytron, Ferrante, Rosen, Wegman, Zadeck: Efficiently Computing
  Static Single Assignment Form and the Control Dependence Graph.
  TOPLAS 13(4), 1991.
- Cooper, Harvey, Kennedy: A Simple, Fast Dominance Algorithm.
  Software Practice and Experience, 2001.
- Kildall: A Unified Approach to Global Program Optimization. POPL 1973.
- Poletto, Sarkar: Linear Scan Register Allocation. TOPLAS 21(5), 1999.
- Chaitin: Register Allocation & Spilling via Graph Coloring. SIGPLAN
  Symposium on Compiler Construction, 1982.
- Briggs, Cooper, Torczon: Improvements to Graph Coloring Register
  Allocation. TOPLAS 16(3), 1994.
- Yang, Chen, Eide, Regehr: Finding and Understanding Bugs in C
  Compilers. PLDI 2011 (Csmith).
- Zeller, Hildebrandt: Simplifying and Isolating Failure-Inducing
  Input. IEEE TSE 28(2), 2002.
- Lopes, Lee, Hur, Liu, Regehr: Alive2: Bounded Translation Validation
  for LLVM. PLDI 2021.

Dokumentaatio ja työkalut:

- RISC-V ELF psABI Specification, <https://github.com/riscv-non-isa/riscv-elf-psabi-doc>.
- The RISC-V Instruction Set Manual, Volume I: Unprivileged ISA,
  <https://riscv.org/technical/specifications/>.
- GCC Internals, <https://gcc.gnu.org/onlinedocs/gccint/>.
- LLVM Language Reference Manual, <https://llvm.org/docs/LangRef.html>,
  ja LLVM:n Kaleidoscope-opas <https://llvm.org/docs/tutorial/>.
- Compiler Explorer, <https://godbolt.org/>.
- C-Reduce, <https://github.com/csmith-project/creduce>, ja Csmith,
  <https://github.com/csmith-project/csmith>.
- QEMU User Mode Emulation, <https://www.qemu.org/docs/master/user/>.
