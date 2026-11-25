#lang racket
;; Piirtää lausekkeen ja sen derivaatan puina Graphviz-muodossa.
;; Lauseke on lista, joten puun piirtäminen on rakenteellinen rekursio.
(require "05-derivaatta.rkt")

;; @alku piirto
(define seuraava-id 0)

;; Tulostaa solmun ja sen alipuut, palauttaa solmun tunnisteen.
(define (piirra lauseke)
  (define id (format "n~a" seuraava-id))
  (set! seuraava-id (add1 seuraava-id))
  (match lauseke
    [(list operaattori argumentit ...)
     (printf "    ~a [label=\"~a\"];\n" id operaattori)
     (for ([a (in-list argumentit)])
       (printf "    ~a -> ~a;\n" id (piirra a)))]
    [lehti
     (printf "    ~a [label=\"~a\", fillcolor=\"#FFFFFF\"];\n" id lehti)])
  id)

(define (ryhma nimi otsikko lauseke)
  (printf "  subgraph cluster_~a {\n" nimi)
  (printf "    label=\"~a\"; color=\"#C9CED6\"; style=rounded;\n" otsikko)
  (void (piirra lauseke))
  (displayln "  }"))
;; @loppu piirto

(define f '(* (expt x 2) (+ x 1)))
(displayln "digraph {")
(displayln "  rankdir=TB; nodesep=0.25; ranksep=0.3;")
(displayln "  node [shape=circle, width=0.4, fixedsize=true];")
(ryhma "f" "f" f)
(ryhma "df" "df/dx" (d f 'x))
(displayln "}")
