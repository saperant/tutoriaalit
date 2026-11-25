#lang racket
;; Sijoitusmallin jäljitys: sama summa tavallisella rekursiolla ja
;; häntärekursiolla. Tuloste näyttää, miltä laskenta näyttää kullakin
;; askeleella.

;; @alku tavallinen
;; `ymparilla` kertoo, mitä kesken jääneet kutsut vielä odottavat:
;; se täydentää annetun osalausekkeen koko lausekkeeksi.
(define (summa lista [ymparilla identity])
  (displayln (ymparilla (format "(summa '~a)" lista)))
  (cond
    [(empty? lista)
     (displayln (ymparilla "0"))
     0]
    [else
     (define x (first lista))
     (define loput
       (summa (rest lista)
              (λ (osa) (ymparilla (format "(+ ~a ~a)" x osa)))))
     (define tulos (+ x loput))
     (displayln (ymparilla (~a tulos)))
     tulos]))
;; @loppu tavallinen

;; @alku hanta
;; Häntärekursiossa mikään ei jää odottamaan: koko tila on argumenteissa.
(define (summa/kertyma lista)
  (let kierros ([jaljella lista] [kertyma 0])
    (printf "(kierros '~a ~a)\n" jaljella kertyma)
    (if (empty? jaljella)
        kertyma
        (kierros (rest jaljella) (+ kertyma (first jaljella))))))
;; @loppu hanta

(displayln "tavallinen rekursio:")
(void (summa '(1 2 3)))
(displayln "häntärekursio:")
(displayln (summa/kertyma '(1 2 3)))
