#lang racket
;; Tietueen kentät ovat oletuksena muuttumattomia: asettajaa ei ole.

;; @alku virhe
(struct piste (x y) #:transparent)
(define p (piste 1 2))

(set-piste-x! p 5)                             ; @virhe
(define siirretty (struct-copy piste p [x 5])) ; uusi arvo
(println (list p siirretty))
;; @loppu virhe
