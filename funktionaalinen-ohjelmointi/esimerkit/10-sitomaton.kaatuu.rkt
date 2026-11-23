#lang racket
;; Tulkin virheilmoitus: muuttujaa ei löydy mistään ympäristön kehyksestä.
(require "10-tulkki/tulkki.rkt")

;; @alku virhe
(define g (uusi-globaali))
(arvioi '(define hinta 100) g)
(displayln (arvioi '(* hinta 2) g))
(displayln (arvioi '((lambda (x) (+ x alv)) hinta) g))  ; alv puuttuu
;; @loppu virhe
