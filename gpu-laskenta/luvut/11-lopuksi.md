# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Referenssi ensin.** Jokainen GPU-toteutus vertaa tulostaan
   yksinkertaiseen CPU-toteutukseen epätasaisilla koilla:
   kokonaisluvut tarkasti, liukuluvut toleranssilla kaksoistarkkuutta
   vastaan.
2. **Validointi päälle**, myös synkronoinnin validointi testeissä.
   Lavapipellä ja yhdellä laitteella toimiva ohjelma voi olla väärin.
3. **Reunat tarkistetaan**, ryhmien määrä pyöristetään ylöspäin ja
   rajat (`maxComputeWorkGroupCount` ja muut) kysytään laitteelta.
4. **Työryhmät eivät odota toisiaan.** Riippuvuus työryhmien välillä
   on uusi ajo ja este.
5. **Aliryhmä, työryhmä, ajo**: tee mahdollisimman paljon alimmalla
   tasolla, jossa tahdistus on halvinta.
6. **Naapurikaistat, naapuriosoitteet.** Yhtenäiset muistihaut ja
   jaetun muistin täyte pankkikonfliktien välttämiseksi.
7. **Älä kiinnitä aliryhmän leveyttä**, ja testaa vähintään kahdella
   leveydellä.
8. **Kilpailu ratkaisee atomisten operaatioiden hinnan**: yksityistä ja
   yhdistä, ja mittaa vinolla datalla.
9. **Pidä data laitteella** ja mittaa siirrot osana kokonaisuutta.
10. **Mittaa kohdelaitteella.** Lavapipe testaa oikeellisuuden; nopeus
    mitataan sillä laitteella, jolle ohjelma tehdään.

## Mihin seuraavaksi

- *Säteenseuranta ja fysikaalinen valaistus*: polunseuranta on luonteva
  GPU-laskennan sovellus, ja sen kiihdytysrakenteet rakennetaan GPU:lla
  lajittelemalla ja skannaamalla.
- *C++:n suorituskyky* ja *Rinnakkaisohjelmointi*: samat primitiivit
  CPU:n säikeillä, muistimalli ja lukottomat rakenteet.
- *Peliohjelmointi*: hiukkaset, fysiikka ja GPU-ohjattu renderöinti
  laskentavarjostimilla.
- Kirjastot ja kehykset: CUB ja Thrust, rocPRIM, oneDPL, Kompute ja
  Vulkan Memory Allocator.

## Lähteet ja jatkolukeminen

Määrittelyt:

- Khronos Group: *Vulkan Specification*, erityisesti luvut
  Dispatching Commands, Synchronization and Cache Control sekä Memory
  Model. <https://docs.vulkan.org/>
- Khronos Group: *GL_KHR_shader_subgroup* -laajennus ja *Vulkan
  Subgroup Tutorial*.
  <https://www.khronos.org/blog/vulkan-subgroup-tutorial>
- Khronos Group: *OpenGL Shading Language 4.60*, laskentavarjostimet ja
  jaettu muisti. <https://registry.khronos.org/OpenGL/>
- Khronos Group: *Synchronization Examples* (Vulkan-Docs wiki).
- Mesa: lavapipe- ja llvmpipe-dokumentaatio.
  <https://docs.mesa3d.org/>

Algoritmit:

- Guy E. Blelloch: *Prefix Sums and Their Applications*. Carnegie
  Mellon University, 1990.
- W. Daniel Hillis ja Guy L. Steele: Data Parallel Algorithms.
  *Communications of the ACM* 29 (12), 1986.
- Kenneth E. Batcher: Sorting Networks and Their Applications.
  *AFIPS Spring Joint Computer Conference*, 1968.
- Mark Harris, Shubhabrata Sengupta ja John D. Owens: Parallel Prefix
  Sum (Scan) with CUDA. *GPU Gems 3*, luku 39. Addison-Wesley 2007.
- Duane Merrill ja Michael Garland: Single-pass Parallel Prefix Scan
  with Decoupled Look-back. NVIDIA Technical Report, 2016.
- Andy Adinets ja Duane Merrill: Onesweep: A Faster Least Significant
  Digit Radix Sort for GPUs. arXiv:2206.01784, 2022.
- Mark Harris: *Optimizing Parallel Reduction in CUDA*. NVIDIA, 2007.

Arkkitehtuuri ja optimointi:

- David B. Kirk, Wen-mei W. Hwu ja Izzat El Hajj: *Programming
  Massively Parallel Processors*, 4. painos. Morgan Kaufmann 2022.
- NVIDIA: *CUDA C++ Programming Guide* ja *CUDA C++ Best Practices
  Guide*. <https://docs.nvidia.com/cuda/>
- AMD GPUOpen: RDNA-arkkitehtuurin optimointioppaat ja FidelityFX
  Parallel Sort. <https://gpuopen.com/>
- Samuel Williams, Andrew Waterman ja David Patterson: Roofline: An
  Insightful Visual Performance Model for Multicore Architectures.
  *Communications of the ACM* 52 (4), 2009.

Tämän tutoriaalin teksti ja esimerkit on kirjoitettu itse. Lähteistä
ei ole kopioitu tekstiä eikä koodia.
