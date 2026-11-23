#lang racket
;; Asiakaspalvelun jonosimulaatio. Testaaja ajaa tämän tiedoston, joten se
;; ajaa myös jono.rkt:n testit; tavallisesti ne ajetaan: raco test .
(require "jono.rkt"
         (submod "jono.rkt" test))

;; @alku simulaatio
(define tapahtumat
  '((saapuu "Aino") (saapuu "Eero") (palvele) (saapuu "Iida")
    (palvele) (palvele)))

(define lopuksi
  (for/fold ([j tyhja-jono]) ([t (in-list tapahtumat)])
    (match t
      [`(saapuu ,nimi) (printf "~a jonoon\n" nimi) (jonoon j nimi)]
      [`(palvele) (printf "palvellaan ~a\n" (jonon-eka j)) (jonosta j)])))
(printf "jono tyhjä lopuksi: ~a\n" (jono-tyhja? lopuksi))
;; @loppu simulaatio
