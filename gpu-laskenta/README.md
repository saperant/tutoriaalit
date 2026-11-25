# GPU-laskenta

Tiivis suomenkielinen tutoriaali yleiskäyttöisestä laskennasta
näytönohjaimella Vulkanin laskentavarjostimilla: laskentaputki ja
työryhmät, push- ja erikoistusvakiot, GPU:n suoritusmalli (aliryhmät,
hajaantuminen, käyttöaste), rinnakkaiset primitiivit (reduktio,
prefiksisumma, virran tiivistys, histogrammi, bitoninen ja
kantalukulajittelu), muistihierarkia (yhtenäiset haut,
pankkikonfliktit, laatoitus), synkronointi ja suorituskyvyn
mittaaminen aikaleimoilla.
Valmiit dokumentit:
[gpu-laskenta.pdf](https://saperant.github.io/tutoriaalit/materiaalit/gpu-laskenta.pdf)
ja pikaopas
[gpu-laskenta-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/gpu-laskenta-pikaopas.pdf).

Esitiedot: GPU-ohjelmointi (Vulkanin perusteet) ja Suorituskyvyn
analyysi ja optimointi (roofline, mittaaminen).

## Sisältö

1. Johdanto – rajapinnat, testaus lavapipellä, ensimmäinen laskenta
2. Laskentavarjostimet – työryhmät, putki ja kuvaajat, reunat,
   push- ja erikoistusvakiot
3. GPU:n suoritusmalli – aliryhmät ja niiden operaatiot,
   hajaantuminen, viiveen piilotus ja käyttöaste
4. Reduktio – atominen, puu jaetussa muistissa, aliryhmät,
   liukulukujen laskujärjestys
5. Prefiksisumma – Hillis–Steele, Blelloch, monitasoinen skannaus,
   virran tiivistys
6. Atomiset operaatiot ja histogrammi – kilpailu ja yksityistäminen
7. Lajittelu – bitoninen verkko ja vakaa kantalukulajittelu
8. GPU:n muistihierarkia – yhtenäiset haut, pankkikonfliktit,
   transpoosi ja matriisitulo
9. Työn jako ja synkronointi – esteet työryhmässä ja ajojen välillä,
   synkronoinnin validointi
10. Suorituskyvyn mittaaminen – aikaleimat, siirrot, roofline,
    profiloijat, CUDA, OpenCL ja SYCL
11. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

`esimerkit/` sisältää 12 C++23-ohjelmaa (GCC 14, Clang tarkistaa
varoitukset), 24 GLSL-laskentavarjostinta (`varjostimet/`) ja pienen
apukirjaston (`yhteinen/`). Ne ajetaan ilman näytönohjainta Mesan
lavapipe-ajurilla validointikerroksen kanssa. Jokainen ohjelma tekee
saman työn myös CPU:lla ja tulostaa vertailun, jota verrataan
tiedostoon `<nimi>.odotettu`. Ajat tulostetaan vain mittaustilassa.

```text
cd esimerkit
make               # varjostimet, ohjelmat, ajot ja vertailu
make aja-07-kantaluku
make mittaa        # ajat GPU:n aikaleimoilla (vaihtelevat koneittain)
```

Tarvittavat paketit (Ubuntu 24.04): `libvulkan-dev
mesa-vulkan-drivers vulkan-validationlayers glslc`, valinnaisesti
`spirv-tools`. Kehityskontissa (`.devcontainer/gpu-laskenta`) ne ovat
valmiina.

## Rakentaminen

`make testaa` tarkistaa rakenteen ja ajaa esimerkit, `make pdf`
rakentaa PDF:t ja `make kuvat` piirtää algoritmien periaatekuvat
(Matplotlib).

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
