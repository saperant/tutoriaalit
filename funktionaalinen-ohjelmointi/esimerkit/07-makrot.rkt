#lang racket
;; Makro muuntaa koodia ennen arviointia. Se pystyy siihen, mihin funktio
;; ei pysty: viivästämään arviointia ja näkemään argumenttinsa koodina.

;; @alku tarkista
;; Funktio saisi vain arvon #f. Makro näkee lausekkeen tekstinä, kuten
;; C:n assert(#expr), mutta ilman esikääntäjän tekstikorvausta.
(define-syntax-rule (varmista ehto)
  (unless ehto
    (printf "varmistus epäonnistui: ~s\n" 'ehto)))

(define saldo 40)
(varmista (>= saldo 0))
(varmista (> saldo 100))
;; @loppu tarkista

;; @alku vaihda
(define-syntax-rule (vaihda! a b)
  (let ([tmp a])
    (set! a b)
    (set! b tmp)))

(define tmp 1)                 ; sama nimi kuin makron apumuuttujalla
(define toinen 2)
(vaihda! tmp toinen)           ; hygienia: nimet eivät sekoitu
(displayln (list tmp toinen))
;; @loppu vaihda

;; @alku silmukka
;; syntax-rules ja ellipsi (...): uusi ohjausrakenne kieleen.
(define-syntax kunnes
  (syntax-rules ()
    [(_ ehto runko ...)
     (let silmukka ()
       (unless ehto
         runko ...
         (silmukka)))]))

(define n 1)
(kunnes (> n 100)
  (set! n (* n 3)))
(displayln n)
;; @loppu silmukka
