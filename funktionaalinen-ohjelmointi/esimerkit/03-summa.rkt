#lang racket
;; Rakenteellinen rekursio listan yli kolmella tavalla.

;; @alku rekursio
;; Lista on joko tyhjä tai (cons alkio lista): funktiossa on haara
;; kummallekin tapaukselle, ja rekursio seuraa datan rakennetta.
(define (summa lista)
  (if (empty? lista)
      0
      (+ (first lista) (summa (rest lista)))))
;; @loppu rekursio

;; @alku hanta
;; Häntärekursio: rekursiivinen kutsu on funktion viimeinen teko, joten
;; kutsupino ei kasva. Välitulos kulkee kertymässä (akkumulaattori).
(define (summa/kertyma lista)
  (define (kierros jaljella kertyma)
    (if (empty? jaljella)
        kertyma
        (kierros (rest jaljella) (+ kertyma (first jaljella)))))
  (kierros lista 0))

;; Sama nimetyllä let-lausekkeella: silmukka on häntäkutsu.
(define (keskiarvo lista)
  (let silmukka ([xs lista] [summa 0] [lkm 0])
    (if (empty? xs)
        (/ summa lkm)
        (silmukka (rest xs) (+ summa (first xs)) (add1 lkm)))))
;; @loppu hanta

;; @alku syva
(define iso (range 1000000))
(displayln (summa iso))           ; syväkään rekursio ei kaada Racketia
(displayln (summa/kertyma iso))
(displayln (keskiarvo '(4 8 15 16 23 42)))
;; @loppu syva
