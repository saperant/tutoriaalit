#lang racket
;; Symbolinen derivointi: lausekepuu on tavallinen lista, ja match purkaa
;; sen. Sama rakenne toistuu kääntäjissä (AST-muunnokset).
(provide d)

;; @alku derivoi
;; Lauseke: luku, muuttuja tai (+ a b), (* a b), (expt a n).
(define (d lauseke x)
  (match lauseke
    [(? number?) 0]
    [(? symbol? y) (if (eq? y x) 1 0)]
    [`(+ ,a ,b) (summa (d a x) (d b x))]
    [`(* ,a ,b) (summa (tulo (d a x) b) (tulo a (d b x)))]
    [`(expt ,a ,(? number? n))
     (tulo (tulo n (potenssi a (- n 1))) (d a x))]))
;; @loppu derivoi

;; @alku sievenna
;; Älykkäät konstruktorit sieventävät jo rakennusvaiheessa.
(define (summa a b)
  (match* (a b)
    [(0 _) b]
    [(_ 0) a]
    [((? number?) (? number?)) (+ a b)]
    [(_ _) `(+ ,a ,b)]))

(define (tulo a b)
  (match* (a b)
    [(0 _) 0]
    [(_ 0) 0]
    [(1 _) b]
    [(_ 1) a]
    [((? number?) (? number?)) (* a b)]
    [(_ _) `(* ,a ,b)]))

(define (potenssi a n)
  (match n
    [0 1]
    [1 a]
    [_ `(expt ,a ,n)]))
;; @loppu sievenna

;; @alku kaytto
(module+ main
  (for ([f (in-list '((+ (* 3 x) 5)
                      (* x y)
                      (expt x 3)
                      (* (expt x 2) (+ x 1))))])
    (printf "d/dx ~a = ~a\n" f (d f 'x))))
;; @loppu kaytto
