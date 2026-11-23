#lang racket
;; delay luo lupauksen (promise): lauseke arvioidaan vasta force-kutsussa
;; ja korkeintaan kerran.
(require racket/promise)

;; @alku lupaus
(define (kallis-haku)
  (displayln "  (haetaan asetukset...)")
  (hash 'kieli "fi" 'teema "tumma"))

(define asetukset (delay (kallis-haku)))

(displayln "ohjelma käynnistyy")
(displayln (hash-ref (force asetukset) 'kieli))   ; haku tehdään nyt
(displayln (hash-ref (force asetukset) 'teema))   ; muistettu arvo
;; @loppu lupaus

;; @alku ehto
;; Laiska argumentti: vaihtoehtoinen arvo lasketaan vain tarvittaessa.
(define (tai-oletus arvo oletus-lupaus)
  (or arvo (force oletus-lupaus)))

(displayln (tai-oletus "annettu" (delay (error "ei arvioida"))))
(displayln (tai-oletus #f (delay (string-upcase "oletus"))))
;; @loppu ehto
