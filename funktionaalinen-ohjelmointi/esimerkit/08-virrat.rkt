#lang racket
;; Virta (stream) on laiska lista: alkio lasketaan vasta, kun sitä
;; tarvitaan, joten virta voi olla ääretön.
(require racket/stream)

;; @alku luvut
(define (luvut-alkaen n)
  (stream-cons n (luvut-alkaen (add1 n))))   ; loppu on lupaus
(define luonnolliset (luvut-alkaen 0))

(displayln (stream->list (stream-take luonnolliset 5)))
;; @loppu luvut

;; @alku seula
;; Eratostheneen seula virtana: jokainen alkuluku suodattaa loput.
(define (seula s)
  (define p (stream-first s))
  (stream-cons p
               (seula (stream-filter (λ (n) (positive? (remainder n p)))
                                     (stream-rest s)))))
(define alkuluvut (seula (luvut-alkaen 2)))

(displayln (stream->list (stream-take alkuluvut 10)))
(displayln (stream-ref alkuluvut 99))        ; sadas alkuluku
;; @loppu seula

;; @alku putki
;; Putki ilman välilistoja: neliöt, parilliset, kunnes summa > 1000.
(define parilliset-nelio
  (stream-filter even? (stream-map (λ (n) (* n n)) luonnolliset)))
(displayln (for/fold ([summa 0]) ([x (in-stream parilliset-nelio)]
                                  #:break (> summa 1000))
             (+ summa x)))
;; @loppu putki
