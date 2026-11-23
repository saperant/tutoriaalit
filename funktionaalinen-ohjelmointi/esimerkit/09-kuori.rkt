#lang racket
;; Funktionaalinen ydin, imperatiivinen kuori: päätökset tehdään puhtaissa
;; funktioissa, ja vain ohut kuori lukee syötettä ja tulostaa.

;; @alku ydin
;; Ydin: (tilit, komento) → (values uudet-tilit viesti). Ei I/O:ta.
(define (kasittele tilit komento)
  (define (on? tili) (hash-has-key? tilit tili))
  (match komento
    [`(avaa ,tili)
     (if (on? tili)
         (values tilit (format "~a on jo olemassa" tili))
         (values (hash-set tilit tili 0) (format "avattu ~a" tili)))]
    [`(talleta ,tili ,(? exact-positive-integer? summa))
     #:when (on? tili)
     (values (hash-update tilit tili (λ (s) (+ s summa))) "ok")]
    [`(siirto ,mista ,mihin ,(? exact-positive-integer? summa))
     #:when (and (on? mista) (on? mihin))
     (if (< (hash-ref tilit mista) summa)
         (values tilit (format "kate ei riitä tilillä ~a" mista))
         (values (hash-update (hash-update tilit mista (λ (s) (- s summa)))
                              mihin (λ (s) (+ s summa)))
                 "ok"))]
    [`(saldot)
     (define rivit (sort (hash->list tilit) string<? #:key car))
     (values tilit (string-join
                    (for/list ([r (in-list rivit)])
                      (format "~a=~a" (car r) (cdr r)))
                    " "))]
    [_ (values tilit "hylätty: tuntematon tili tai väärä arvo")]))
;; @loppu ydin

;; @alku kuori
;; Kuori: lukee S-lausekkeita syötteestä, ajaa ytimen ja tulostaa.
(for/fold ([tilit (hash)] #:result (void))
          ([komento (in-port read)])
  (define-values (uudet viesti) (kasittele tilit komento))
  (printf "~s: ~a\n" komento viesti)
  uudet)
;; @loppu kuori
