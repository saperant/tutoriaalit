# Lopuksi {.runko-lahteet}

Tutoriaalin osat olivat pieniä, mutta niiden rakenne on sama kuin
suurissa peleissä ja pelimoottoreissa. Tämä luku kertoo, missä ne
näkyvät moottoreissa, kokoaa nyrkkisäännöt ja ohjaa eteenpäin.

## Samat osat pelimoottorissa

Pelimoottori tarjoaa tämän tutoriaalin asiat valmiina komponentteina.
Niiden asetukset ovat tuttuja, kun tietää, mitä alla tapahtuu:
hahmo-ohjaimen "suurin käveltävä kulma" on normaalin y-komponentin
raja, ja kameran jousivarsi on säde kohteesta kameraan.

| Tutoriaalissa | Godot 4 | Unity | Unreal Engine 5 |
|------------------|------------------------|------------------------|----------------------------------|
| asento | `Quaternion`, `Basis` | `Quaternion` | `FQuat`; `FRotator` on Eulerin kulmat |
| muunnoshierarkia | `Node3D`-puu | `Transform`-hierarkia | komponenttien kiinnitykset |
| törmäysmuodot | `CollisionShape3D` | `Collider`-komponentit | törmäysprimitiivit |
| säteenheitto | `intersect_ray` | `Physics.Raycast` | `LineTraceSingleByChannel` |
| hahmo-ohjain | `CharacterBody3D` | `CharacterController` | `UCharacterMovementComponent` |
| kameran törmäys | `SpringArm3D` | Cinemachine | `USpringArmComponent` |
| luuranko ja sekoitus | `Skeleton3D`, `AnimationTree` | Animator, Blend Tree | Animation Blueprint, Blend Space |
| glTF | tuonti sisäänrakennettu | lisäpaketti | tuonti sisäänrakennettu |

Moottori tekee lisäksi näkyvyyskarsinnan, laajan vaiheen ja
skinnauksen itse. Se ei kuitenkaan päätä, missä järjestyksessä pelin
omat osat ajetaan, eikä se korjaa vääriä oletuksia. Tavallisimmat
kolmiulotteisen pelin virheet moottorilla tehtynä ovat samat kuin
ilman: Eulerin kulmien interpolointi, pehmennys kiinteällä kertoimella,
kamera, joka päivitetään ennen hahmoa, epäyhtenäinen skaala
fysiikkakappaleen vanhemmassa ja koordinaatiston tai yksikön
sekaannus tuonnissa.

## Nyrkkisäännöt

| Tilanne | Sääntö |
|---------|--------|
| asennon tallennus | kvaternio; Eulerin kulmat vain kameralle ja editorille |
| kertyvä kierto | normalisoi joka päivityksen jälkeen |
| interpolointi | TRS-muodossa: lerp sijainnille, slerp tai nlerp kierrolle |
| hierarkia | paikallinen muunnos on tila, maailmamatriisi välimuisti |
| vanhemman vaihto | säilytä maailmamuunnos käänteismatriisilla |
| törmäysmuoto | yksinkertaisin, joka riittää: pallo, kapseli, laatikko |
| törmäystesti | lähin piste ja säde; palauta normaali ja syvyys |
| nopea kappale | säde tai pyyhkäisy, ei paikkatesti |
| monta kohdetta | tilarakenne; tarkista tulos raakaa hakua vastaan |
| pelaajan hahmo | kinemaattinen kapseli omilla säännöillään |
| pehmennys | `1 - exp(-nopeus * dt)`, ei kiinteää kerrointa |
| kamera | päivitä hahmon jälkeen; estä seinän läpi näkeminen säteellä |
| karsinta | varovainen: epävarma kappale piirretään |
| animaatio | sekoita pooseja, ei matriiseja |
| resurssi | epäluotettavaa syötettä: tarkista jokainen indeksi |
| testaus | tallennettu syöte ja tekstiloki; kuva vianetsintään |

## Jatkotaidot

- *Pelifysiikka*: voimat ja vääntömomentit, jäykän kappaleen
  dynamiikka, kosketusten ratkaisu, nivelet ja pehmeät kappaleet.
  Jatkaa suoraan tämän tutoriaalin törmäysmuodoista ja kvaternioista.
- *GPU-ohjelmointi: OpenGL ja Vulkan*: saman kohtauksen piirtäminen
  näytönohjaimella, skinnaus verteksivarjostimessa ja piirtolistan
  lähettäminen grafiikkarajapinnalle.
- *Säteenseuranta ja fysikaalinen valaistus*: BVH:n tehokkaat
  rakennus- ja läpikäyntitavat valon simuloinnissa.
- *Reaaliaikaiset moninpelit*: hahmon tilan ennustus ja täsmäytys
  verkon yli; kinemaattinen ohjain ja tallennettu syöte ovat sen
  lähtökohta.
- *C++:n suorituskyky*: datan asettelu, kun kappaleita on kymmeniä
  tuhansia.

## Lähteet ja jatkolukeminen

Kirjat:

- Christer Ericson: *Real-Time Collision Detection*. Morgan
  Kaufmann, 2005. Törmäystestien ja tilarakenteiden perusteos;
  lähimmän pisteen menetelmät ja BVH.
- Jason Gregory: *Game Engine Architecture*, 3. painos. CRC
  Press, 2018. Pelimoottorin osat kokonaisuutena: näkymägraafi,
  animaatio, hahmo-ohjain ja resurssiputki.
- Eric Lengyel: *Foundations of Game Engine Development, Volume 1:
  Mathematics*. Terathon Software, 2016. Kvaterniot ja muunnokset.
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman ja muut: *Real-Time
  Rendering*, 4. painos. CRC Press, 2018. Näkyvyyskarsinta ja
  leikkaustestit renderöinnin näkökulmasta.

Artikkelit:

- Ken Shoemake: *Animating Rotation with Quaternion Curves*.
  SIGGRAPH 1985. Slerpin alkuperäinen esitys.
- Jonathan Blow: *Understanding Slerp, Then Not Using It*. Game
  Developer Magazine, 2004. Perustelu nlerpin käytölle.
- Tomas Möller ja Ben Trumbore: *Fast, Minimum Storage Ray-Triangle
  Intersection*. Journal of Graphics Tools, 1997.
- Gil Gribb ja Klaus Hartmann: *Fast Extraction of Viewing Frustum
  Planes from the World-View-Projection Matrix*, 2001.
- Kasper Fauerby: *Improved Collision Detection and Response*, 2003.
  Hahmon liukuminen kolmioverkossa.

Määrittelyt ja kirjastot:

- Khronos Group: *glTF 2.0 Specification*,
  <https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html>.
- Niels Lohmann: *JSON for Modern C++*,
  <https://github.com/nlohmann/json> (MIT-lisenssi).
- Pelimoottorien dokumentaatio: <https://docs.godotengine.org>,
  <https://docs.unity3d.com> ja <https://dev.epicgames.com/documentation>.

Tutoriaalin koodi on kirjoitettu tätä tutoriaalia varten. Algoritmit
ovat alan yleisesti tunnettuja menetelmiä, jotka on toteutettu
lähteissä kuvattujen periaatteiden pohjalta.
