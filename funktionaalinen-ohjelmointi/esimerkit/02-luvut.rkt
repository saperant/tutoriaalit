#lang racket
;; Racketin lukutorni: tarkat rationaaliluvut ja rajattomat kokonaisluvut
;; ovat oletus, liukuluvut vain pyydettäessä.

;; @alku tarkat
(displayln (+ 1/10 2/10))              ; tarkka: 3/10
(displayln (+ 0.1 0.2))                ; liukuluku: 0.30000000000000004
(displayln (= (+ 1/10 2/10) 3/10))     ; #t
(displayln (expt 2 100))               ; kokonaisluku ei vuoda yli
(displayln (exact->inexact 2/3))       ; muunnos on aina eksplisiittinen
;; @loppu tarkat

;; @alku rahat
;; Hinnat sentteinä tai rationaalilukuina: pyöristys tehdään kerran,
;; vasta lopuksi, ja säännöllä, jonka ohjelma valitsee itse.
(define alv 255/1000)
(define (verollinen netto) (* netto (+ 1 alv)))
(define (senteiksi summa) (round (* summa 100)))   ; pankkiirin pyöristys

(define rivit '(19/2 1999/100 3))      ; 9,50 + 19,99 + 3,00 euroa
(define netto (apply + rivit))
(printf "netto ~a, verollinen ~a, sentteinä ~a\n"
        netto (exact->inexact (verollinen netto))
        (senteiksi (verollinen netto)))
;; @loppu rahat
