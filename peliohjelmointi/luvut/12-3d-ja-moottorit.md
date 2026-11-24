# 3D ja pelimoottorit

3D-peli rakentuu samoista osista kuin 2D-peli: kiinteä askel, syöte,
tilat, entiteetit, törmäykset ja resurssit. Uutta ovat muunnosten
hierarkia, kamera ja projektio sekä grafiikkaputki, joka piirtää
kolmioita näytönohjaimella. Tässä luvussa käydään läpi, miten peli
liittyy renderöintiin, ja mitä pelimoottori tekee puolestasi.

## Näkymäpuu

Pelimaailman oliot ovat hierarkiassa: pyörä kuuluu autoon, auto
lautalle ja lautta maailmaan. Jokaisella solmulla on *paikallinen
muunnos* vanhempansa koordinaatistossa. *Maailmamuunnos* saadaan
kertomalla muunnokset juuresta alas.

```{.cpp tiedosto="esimerkit/12-nakymapuu.cpp" osa="matriisi"}
```

```{.cpp tiedosto="esimerkit/12-nakymapuu.cpp" osa="puu"}
```

Kun solmut ovat taulukossa vanhemmat ennen lapsia, yksi läpikäynti
riittää, ja muisti luetaan järjestyksessä. Moottorit päivittävät vain
muuttuneet haarat (*likaisuuslippu*, dirty flag).

## Kamera ja projektio

Kamera on käänteinen muunnos: maailma siirretään kameran
koordinaatistoon, jossa kamera on origossa ja katsoo −z-suuntaan.
Perspektiivi jakaa koordinaatit syvyydellä, jolloin kaukaiset kappaleet
pienenevät ja lähestyvät ruudun keskustaa.

```{.cpp tiedosto="esimerkit/12-nakymapuu.cpp" osa="projektio"}
```

```{.tuloste tiedosto="esimerkit/12-nakymapuu.odotettu"}
```

Kun lauttaa käännetään 90 astetta, auto ja pyörä liikkuvat mukana,
vaikka niiden paikallisia muunnoksia ei muutettu. Kauempana oleva auto
piirtyy lähemmäs ruudun keskustaa. Oikeassa renderöinnissä
projektiomatriisi kuvaa myös syvyyden z-puskuria varten, ja
näytönohjain tekee jaon (taidot *Renderöinnin perusteet* ja
*GPU-ohjelmointi*).

## Pelin ja renderöinnin raja

Peli ei kutsu OpenGL:ää tai Vulkania pelilogiikasta. Pelin tila
muunnetaan joka ruudulla *piirtolistaksi*: mitä malleja piirretään,
millä materiaaleilla ja muunnoksilla. Renderöijä lajittelee listan
(läpinäkymättömät edestä taakse, läpinäkyvät takaa eteen, materiaalin
mukaan) ja piirtää sen. Raja mahdollistaa renderöinnin omassa
säikeessään ja interpoloinnin kiinteän askeleen ja näytön välillä.

## Mitä pelimoottori tekee

| Tutoriaalin rakenne | Godot | Unity | Unreal |
|---------------------|-------|-------|--------|
| kiinteä askel | `_physics_process` | `FixedUpdate` | fysiikan alaskeleet |
| piirto ja interpolointi | `_process` | `Update`, interpolointi | `Tick` |
| entiteetit ja komponentit | solmupuu | GameObject, DOTS | Actor, Component |
| kohtaukset | scene | Scene | Level |
| tapahtumat | signaalit | tapahtumat | delegaatit |
| resurssit ja kuumalataus | resurssit, tuonti | AssetDatabase | Asset Registry |
| skriptaus | GDScript, C# | C# | C++, Blueprint |

Moottori tuo valmiina editorin, resurssien tuontiputken, fysiikan,
animaation, äänen, käyttöliittymän, verkon ja julkaisun monelle
alustalle. Se ei kuitenkaan tee pelistä determinististä, ei päätä
datan asettelua eikä korjaa väärin valittua päivitysvaihetta: liike
`Update`-vaiheessa ilman `dt`:tä ja fysiikka muualla kuin kiinteässä
vaiheessa ovat moottoripelien yleisimpiä virheitä.

Moottorin valinta:

- **Godot** (MIT-lisenssi): kevyt, avoin, 2D:ssä vahva, solmupuuhun
  perustuva arkkitehtuuri.
- **Unity**: laaja ekosysteemi ja mobiilituki, C#-skriptaus, DOTS
  suurille oliomäärille.
- **Unreal**: korkealaatuinen 3D-renderöinti, C++ ja visuaalinen
  Blueprint-kieli, raskas mutta kattava.
- **Oma moottori tai kehys** (SDL, raylib, bgfx): täysi hallinta ja
  pieni koko, mutta editori ja työkalut tehdään itse.

## Käytännössä

- **Muunnoshierarkia taulukkona** vanhemmat ennen lapsia, ja vain
  muuttuneet haarat päivitetään.
- **Piirtolista** erottaa pelin tilan renderöinnistä; peli ei sisällä
  grafiikkarajapinnan kutsuja.
- **Moottorin vaiheet oikein:** syöte ja liike kiinteässä vaiheessa,
  kamera ja efektit piirtovaiheessa.
- **Moottori ei vapauta suunnittelusta:** datan asettelu, determinismi
  ja resurssien elinkaari ovat moottorissakin pelin vastuulla.

## Itsearviointi

- Osaat laskea näkymäpuun maailmamuunnokset ja selittää, miksi taulukko
  vanhemmat ennen lapsia riittää yhteen läpikäyntiin.
- Osaat muuntaa pisteen maailmasta ruudulle kameran ja perspektiivin
  avulla.
- Osaat kertoa, mitä pelimoottori tekee pelisilmukan, entiteettien ja
  resurssien osalta, ja nimetä tyypilliset moottorikäytön virheet.
