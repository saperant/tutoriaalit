#lang racket
;; Sulkeuma: funktio, joka muistaa ympäristön, jossa se luotiin.

;; @alku tehdas
(define (lisaaja n)
  (λ (x) (+ x n)))             ; n on sidottu lisaaja-kutsun ympäristöön

(define seuraava (lisaaja 1))
(displayln (seuraava 41))
(displayln (map (lisaaja 10) '(1 2 3)))
;; @loppu tehdas

;; @alku tila
;; Sulkeuma voi kapseloida muuttuvan tilan: tilaan pääsee käsiksi vain
;; palautettujen funktioiden kautta.
(define (tunnistegeneraattori etuliite)
  (define laskuri 0)
  (λ ()
    (set! laskuri (add1 laskuri))
    (format "~a-~a" etuliite laskuri)))

(define tilaus-id (tunnistegeneraattori "T"))
(define asiakas-id (tunnistegeneraattori "A"))
(displayln (list (tilaus-id) (tilaus-id) (asiakas-id) (tilaus-id)))
;; @loppu tila

;; @alku olio
;; Olio sulkeumina: viesti valitsee toiminnon, tila on yksityinen.
(define (tili saldo)
  (define (nosta summa)
    (if (> summa saldo)
        (error 'tili "kate ei riitä: ~a > ~a" summa saldo)
        (begin (set! saldo (- saldo summa)) saldo)))
  (define (talleta summa)
    (set! saldo (+ saldo summa))
    saldo)
  (λ (viesti . argumentit)
    (case viesti
      [(nosta) (apply nosta argumentit)]
      [(talleta) (apply talleta argumentit)]
      [(saldo) saldo]
      [else (error 'tili "tuntematon viesti: ~a" viesti)])))

(define kayttotili (tili 100))
(displayln (kayttotili 'talleta 50))
(displayln (kayttotili 'nosta 30))
(displayln (kayttotili 'saldo))
;; @loppu olio
