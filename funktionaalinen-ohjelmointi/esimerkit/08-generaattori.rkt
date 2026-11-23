#lang racket
;; Generaattori tuottaa arvoja yksi kerrallaan ja jatkaa siitä, mihin
;; jäi. Racketissa se on toteutettu jatkeilla (continuation), samalla
;; mekanismilla, josta Pythonin yield ja async/await ovat sukua.
(require racket/generator)

;; @alku puu
;; Binääripuu: #f tai (solmu vasen arvo oikea).
(struct solmu (vasen arvo oikea))

(define (lisaa puu x)
  (match puu
    [#f (solmu #f x #f)]
    [(solmu v a o) (if (< x a)
                       (solmu (lisaa v x) a o)
                       (solmu v a (lisaa o x)))]))

;; Sisäjärjestyksen läpikäynti: rekursio pysyy luonnollisena, ja kutsuja
;; saa arvot yksi kerrallaan.
(define (sisajarjestys puu)
  (generator ()
    (let kay ([p puu])
      (when p
        (kay (solmu-vasen p))
        (yield (solmu-arvo p))
        (kay (solmu-oikea p))))
    (yield (void))))                    ; loppumerkki
;; @loppu puu

;; @alku kaytto
(define puu (foldl (λ (x p) (lisaa p x)) #f '(50 30 70 20 40 60 80)))

;; Kolme pienintä: läpikäynti pysähtyy, loppua puusta ei käydä läpi.
(displayln (for/list ([x (in-producer (sisajarjestys puu) (void))]
                      [_ (in-range 3)])
             x))
;; @loppu kaytto
