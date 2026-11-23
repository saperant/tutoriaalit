#lang racket
;; Pysyvät (persistent) tietorakenteet: jokainen muutos tuottaa uuden
;; version, ja vanhat versiot jäävät käyttöön. Kumoaminen on ilmaista.

;; @alku ostoskori
(struct kori (rivit alennus) #:transparent)  ; rivit: tuote → kpl

(define (lisaa k tuote [kpl 1])
  (struct-copy kori k
               [rivit (hash-update (kori-rivit k) tuote
                                   (λ (n) (+ n kpl)) 0)]))

(define (poista k tuote)
  (struct-copy kori k [rivit (hash-remove (kori-rivit k) tuote)]))

(define (aseta-alennus k prosentti)
  (struct-copy kori k [alennus prosentti]))
;; @loppu ostoskori

;; @alku historia
;; Historia on lista versioita, uusin ensin. Kumoa = pudota ensimmäinen.
(define (tee historia muutos . argumentit)
  (cons (apply muutos (first historia) argumentit) historia))
(define (kumoa historia) (rest historia))

(define (nayta k)
  (define rivit (sort (hash->list (kori-rivit k)) string<? #:key car))
  (printf "~a alennus ~a %\n" rivit (kori-alennus k)))

(define h0 (list (kori (hash) 0)))
(define h1 (tee h0 lisaa "kahvi" 2))
(define h2 (tee h1 lisaa "pulla" 3))
(define h3 (tee h2 aseta-alennus 10))
(define h4 (tee h3 poista "kahvi"))

(for-each nayta (reverse h4))
(nayta (first (kumoa (kumoa h4))))
;; Muuttumaton osa jaetaan versioiden kesken, sitä ei kopioida.
(displayln (eq? (kori-rivit (first h3)) (kori-rivit (first h2))))
;; @loppu historia
