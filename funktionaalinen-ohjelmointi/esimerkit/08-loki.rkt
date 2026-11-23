#lang racket
;; Syöte luetaan laiskasti rivi kerrallaan: lukeminen loppuu ensimmäiseen
;; virheeseen, eikä koko tiedostoa tarvitse pitää muistissa.

;; @alku loki
(define (vakavuus rivi)
  (match (regexp-match #px"^\\S+ (INFO|WARN|ERROR) " rivi)
    [(list _ taso) (string->symbol taso)]
    [#f 'tuntematon]))

(define-values (luettu varoitukset)
  (for/fold ([n 0] [varoitukset '()])
            ([rivi (in-lines (current-input-port))]
             #:final (eq? (vakavuus rivi) 'ERROR))
    (values (add1 n)
            (if (eq? (vakavuus rivi) 'WARN)
                (cons rivi varoitukset)
                varoitukset))))

(printf "luettiin ~a riviä ensimmäiseen virheeseen asti\n" luettu)
(for-each displayln (reverse varoitukset))
;; @loppu loki
