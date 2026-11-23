#lang racket
;; Pikaoppaan testatut koodipalat.
(require racket/stream)

;; @alku perus
(define (alennettu hinta [pros 10])   ; valinnainen argumentti
  (* hinta (- 1 (/ pros 100))))
(define (tervehdi #:nimi nimi)         ; avainsana-argumentti
  (string-append "Hei " nimi))
(let* ([a 2] [b (* a 3)]) (list a b))  ; '(2 6)
(cond [(> 3 2) 'iso] [else 'pieni])    ; 'iso
;; @loppu perus

;; @alku listat
(define xs '(3 1 4 1 5))
(map add1 xs)                          ; '(4 2 5 2 6)
(filter odd? xs)                       ; '(3 1 1 5)
(foldl + 0 xs)                         ; 14
(sort xs <)                            ; '(1 1 3 4 5)
(for/list ([x xs] #:when (> x 2)) (* x x))  ; '(9 16 25)
(apply max xs)                         ; 5
;; @loppu listat

;; @alku data
(struct piste (x y) #:transparent)     ; muuttumaton
(define p (piste 1 2))
(struct-copy piste p [x 5])            ; (piste 5 2)
(match p [(piste x 2) x] [_ #f])       ; 1
(define h (hash 'a 1))                 ; muuttumaton
(hash-set h 'b 2)                      ; uusi taulu
(hash-ref h 'c 0)                      ; oletus 0
;; @loppu data

;; @alku makro
(define-syntax-rule (kahdesti lauseke)
  (begin lauseke lauseke))
;; @loppu makro

;; @alku laiska
(define (alkaen n) (stream-cons n (alkaen (add1 n))))
(stream->list (stream-take (alkaen 1) 3))   ; '(1 2 3)
(define lupaus (delay (expt 2 64)))
(force lupaus)
;; @loppu laiska

;; @alku virheet
(with-handlers ([exn:fail? exn-message])
  (error 'jasenna "virheellinen syöte: ~a" "x"))
;; @loppu virheet
