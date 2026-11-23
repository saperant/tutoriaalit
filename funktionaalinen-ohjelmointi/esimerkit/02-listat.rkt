#lang racket
;; Lista on pari-solujen ketju: (cons alkio loppu). Tyhjä lista on '().

;; @alku rakenne
(define kaupungit (list "Oulu" "Tampere" "Turku"))
(define lisatty (cons "Espoo" kaupungit))   ; uusi lista, vanha ennallaan

(displayln (first lisatty))                 ; car: ensimmäinen alkio
(displayln (rest lisatty))                  ; cdr: loput
(displayln kaupungit)                       ; alkuperäinen ei muuttunut
(displayln (eq? (rest lisatty) kaupungit))  ; loppu on jaettu, ei kopio
;; @loppu rakenne

;; @alku lainaus
;; Lainattu lauseke on dataa: symboleja, lukuja ja listoja.
(define resepti '(pannukakku (maito 5) (muna 2) (jauho 3)))
(displayln (car resepti))                   ; symboli pannukakku
(displayln (cadr resepti))                  ; (maito 5)
(displayln (assq 'muna (cdr resepti)))      ; avain-arvo-haku
(printf "~a | ~s | ~v\n" "teksti" "teksti" 'symboli)
;; @loppu lainaus

;; @alku valmiit
(displayln (length kaupungit))
(displayln (reverse kaupungit))
(displayln (append kaupungit '("Vaasa")))
(displayln (list-ref kaupungit 1))          ; O(n): lista ei ole taulukko
(displayln (member "Tampere" kaupungit))    ; loppuosa tai #f
;; @loppu valmiit
