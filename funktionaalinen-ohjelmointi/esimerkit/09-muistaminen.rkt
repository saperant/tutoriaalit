#lang racket
;; Muistaminen (memoization): puhdas funktio voidaan välimuistittaa
;; turvallisesti, koska sama syöte antaa aina saman tuloksen.

;; @alku muista
;; Muuttuva taulu on piilossa sulkeumassa: ulospäin funktio on puhdas.
(define (muista f)
  (define taulu (make-hash))
  (λ argumentit
    (hash-ref! taulu argumentit (λ () (apply f argumentit)))))
;; @loppu muista

;; @alku editointi
;; Levenshteinin etäisyys: montako lisäystä, poistoa tai vaihtoa tarvitaan.
;; Rekursio kulkee indekseillä; muistettuna aika on O(n·m).
(define (etaisyys a b)
  (define et
    (muista
     (λ (i j)
       (cond [(= i (string-length a)) (- (string-length b) j)]
             [(= j (string-length b)) (- (string-length a) i)]
             [(char=? (string-ref a i) (string-ref b j))
              (et (add1 i) (add1 j))]
             [else (add1 (min (et (add1 i) j)           ; poisto
                              (et i (add1 j))           ; lisäys
                              (et (add1 i) (add1 j))))]))))  ; vaihto
  (et 0 0))
;; @loppu editointi

;; @alku ehdotus
(define komennot '("commit" "checkout" "cherry-pick" "clone" "config"))
(define (tarkoititko syote)
  (argmin (λ (k) (etaisyys syote k)) komennot))

(for ([s (in-list '("comit" "chekout" "clnoe" "cherry-pikc"))])
  (printf "~a → ~a\n" s (tarkoititko s)))
;; @loppu ehdotus
