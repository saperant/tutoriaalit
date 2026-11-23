#lang racket
;; Sopimus tarkistaa arvot moduulin rajalla ja kertoo, kumpi osapuoli
;; rikkoi sen (blame).

;; @alku sopimus
(module laskut racket
  (provide (contract-out
            [alv-osuus (-> (and/c rational? (>=/c 0)) rational?)]))
  (define (alv-osuus verollinen)
    (* verollinen 255/1255)))

(require 'laskut)
(displayln (alv-osuus 1255))      ; 255
(displayln (alv-osuus "100"))     ; merkkijono: kutsuja rikkoo sopimuksen
;; @loppu sopimus
