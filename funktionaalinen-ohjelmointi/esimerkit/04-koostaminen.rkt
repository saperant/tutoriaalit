#lang racket
;; Funktioita yhdistelemällä rakennetaan uusia funktioita.

;; @alku validointi
;; Validointisäännöt ovat dataa: lista (viesti . predikaatti) -pareja.
(define (pituus-vahintaan n) (λ (s) (>= (string-length s) n)))
(define (sisaltaa luokka) (λ (s) (regexp-match? luokka s)))

(define salasanasaannot
  (list (cons "vähintään 12 merkkiä" (pituus-vahintaan 12))
        (cons "numero" (sisaltaa #px"[0-9]"))
        (cons "iso kirjain" (sisaltaa #px"[A-ZÅÄÖ]"))))

(define (puutteet saannot arvo)
  (for/list ([saanto (in-list saannot)]
             #:unless ((cdr saanto) arvo))
    (car saanto)))

(displayln (puutteet salasanasaannot "kissa123"))
(displayln (puutteet salasanasaannot "Pitkä-salasana-2026"))
;; @loppu validointi

;; @alku compose
(define siisti (compose string-titlecase string-trim))
(displayln (map siisti '("  matti meikäläinen " "MAIJA")))

;; curry kiinnittää ensimmäiset argumentit.
(define alle (curry > 10))             ; (λ (x) (> 10 x))
(displayln (filter alle '(3 14 7 25 9)))
;; @loppu compose

;; @alku avain
;; Vertailija avainfunktiosta: funktio, joka palauttaa funktion.
(define (avaimella avain [ennen? <])
  (λ (a b) (ennen? (avain a) (avain b))))

(define tuotteet '(("kahvi" 459) ("tee" 329) ("kaakao" 389)))
(displayln (sort tuotteet (avaimella second)))
(displayln (sort tuotteet (avaimella first string<?)))
;; @loppu avain
