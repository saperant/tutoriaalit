# Lopuksi {.runko-lahteet}

Tutoriaali kulki pikseleistä maailmaan. Ensin kuva oli taulukko, jonka
arvoja suodatettiin ja kynnystettiin. Sitten siitä löydettiin rakenteita:
reunoja, alueita, muotoja ja piirteitä. Geometria liitti kuvat toisiinsa,
kameramalli kuvan maailmaan, ja stereonäkö palautti kolmannen
ulottuvuuden. Jokainen menetelmä testattiin synteettisellä kuvalla,
jonka oikea vastaus tunnettiin. Tämä työtapa kantaa myös oikeisiin
kuviin: tunnettu testikuva, mitattu virhe ja tulos, joka toistuu.

## Nyrkkisäännöt

| Tilanne | Sääntö |
|------------------|--------------------------------------------------|
| koordinaatit | NumPy `[y, x]`, OpenCV `(x, y)`, koko `(leveys, korkeus)` |
| värit | OpenCV on BGR; muunna rajapinnassa |
| laskenta | `float32` ja `np.clip`, ei `uint8`-aritmetiikkaa |
| derivaatat | `CV_32F` tai `CV_16S`, ei `CV_8U` |
| värikynnystys | HSV; punainen kahdella välillä |
| vaihteleva valaistus | adaptiivinen kynnystys tai CLAHE |
| kohina | Gauss: Gauss tai bilateraalinen; impulssit: mediaani |
| pienennys | `INTER_AREA` tai `pyrDown`; maskit `INTER_NEAREST` |
| `filter2D` | korrelaatio; käännä ydin konvoluutiota varten |
| Canny | tasoita ensin; yläkynnys 2–3 x alakynnys |
| maskien siistiminen | avaus, sitten sulkeminen |
| piirteet | ORB oletuksena, SIFT vaikeisiin; ratio-testi ja RANSAC aina |
| muunnokset | yksinkertaisin riittävä; yhdistä matriisit, näytteistä kerran |
| kalibrointi | monta asentoa, koko kuva-ala; virhe alle 0,5 px |
| stereo | $Z = fB/d$; virhe kasvaa etäisyyden neliössä |
| seuranta | kulmapisteet, mediaani, Kalman puuttuville havainnoille |
| suorituskyky | ei pikselisilmukoita Pythonissa; mittaa ennen C++:aa |
| arviointi | erillinen testijoukko käyttötilanteesta; sekaannusmatriisi |
| testaus | synteettinen kuva tunnetulla vastauksella, toleranssit |

## Lähitaidot taitopuussa

- *Signaalit ja järjestelmät* ja *Digitaalinen signaalinkäsittely*
  antavat suodatukselle ja näytteistykselle teorian, jota tässä
  sovellettiin kahteen ulottuvuuteen.
- *Renderöinnin perusteet* ja *Säteenseuranta ja fysikaalinen
  valaistus* tekevät käänteisen tehtävän: kuvan näkymästä. Synteettinen
  kamera on niiden ja konenäön yhteinen työkalu.
- *GPU-laskenta* kiihdyttää kuvankäsittelyä ja neuroverkkojen päättelyä.
- *Lineaarialgebra* sekä *Todennäköisyys ja tilastot* ovat geometrian,
  RANSACin ja Kalman-suotimen perusta.
- Koneoppimisesta ja neuroverkoista ei ole vielä omaa taitoa
  taitopuussa. Luku 11 käsitteli rajapinnan, jossa klassinen konenäkö ja
  opetettu malli kohtaavat.

## Lähteet ja lisälukemista

- Richard Szeliski: *Computer Vision: Algorithms and Applications*,
  2. painos. Springer, 2022. Verkossa vapaasti luettavissa
  <https://szeliski.org/Book/>. Alan kattavin oppikirja: kuvankäsittely,
  piirteet, geometria, stereo ja tunnistus.
- Richard Hartley ja Andrew Zisserman: *Multiple View Geometry in
  Computer Vision*, 2. painos. Cambridge University Press, 2004.
  Homografia, epipolaarigeometria, kalibrointi ja DLT.
- Rafael C. Gonzalez ja Richard E. Woods: *Digital Image Processing*,
  4. painos. Pearson, 2018. Suodatus, morfologia ja segmentointi.
- Gary Bradski ja Adrian Kaehler: *Learning OpenCV*. O'Reilly, 2008.
  OpenCV:n alkuperäisten kehittäjien kirja.
- OpenCV:n dokumentaatio ja oppaat, <https://docs.opencv.org/>.
- Nobuyuki Otsu: A threshold selection method from gray-level
  histograms. *IEEE Transactions on Systems, Man, and Cybernetics* 9
  (1979), 62–66.
- John Canny: A computational approach to edge detection. *IEEE
  Transactions on Pattern Analysis and Machine Intelligence* 8 (1986),
  679–698.
- Chris Harris ja Mike Stephens: A combined corner and edge detector.
  *Alvey Vision Conference*, 1988.
- Jianbo Shi ja Carlo Tomasi: Good features to track. *IEEE Conference
  on Computer Vision and Pattern Recognition*, 1994.
- David G. Lowe: Distinctive image features from scale-invariant
  keypoints. *International Journal of Computer Vision* 60 (2004),
  91–110.
- Ethan Rublee, Vincent Rabaud, Kurt Konolige ja Gary Bradski: ORB: an
  efficient alternative to SIFT or SURF. *IEEE International Conference
  on Computer Vision*, 2011.
- Martin A. Fischler ja Robert C. Bolles: Random sample consensus.
  *Communications of the ACM* 24 (1981), 381–395.
- Zhengyou Zhang: A flexible new technique for camera calibration.
  *IEEE Transactions on Pattern Analysis and Machine Intelligence* 22
  (2000), 1330–1334.
- Heiko Hirschmüller: Stereo processing by semiglobal matching and
  mutual information. *IEEE Transactions on Pattern Analysis and
  Machine Intelligence* 30 (2008), 328–341.
- Bruce D. Lucas ja Takeo Kanade: An iterative image registration
  technique with an application to stereo vision. *International Joint
  Conference on Artificial Intelligence*, 1981.
- Rudolf E. Kalman: A new approach to linear filtering and prediction
  problems. *Journal of Basic Engineering* 82 (1960), 35–45.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Lähdeteosten tekstiä ei ole kopioitu; niihin viitataan lisälukemistona.
OpenCV on lisensoitu Apache 2.0 -lisenssillä.
