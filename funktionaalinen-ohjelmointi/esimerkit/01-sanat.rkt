#lang racket
;; Sanojen esiintymät: lukee tekstin syötteestä ja tulostaa kolme
;; yleisintä sanaa. Koko ohjelma on funktioiden ketju ilman muuttujien
;; päivittämistä.

;; @alku sanat
(define (sanat rivi)
  (string-split (string-downcase rivi) #px"\\P{L}+"))

(define (laske-esiintymat sanalista)
  (for/fold ([maarat (hash)])          ; muuttumaton hajautustaulu
            ([sana (in-list sanalista)])
    (hash-update maarat sana add1 0)))

;; Järjestys: määrä laskevasti, tasatilanteessa aakkosjärjestys.
(define (ennen? a b)
  (or (> (cdr a) (cdr b))
      (and (= (cdr a) (cdr b)) (string<? (car a) (car b)))))

(define (yleisimmat maarat n)
  (take (sort (hash->list maarat) ennen?) n))
;; @loppu sanat

;; @alku paa
(define kaikki-sanat
  (append-map sanat (port->lines (current-input-port))))

(for ([pari (in-list (yleisimmat (laske-esiintymat kaikki-sanat) 3))])
  (printf "~a ~a\n" (cdr pari) (car pari)))
;; @loppu paa
