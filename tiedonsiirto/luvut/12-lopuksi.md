# Lopuksi {.runko-lahteet}

Tutoriaali kulki bitistä aaltomuotoon ja takaisin. Kantataajuusmalli
teki radiosignaalista kompleksilukujen jonon, konstellaatio ja
pulssinmuokkaus muuttivat bitit kaistaltaan rajatuksi signaaliksi, ja
sovitettu suodin, synkronointi ja kanavakoodaus palauttivat bitit
kohinasta. Jokainen vaihe tarkistettiin simulaatiolla teoreettista
tulosta vastaan, ja sama periaate pätee oikeisiin järjestelmiin:
simulaatio, jonka tulos osuu teoriaan, on lähtökohta toteutukselle ja
mittauksille.

## Nyrkkisäännöt

| Tilanne | Sääntö |
|--------------|----------------------------------------------|
| kantataajuus | $s(t) = \operatorname{Re}\{x(t)e^{i2\pi f_c t}\}$; teho kaistalla puolet |
| AM | verhokäyräilmaisin vaatii $\mu \le 1$; DSB-SC vaatii vaiheen |
| FM | Carson: $B \approx 2(\Delta f + f_m)$; ilmaisu $\arg(z[n]z^*[n-1])$ |
| konstellaatio | keskienergia 1, Gray-nimiöt; +2 bittiä noin +4–6 dB |
| pulssi | RRC + RRC = RC, ISI nolla; kaista $(1+\beta)/(2T)$ |
| roll-off | 0,2–0,35; pieni $\beta$ vaatii tarkan ajoituksen |
| vastaanottosuodin | sovitettu suodin: SNR $= E_s/N_0$ |
| kohina | $N_0 = E_s / (E_s/N_0)$; tarkista EVM:llä |
| SNR näytteellä | $E_s/N_0 - 10\log_{10}\text{sps}$ |
| BPSK, QPSK | $P_b = Q(\sqrt{2E_b/N_0})$; $10^{-6}$ noin 10,5 dB |
| Shannon | $E_b/N_0 > (2^\eta-1)/\eta$; vähintään $-1{,}59$ dB |
| häipyminen | BER noin $1/(4\,E_b/N_0)$; diversiteetti jyrkentää |
| OFDM | etuliite > kanavan viive; yksi kerroin alikantoaaltoa kohti |
| vaihe ja taajuus | karkea estimaatti alkuosasta, sitten 2. asteen silmukka |
| QPSK:n epävarmuus | tahdistussana tai differentiaalinen koodaus |
| ajoitus | Gardner, 2 näytettä/symboli, interpolointi |
| kehys | alkuosan korrelaation itseisarvo, normitettu kynnys |
| koodaus | vertaa samalla $E_b/N_0$:lla; pehmeä päätös noin +2 dB |
| purskeet | lomitus syvemmäksi kuin purske |
| Monte Carlo | vähintään 100 virhettä; 0 virhettä: BER < $3/n$ |

## Jatkotaidot taitopuussa

- *Ohjelmistoradio* vie tämän tutoriaalin vastaanottimen oikeaan
  radioon: IQ-näytteet laitteelta, IQ-epätasapaino ja tasakomponentti,
  automaattinen vahvistuksen säätö, näytetaajuuden muunnokset ja
  GNU Radion lohkot.
- *DSP-algoritmien laitteistototeutus* toteuttaa RRC-suotimet,
  NCO:n ja silmukat kiinteän pilkun laitteistona.
- *Tietoliikennetekniikka* ja *Tietoverkot* jatkavat ylöspäin
  protokollapinossa: kehykset, kanavanvaraus ja uudelleenlähetykset.

## Lähteet ja lisälukemista

- John G. Proakis ja Masoud Salehi: *Digital Communications*,
  5. painos. McGraw-Hill, 2008. Alan perusteos: modulaatiot,
  optimaaliset vastaanottimet, synkronointi ja koodaus.
- Bernard Sklar: *Digital Communications: Fundamentals and
  Applications*, 2. painos. Prentice Hall, 2001.
- Michael Rice: *Digital Communications: A Discrete-Time Approach*.
  Pearson, 2009. Diskreettiaikainen näkökulma, erinomainen
  symbolitahdistuksen ja vaihelukittujen silmukoiden käsittely.
- Andrea Goldsmith: *Wireless Communications*. Cambridge University
  Press, 2005. Häipyvät kanavat, diversiteetti ja OFDM.
- David Tse ja Pramod Viswanath: *Fundamentals of Wireless
  Communication*. Cambridge University Press, 2005. Verkossa
  <https://web.stanford.edu/~dntse/wireless_book.html>.
- Umberto Mengali ja Aldo N. D'Andrea: *Synchronization Techniques for
  Digital Receivers*. Plenum, 1997.
- Floyd M. Gardner: A BPSK/QPSK timing-error detector for sampled
  receivers. *IEEE Transactions on Communications* 34 (1986), 423–429.
- Shu Lin ja Daniel J. Costello: *Error Control Coding*, 2. painos.
  Pearson, 2004.
- Andrew J. Viterbi: Error bounds for convolutional codes and an
  asymptotically optimum decoding algorithm. *IEEE Transactions on
  Information Theory* 13 (1967), 260–269.
- Claude E. Shannon: A mathematical theory of communication. *Bell
  System Technical Journal* 27 (1948), 379–423 ja 623–656.
- Marc Lichtman: *PySDR: A Guide to SDR and DSP using Python*.
  Verkossa <https://pysdr.org/> (CC BY-NC-SA).
- SciPyn signaalinkäsittelyn ja erikoisfunktioiden dokumentaatio,
  <https://docs.scipy.org/doc/scipy/reference/signal.html>.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Lähdeteosten tekstiä ei ole kopioitu; niihin viitataan lisälukemistona.
