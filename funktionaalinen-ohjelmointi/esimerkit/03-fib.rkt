#lang racket
;; Puumainen rekursio laskee samoja osatehtäviä yhä uudelleen.

;; @alku naivi
(define (fib n)
  (if (< n 2)
      n
      (+ (fib (- n 1)) (fib (- n 2)))))

;; Kutsujen määrä noudattaa samaa rekursiota: kasvu on eksponentiaalista.
(define (kutsuja n)
  (if (< n 2)
      1
      (+ 1 (kutsuja (- n 1)) (kutsuja (- n 2)))))
;; @loppu naivi

;; @alku iteratiivinen
;; Häntärekursio kahdella kertymällä: n askelta, vakiomuisti.
(define (fib/iter n)
  (let kierros ([a 0] [b 1] [k n])
    (if (zero? k)
        a
        (kierros b (+ a b) (sub1 k)))))
;; @loppu iteratiivinen

(for ([n (in-list '(10 20 25))])
  (printf "fib(~a) = ~a: ~a kutsua, iteroiden ~a askelta\n"
          n (fib n) (kutsuja n) n))
(displayln (fib/iter 100))
