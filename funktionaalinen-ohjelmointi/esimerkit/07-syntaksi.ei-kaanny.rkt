#lang racket
;; syntax-parse tarkistaa makron käytön ja antaa virheen käännösaikana
;; käyttäjän koodin kohdasta, ei makron sisältä.
(require (for-syntax syntax/parse))

;; @alku parse
(define-syntax (vaihda! stx)
  (syntax-parse stx
    [(_ a:id b:id)                      ; molempien on oltava nimiä
     #'(let ([tmp a])
         (set! a b)
         (set! b tmp))]))

(define x 1)
(define y 2)
(vaihda! x y)
(vaihda! x 5)                           ; @virhe
(displayln (list x y))
;; @loppu parse
