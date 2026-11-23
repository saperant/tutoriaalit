#lang racket
;; Tietueet (struct) ja hahmontunnistus (match): summatyyppi ilman
;; luokkahierarkiaa.

;; @alku tyypit
;; Muoto on ympyrä, suorakulmio tai kolmio. Kentät ovat muuttumattomia.
(struct ympyra (sade) #:transparent)
(struct suorakulmio (leveys korkeus) #:transparent)
(struct kolmio (a b c) #:transparent)        ; sivujen pituudet
;; @loppu tyypit

;; @alku ala
(define (ala muoto)
  (match muoto
    [(ympyra r) (* pi r r)]
    [(suorakulmio l k) (* l k)]
    [(kolmio a b c)                            ; Heronin kaava
     (define s (/ (+ a b c) 2))
     (sqrt (* s (- s a) (- s b) (- s c)))]))
;; @loppu ala

;; @alku kuvaus
;; Hahmo voi tarkentaa ehdoilla ja purkaa sisäkkäisiä rakenteita.
(define (kuvaus muoto)
  (match muoto
    [(suorakulmio s s) (format "neliö ~a" s)]  ; sama muuttuja: l = k
    [(suorakulmio l k) (format "suorakulmio ~a×~a" l k)]
    [(ympyra (? (λ (r) (< r 1)))) "pieni ympyrä"]
    [(ympyra r) (format "ympyrä r=~a" r)]
    [(kolmio a a a) "tasasivuinen kolmio"]
    [(kolmio _ _ _) "kolmio"]))
;; @loppu kuvaus

;; @alku kaytto
(define muodot
  (list (ympyra 1/2) (suorakulmio 3 3) (suorakulmio 2 5) (kolmio 3 4 5)))
(for ([m (in-list muodot)])
  (printf "~a: ~a\n" (kuvaus m) (~r (ala m) #:precision 2)))

;; Muutos tehdään kopioimalla: alkuperäinen säilyy.
(define iso (struct-copy suorakulmio (second muodot) [leveys 10]))
(println (list (second muodot) iso))      ; println: lukukelpoinen muoto
;; @loppu kaytto
