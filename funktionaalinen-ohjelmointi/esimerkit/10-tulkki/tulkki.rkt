#lang racket
;; Pienen Scheme-murteen tulkki: arvioi (eval) ja sovella (apply)
;; kutsuvat toisiaan. Lähdekoodin jäsentää Racketin read, joten tulkki
;; saa valmiin syntaksipuun S-lausekkeena.
(provide arvioi uusi-globaali)

;; @alku ymparisto
;; Ympäristö on kehysten ketju. Kehys on muuttuva taulu, jotta define voi
;; lisätä sidonnan ja rekursiivinen funktio löytää itsensä.
(struct ymparisto (kehys vanhempi))

(define (etsi ymp nimi)
  (cond [(not ymp) (error 'tulkki "sitomaton muuttuja: ~a" nimi)]
        [(hash-has-key? (ymparisto-kehys ymp) nimi)
         (hash-ref (ymparisto-kehys ymp) nimi)]
        [else (etsi (ymparisto-vanhempi ymp) nimi)]))

(define (laajenna ymp nimet arvot)
  (unless (= (length nimet) (length arvot))
    (error 'tulkki "odotettiin ~a argumenttia, saatiin ~a"
           (length nimet) (length arvot)))
  (ymparisto (make-hasheq (map cons nimet arvot)) ymp))
;; @loppu ymparisto

;; @alku arvot
;; Käyttäjän funktio on sulkeuma: parametrit, runko ja määrittelyn
;; ympäristö. Primitiivi käärii Racketin funktion.
(struct sulkeuma (parametrit runko ymp))
(struct primitiivi (f))
;; @loppu arvot

;; @alku purku
;; Syntaktisen sokerin purku: let on lambdan kutsu, cond on sisäkkäisiä
;; if-lausekkeita. Ydinkieli pysyy pienenä.
(define (pura lauseke)
  (match lauseke
    [`(let ([,nimet ,arvot] ...) ,runko)
     `((lambda ,nimet ,runko) ,@arvot)]
    [`(cond [else ,tulos]) tulos]
    [`(cond [,ehto ,tulos] ,loput ...)
     `(if ,ehto ,tulos (cond ,@loput))]
    [_ lauseke]))
;; @loppu purku

;; @alku arvioi
(define (arvioi lauseke ymp)
  (match lauseke
    [(or (? number?) (? boolean?) (? string?)) lauseke]
    [(? symbol?) (etsi ymp lauseke)]
    [`(quote ,data) data]
    [`(if ,ehto ,niin ,muuten)
     (if (arvioi ehto ymp) (arvioi niin ymp) (arvioi muuten ymp))]
    [`(lambda ,parametrit ,runko) (sulkeuma parametrit runko ymp)]
    [`(define ,nimi ,arvo)
     (hash-set! (ymparisto-kehys ymp) nimi (arvioi arvo ymp))]
    [`(,(or 'let 'cond) ,_ ...) (arvioi (pura lauseke) ymp)]
    [`(,f ,argumentit ...)
     (sovella (arvioi f ymp)
              (map (λ (a) (arvioi a ymp)) argumentit))]))
;; @loppu arvioi

;; @alku sovella
(define (sovella f argumentit)
  (match f
    [(primitiivi g) (apply g argumentit)]
    [(sulkeuma parametrit runko ymp)
     ;; Häntäkutsu Racketissa: tulkittu kieli perii häntäkutsujen
     ;; optimoinnin isäntäkieleltä.
     (arvioi runko (laajenna ymp parametrit argumentit))]
    [_ (error 'tulkki "ei funktio: ~a" f)]))
;; @loppu sovella

;; @alku globaali
(define (uusi-globaali)
  (ymparisto
   (make-hasheq
    (for/list ([(nimi f) (in-hash
                          (hash '+ + '- - '* * '/ / '= = '< < '> >
                                'cons cons 'car car 'cdr cdr
                                'list list 'null? null?))])
      (cons nimi (primitiivi f))))
   #f))
;; @loppu globaali
