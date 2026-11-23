#lang racket
;; Lukee ohjelman syötteestä lauseke kerrallaan ja tulostaa tulokset.
(require "tulkki.rkt")

;; @alku silmukka
(define globaali (uusi-globaali))
(for ([lauseke (in-port read)])
  (define tulos (arvioi lauseke globaali))
  (unless (void? tulos)             ; define ei tuota tulostettavaa arvoa
    (displayln tulos)))
;; @loppu silmukka
