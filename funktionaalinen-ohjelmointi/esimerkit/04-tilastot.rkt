#lang racket
;; map, filter ja fold: kolme peruskaavaa, joihin useimmat listan
;; läpikäynnit palautuvat.

;; @alku omat
;; Valmiit funktiot ovat pelkkää rakenteellista rekursiota.
(define (oma-map f lista)
  (if (empty? lista)
      '()
      (cons (f (first lista)) (oma-map f (rest lista)))))

(define (oma-filter ok? lista)
  (cond [(empty? lista) '()]
        [(ok? (first lista))
         (cons (first lista) (oma-filter ok? (rest lista)))]
        [else (oma-filter ok? (rest lista))]))
;; @loppu omat

;; @alku tilastot
;; Anturin lukemat; #f tarkoittaa puuttuvaa mittausta.
(define lukemat '(21.5 #f 22.0 23.5 #f 19.0 24.0))

(define mitatut (filter real? lukemat))
(define fahrenheit (map (λ (c) (+ 32 (* 9/5 c))) mitatut))
(define suurin (foldl max -inf.0 mitatut))
(define keskiarvo (/ (foldl + 0 mitatut) (length mitatut)))

(printf "mitattu ~a/~a, suurin ~a, keskiarvo ~a\n"
        (length mitatut) (length lukemat) suurin keskiarvo)
(displayln (map (λ (f) (~r f #:precision 1)) fahrenheit))
(displayln (oma-map add1 (oma-filter even? '(1 2 3 4 5 6))))
;; @loppu tilastot

;; @alku suunta
;; foldr käsittelee alkiot oikealta, foldl vasemmalta.
(displayln (foldr cons '() '(1 2 3)))   ; (1 2 3): kopio
(displayln (foldl cons '() '(1 2 3)))   ; (3 2 1): käännetty
;; @loppu suunta
