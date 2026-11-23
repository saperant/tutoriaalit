#lang racket
;; Muuttumaton FIFO-jono kahdella listalla (Okasaki): lisäys loppuun ja
;; poisto alusta ovat tasoitetusti O(1).

;; @alku rajapinta
(provide
 (contract-out
  [tyhja-jono jono?]
  [jono-tyhja? (-> jono? boolean?)]
  [jonoon (-> jono? any/c jono?)]
  [jonon-eka (-> (and/c jono? (not/c jono-tyhja?)) any/c)]
  [jonosta (-> (and/c jono? (not/c jono-tyhja?)) jono?)]))
;; @loppu rajapinta

;; @alku toteutus
;; alku: poistettavat järjestyksessä, loppu: lisätyt käänteisesti.
;; Invariantti: alku on tyhjä vain, jos koko jono on tyhjä.
(struct jono (alku loppu))

(define tyhja-jono (jono '() '()))
(define (jono-tyhja? j) (empty? (jono-alku j)))

(define (tasapainota alku loppu)
  (if (empty? alku)
      (jono (reverse loppu) '())
      (jono alku loppu)))

(define (jonoon j x) (tasapainota (jono-alku j) (cons x (jono-loppu j))))
(define (jonon-eka j) (first (jono-alku j)))
(define (jonosta j) (tasapainota (rest (jono-alku j)) (jono-loppu j)))
;; @loppu toteutus

;; @alku testit
(module+ test
  (require rackunit)
  (define (lista->jono xs) (foldl (λ (x j) (jonoon j x)) tyhja-jono xs))
  (define (jono->lista j)
    (if (jono-tyhja? j) '() (cons (jonon-eka j) (jono->lista (jonosta j)))))

  (test-case "FIFO-järjestys säilyy"
    (check-equal? (jono->lista (lista->jono '(1 2 3))) '(1 2 3)))
  (test-case "vanha versio ei muutu"
    (define j1 (lista->jono '(a b)))
    (define j2 (jonosta j1))
    (check-equal? (jonon-eka j1) 'a)
    (check-equal? (jonon-eka j2) 'b))
  (test-case "tyhjästä jonosta lukeminen rikkoo sopimuksen"
    (check-exn exn:fail:contract? (λ () (jonon-eka tyhja-jono)))))
;; @loppu testit
