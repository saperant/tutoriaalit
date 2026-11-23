#lang racket
;; for-muodot: koosteet (comprehension) ilman eksplisiittistä rekursiota.

;; @alku muodot
(define tilaukset
  '(("Aalto" kahvi 2) ("Berg" tee 1) ("Aalto" pulla 3) ("Berg" kahvi 1)))

(displayln (for/list ([t (in-list tilaukset)]
                      #:when (eq? (second t) 'kahvi))
             (first t)))
(displayln (for/sum ([t (in-list tilaukset)]) (third t)))
(define viimeisin                                 ; viimeinen voittaa
  (for/hash ([t (in-list tilaukset)])
    (values (first t) (second t))))
(displayln (hash-ref viimeisin "Aalto"))
;; @loppu muodot

;; @alku fold
;; for/fold: useampi kertymä yhdellä läpikäynnillä.
(define-values (kpl-yht asiakkaat)
  (for/fold ([kpl 0] [nimet (set)])
            ([t (in-list tilaukset)])
    (values (+ kpl (third t)) (set-add nimet (first t)))))
(printf "~a kappaletta, ~a asiakasta\n" kpl-yht (set-count asiakkaat))
;; @loppu fold

;; @alku sisakkaiset
;; for* käy läpi kaikki yhdistelmät, for rinnakkain.
(displayln (for*/list ([rivi (in-range 1 3)] [sarake (in-string "ab")])
             (format "~a~a" sarake rivi)))
(displayln (for/list ([i (in-naturals 1)] [nimi (in-list '(a b c))])
             (cons i nimi)))
;; @loppu sisakkaiset
