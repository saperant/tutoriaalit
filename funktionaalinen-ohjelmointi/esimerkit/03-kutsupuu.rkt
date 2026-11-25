#lang racket
;; Piirtää (fib 5):n kutsupuun Graphviz-muodossa. Kutsu, jonka
;; argumentti on jo laskettu aiemmin, merkitään harmaalla: se on
;; turhaa työtä.

;; @alku puu
(define seuraava-id 0)
(define laskettu (mutable-set))

;; Palauttaa solmun tunnisteen ja tulostaa solmun ja sen kaaret.
(define (piirra n)
  (define id seuraava-id)
  (set! seuraava-id (add1 id))
  (define toisto? (set-member? laskettu n))
  (printf "  k~a [label=\"fib ~a\"~a];\n" id n
          (if toisto? ", fillcolor=\"#E3E6EA\", fontcolor=\"#6B7280\"" ""))
  (when (>= n 2)
    (for ([m (in-list (list (- n 1) (- n 2)))])
      (printf "  k~a -> k~a;\n" id (piirra m))))
  (set-add! laskettu n)
  id)
;; @loppu puu

(displayln "digraph {")
(displayln "  rankdir=TB; nodesep=0.25; ranksep=0.35;")
(void (piirra 5))
(displayln "}")
