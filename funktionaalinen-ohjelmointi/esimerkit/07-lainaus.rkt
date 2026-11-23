#lang racket
;; Koodi on dataa: lainaus (quote) ja puolilainaus (quasiquote).
(require xml)

;; @alku puolilainaus
(define tuotteet '(("kahvi" 459) ("tee" 329)))

;; ` rakentaa rungon, , lisää arvon ja ,@ liittää listan alkiot.
(define (taulukko rivit)
  `(table ((class "hinnat"))
          (tr (th "tuote") (th "hinta"))
          ,@(for/list ([r (in-list rivit)])
              `(tr (td ,(first r))
                   (td ,(~r (/ (second r) 100) #:precision '(= 2)))))))

(define html (taulukko tuotteet))
(pretty-write html)                          ; rakenne on tavallinen lista
(displayln (xexpr->string (last html)))      ; ja muuntuu HTML:ksi
;; @loppu puolilainaus

;; @alku eval
;; Lauseke rakennetaan datana ja arvioidaan omassa nimiavaruudessaan.
(define-namespace-anchor ankkuri)
(define ns (namespace-anchor->namespace ankkuri))

(define kaava `(+ ,@(map second tuotteet)))
(displayln kaava)
(displayln (eval kaava ns))
;; @loppu eval
