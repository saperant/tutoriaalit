#lang racket
;; Pieni kielensisäinen kieli (DSL): makro kääntää tilakoneen kuvauksen
;; tavalliseksi funktioksi käännösaikana.

;; @alku makro
(define-syntax-rule (tilakone [tila (tapahtuma -> seuraava) ...] ...)
  (λ (nykyinen syote)
    (define (ei-siirtymaa)
      (error 'tilakone "ei siirtymää: ~a + ~a" nykyinen syote))
    (match nykyinen
      ['tila (match syote
               ['tapahtuma 'seuraava] ...
               [_ (ei-siirtymaa)])] ...
      [_ (ei-siirtymaa)])))
;; @loppu makro

;; @alku kaytto
(define ovi
  (tilakone
   [kiinni (avaa -> auki) (lukitse -> lukossa)]
   [auki (sulje -> kiinni)]
   [lukossa (avaa-lukko -> kiinni)]))

(define (aja kone alku tapahtumat)
  (for/fold ([tila alku]) ([t (in-list tapahtumat)])
    (define uusi (kone tila t))
    (printf "~a --~a--> ~a\n" tila t uusi)
    uusi))

(void (aja ovi 'kiinni '(avaa sulje lukitse avaa-lukko)))
;; @loppu kaytto
