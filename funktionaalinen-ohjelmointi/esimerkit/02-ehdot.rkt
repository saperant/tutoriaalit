#lang racket
;; Kaikki on lauseke: if, cond ja let palauttavat arvon.

;; @alku cond
(define (luokittele lampotila)
  (cond [(< lampotila -20) "paukkupakkanen"]
        [(< lampotila 0) "pakkanen"]
        [(< lampotila 15) "viileä"]
        [else "lämmin"]))

(for ([t (in-list '(-25 -3 8 21))])
  (printf "~a: ~a\n" t (luokittele t)))
;; @loppu cond

;; @alku totuus
;; Vain #f on epätosi. Tyhjä lista, 0 ja "" ovat tosia.
(displayln (if '() "tosi" "epätosi"))
(displayln (if 0 "tosi" "epätosi"))
;; or palauttaa ensimmäisen toden arvon: oletusarvo ilman if-lausetta.
(define asetukset (hash 'portti 8080))
(displayln (or (hash-ref asetukset 'isanta #f) "localhost"))
;; @loppu totuus

;; @alku let
(define (hypotenuusa a b)
  (let* ([a2 (* a a)]                 ; let* näkee edelliset sidonnat
         [b2 (* b b)])
    (sqrt (+ a2 b2))))
(displayln (hypotenuusa 3 4))
;; @loppu let

;; @alku yhtasuuruus
(displayln (equal? (list 1 2) (list 1 2)))  ; rakenne sama: #t
(displayln (eq? (list 1 2) (list 1 2)))     ; sama olio: #f
(displayln (= 1 1.0))                       ; lukuarvo sama: #t
(displayln (equal? 1 1.0))                  ; tarkka ≠ epätarkka: #f
;; @loppu yhtasuuruus
