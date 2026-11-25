#lang racket
;; Hajautustaulun perusoperaatiot. Muuttumaton taulu (hash) palauttaa
;; muutoksesta uuden taulun; muuttuva (make-hash) muuttaa paikallaan.

;; @alku muuttumaton
(define varasto (hash "kahvi" 2 "pulla" 3))

(displayln (hash-ref varasto "kahvi"))        ; haku
(displayln (hash-ref varasto "tee" 0))        ; oletusarvo puuttuvalle
(define v2 (hash-set varasto "tee" 5))        ; lisäys tai korvaus
(define v3 (hash-update v2 "kahvi" add1))     ; arvo funktion läpi
(define v4 (hash-update v3 "mehu" add1 0))    ; puuttuvalle oletus 0
(define v5 (hash-remove v4 "pulla"))

(displayln (for/sum ([(tuote kpl) (in-hash v5)]) kpl))  ; läpikäynti
(displayln (sort (hash->list v5) string<? #:key car))
(displayln (sort (hash->list varasto) string<? #:key car))  ; ennallaan
;; @loppu muuttumaton

;; @alku muuttuva
;; Muuttuva taulu on paikallista tilaa varten (luku 9). Operaatioiden
;; nimessä on huutomerkki.
(define laskuri (make-hash))
(for ([sana (in-list '("a" "b" "a"))])
  (hash-update! laskuri sana add1 0))
(displayln (sort (hash->list laskuri) string<? #:key car))
;; @loppu muuttuva
