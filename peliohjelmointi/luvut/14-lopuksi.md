# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. Simulaatio etenee kiinteällä askeleella; aika lasketaan
   kokonaislukuina ja ruudun kesto rajataan.
2. Pelilogiikka ei tunne kelloa, ikkunaa eikä grafiikkaa. Se saa
   toiminnot ja `dt`:n.
3. Syöte muunnetaan toiminnoiksi; hyppy kuuluu painallukseen, liike
   pitoon. Anna pelaajalle armoa (puskurointi, kojoottiaika).
4. Determinismi: oma satunnaislukugeneraattori siemenellä, kiinteä
   järjestys ja tarkistussummat. Tallenne ja summa ovat testi.
5. Tilat tilakoneina, kohtaukset pinossa, muutokset ja poistot ruudun
   lopussa.
6. Koostaminen periytymisen sijaan; paljon samanlaisia olioita tiiviinä
   datana.
7. Viittaukset tunnisteilla ja kahvoilla, ei osoittimilla.
8. Törmäykset kahdessa vaiheessa; nopeat kappaleet pyyhkäisytestillä.
   Vasteessa ensin erotus, sitten nopeuden muutos.
9. Semi-implisiittinen Euler ja suunnittelijan kielellä annetut
   parametrit.
10. Tekoälyssä päätös, havainto ja liike erikseen; vastustaja tietää
    vain sen, minkä se näkee.
11. Ei keon varauksia pelisilmukassa; poolit ja areenat.

## Mallit

| Malli | Ratkaisee | Luku |
|-------|-----------|------|
| pelisilmukka, kiinteä askel | laitteistosta riippumaton simulaatio | Pelisilmukka |
| päivitysmenetelmä (update) | olioiden käsittely kerran askeleessa | Pelisilmukka |
| komento | syötteen tallennus ja toisto | Syöte |
| tilakone | toisensa poissulkevat tilat | Pelin tila |
| tapahtumajono | järjestelmien irrotus | Pelin tila |
| komponentti, ECS | kykyjen yhdistelmät, datan asettelu | Entiteetit |
| tila-taulukko (spatial partition) | törmäysparien karsinta | Törmäykset |
| käänteismassa | liikkumattomat kappaleet ilman erikoistapausta | Fysiikka ja törmäysvaste |
| reitinhaku (A\*) | liike esteiden ohi | Pelitekoäly |
| objektipooli | varaukset pelisilmukassa | Resurssit |
| kahva | roikkuvat viittaukset | Resurssit |
| välitön käyttöliittymä | käyttöliittymän tilan synkronointi | Ääni ja käyttöliittymä |
| palvelun paikantaja | globaalien järjestelmien (ääni, loki) haku ilman singletonia | ks. Nystrom |

## Jatkotaidot

- *3D-peliohjelmointi*: kolmiulotteisen pelin rakenne: orientaatiot ja
  kvaterniot, muunnoshierarkia, kamerat, 3D-törmäykset ja animaatio.
- *Pelifysiikka*: jäykät kappaleet, rajoitteet ja nivelet sekä pehmeät
  kappaleet luvun *Fysiikka ja törmäysvaste* jatkoksi.
- *Reaaliaikaiset moninpelit*: tilan synkronointi, asiakkaan ennustus,
  viiveen kompensointi ja rollback. Tämän tutoriaalin determinismi ja
  tallenteet ovat sen perusta.
- *Renderöinnin perusteet* ja *GPU-ohjelmointi: OpenGL ja Vulkan*:
  grafiikkaputki, varjostimet, OpenGL ja Vulkan.
- *C++:n suorituskyky* ja *Suorituskyvyn analyysi ja optimointi*:
  datan asettelu, profilointi ja vektorointi.
- *Algoritmit* ja *Numeeriset menetelmät*: reitinhaun ja
  integraattorien teoria, jota tässä vain käytettiin.

## Lähteet ja lisälukemista

- Robert Nystrom: *Game Programming Patterns*. Genever Benning, 2014.
  Verkkoversio <https://gameprogrammingpatterns.com/>. Lisensoitu
  CC BY-NC-ND 4.0 -lisenssillä, joten siitä ei ole lainattu tekstiä;
  mallien nimet ja jäsennys noudattavat alan vakiintunutta käytäntöä.
- Glenn Fiedler: *Fix Your Timestep!* ja *Integration Basics*.
  <https://gafferongames.com/>. Kiinteän askeleen ja interpoloinnin
  klassinen kuvaus.
- Jason Gregory: *Game Engine Architecture*, 3. painos. CRC Press,
  2018. Moottorin rakenne kokonaisuutena.
- Christer Ericson: *Real-Time Collision Detection*. Morgan Kaufmann,
  2005. Törmäystestit ja laaja vaihe.
- Erin Catto: Box2D-fysiikkamoottori ja GDC-esitykset.
  <https://box2d.org/>.
- Melissa O'Neill: *PCG: A Family of Simple Fast Space-Efficient
  Statistically Good Algorithms for Random Number Generation*, 2014.
  <https://www.pcg-random.org/>.
- Amit Patel: *Red Blob Games*. <https://www.redblobgames.com/>.
  Havainnollisia artikkeleita peleissä käytettävistä algoritmeista,
  muun muassa A\*-reitinhausta.
- SDL2-dokumentaatio: <https://wiki.libsdl.org/>. SDL on
  zlib-lisensoitu.
- EnTT (<https://github.com/skypjack/entt>) ja flecs
  (<https://www.flecs.dev/>): ECS-kirjastot C++:lle ja C:lle.
- Dear ImGui: <https://github.com/ocornut/imgui>. Välitön
  käyttöliittymä kehitystyökaluihin.
- Pelimoottorien dokumentaatio: Godot (<https://docs.godotengine.org/>),
  Unity (<https://docs.unity3d.com/>), Unreal
  (<https://dev.epicgames.com/documentation/>).
