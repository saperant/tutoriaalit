#lang racket
;; Puurekursio: hakemistopuu sisäkkäisinä listoina.
;; Solmu on joko tiedosto (nimi koko) tai hakemisto (nimi solmu ...).

;; @alku data
(define koti
  '("koti"
    ("docs" ("raportti.pdf" 120) ("muistio.txt" 4))
    ("kuvat" ("loma" ("ranta.jpg" 900) ("vuori.jpg" 750)))
    ("muistiinpanot.md" 2)))

(define (tiedosto? solmu) (number? (second solmu)))
(define (lapset solmu) (rest solmu))
;; @loppu data

;; @alku koko
(define (koko solmu)
  (if (tiedosto? solmu)
      (second solmu)
      (apply + (map koko (lapset solmu)))))
;; @loppu koko

;; @alku polut
;; Jokainen rekursiotaso saa polun etuliitteen parametrina.
(define (polut solmu [etuliite ""])
  (define polku (string-append etuliite "/" (first solmu)))
  (if (tiedosto? solmu)
      (list polku)
      (append-map (λ (lapsi) (polut lapsi polku)) (lapset solmu))))
;; @loppu polut

(displayln (koko koti))
(for-each displayln (polut koti))
