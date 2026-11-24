# Lopuksi {.runko-lahteet}

Tutoriaali kulki yhden työnkulun läpi monta kertaa: vaatimus,
suunnittelu SciPyllä, tarkistus, C-toteutus, jonka tila on kutsujan
muistissa, ja vertailu referenssiin toleranssilla, joka on valittu
rakenteen mukaan. Kiinteässä pilkussa vertailu tehtiin bitilleen.
Sama kaava toimii uusillekin algoritmeille: kun toteutuksella on
riippumaton referenssi ja testit kattavat lohkokoot ja rajatapaukset,
signaalinkäsittelyn hiljaiset virheet löytyvät ennen laitetta.

## Nyrkkisäännöt

| Tilanne | Sääntö |
|----------------|--------------------------------------------------|
| vaatimus | kaistat, aaltoilu, vaimennus; tietorakenteena, tarkistusfunktio listana |
| FIR, nopea suunnittelu | Kaiser: `kaiserord` + `firwin`, iteroi pituutta |
| FIR, vähiten laskentaa | `remez`, painot $\delta_p/\delta_s$, tarkista siirtymäkaista |
| mielivaltainen vaste | `firwin2` |
| lineaarinen vaihe | symmetrinen, pariton pituus (tyyppi I) |
| FIR-pituuden arvio | $N \approx (A - 8)/(2{,}285 \cdot 2\pi\,\Delta f)$ |
| IIR | `ellip`/`butter` + `output="sos"`, aina toisen asteen lohkoina |
| analoginen malli | bilineaari, esivääristys $2 f_s \tan(\pi f_c/f_s)$ |
| biquad laitteessa | Bristow-Johnsonin kaavat; DF2T liukuluvuilla, DF1 kiinteällä pilkulla |
| kiinteä pilkku | Q2.14 riittämätön pienille rajataajuuksille; testaa nollasyöte |
| pitkä FIR | overlap-save, FFT noin 4 × suotimen pituus |
| muutama taajuus | Goertzel |
| desimointi | suodata ensin; polyfaasi tai vain tarvittavat ulostulot |
| interpolointi | vahvistus $L$; älä kerro nollia |
| suuri desimointi | CIC + korjaava FIR; $B + N\log_2 R$ bittiä |
| adaptiivinen | NLMS, $\mu$ noin kymmenesosa rajasta, viite ei korreloi hyötysignaalin kanssa |
| reaaliaika | ei muistinvarausta, lukkoja eikä I/O:ta; jonot laitteen ja käsittelyn välillä |
| testaus | lohkoittain = kerralla; C vs. Python toleranssilla; kiinteä pilkku bitilleen |

## Jatkotaidot taitopuussa

- *DSP-algoritmien laitteistototeutus* vie tämän tutoriaalin FIR- ja
  biquad-rakenteet, polyfaasisuotimet ja CIC:n laitteistoksi: kiinteän
  pilkun sanaleveydet, liukuhihnoitus ja verifiointi bittitarkkaa mallia
  vastaan.
- *Digitaalinen tiedonsiirto* käyttää pulssinmuokkaussuotimia,
  sovitettua suodinta, monitaajuuskäsittelyä ja adaptiivisia
  kanavakorjaimia.
- *Ohjelmistoradio* soveltaa desimointia, CIC-suotimia, kompleksisia
  IQ-signaaleja ja FFT-pohjaista spektrianalyysia.
- *Reaaliaikakäyttöjärjestelmät* ja *Mikrokontrollerit ja
  bare-metal-ohjelmointi* tarjoavat ympäristön, jossa luvun 11
  silmukka ajetaan oikeassa laitteessa.

## Lähteet ja lisälukemista

- Alan V. Oppenheim ja Ronald W. Schafer: *Discrete-Time Signal
  Processing*, 3. painos. Pearson, 2010. Suodinsuunnittelu,
  bilineaarimuunnos, rakenteet ja kvantisointi, FFT-algoritmit.
- Richard G. Lyons: *Understanding Digital Signal Processing*,
  3. painos. Prentice Hall, 2010. Käytännönläheinen: CIC, Goertzel,
  polyfaasisuotimet.
- Fredric J. Harris: *Multirate Signal Processing for Communication
  Systems*. Prentice Hall, 2004. Polyfaasirakenteet ja
  näytetaajuuden muunnos.
- P. P. Vaidyanathan: *Multirate Systems and Filter Banks*. Prentice
  Hall, 1993.
- Simon Haykin: *Adaptive Filter Theory*, 5. painos. Pearson, 2013.
  LMS, NLMS, RLS ja niiden analyysi.
- Bernard Widrow ja Samuel D. Stearns: *Adaptive Signal Processing*.
  Prentice Hall, 1985.
- Julius O. Smith III: *Introduction to Digital Filters with Audio
  Applications*. W3K Publishing, 2007. Verkossa
  <https://ccrma.stanford.edu/~jos/filters/>. Suoramuodot ja niiden
  numeriikka.
- Steven W. Smith: *The Scientist and Engineer's Guide to Digital Signal
  Processing*. California Technical Publishing, 1997. Verkossa
  <https://www.dspguide.com/>.
- James F. Kaiser: Nonrecursive digital filter design using the I0-sinh
  window function. *Proc. IEEE International Symposium on Circuits and
  Systems* (1974), 20–23.
- Thomas W. Parks ja James H. McClellan: Chebyshev approximation for
  nonrecursive digital filters with linear phase. *IEEE Transactions on
  Circuit Theory* 19 (1972), 189–194.
- Eugene B. Hogenauer: An economical class of digital filters for
  decimation and interpolation. *IEEE Transactions on Acoustics, Speech,
  and Signal Processing* 29 (1981), 155–162.
- Robert Bristow-Johnson: *Audio EQ Cookbook*. W3C:n julkaisemana
  verkossa <https://www.w3.org/TR/audio-eq-cookbook/>.
- SciPyn signaalinkäsittelyn dokumentaatio,
  <https://docs.scipy.org/doc/scipy/reference/signal.html>.
- Arm CMSIS-DSP -kirjasto, <https://github.com/ARM-software/CMSIS-DSP>.
  Optimoidut FIR-, biquad-, FFT- ja LMS-toteutukset Cortex-M-
  prosessoreille.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Lähdeteosten tekstiä ei ole kopioitu; niihin viitataan lisälukemistona.
Bristow-Johnsonin kaavat ovat yleisesti käytettyjä matemaattisia
tuloksia, ja niiden C-toteutus on kirjoitettu tätä tutoriaalia varten.
