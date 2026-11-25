#lang racket
;; Odotettu epäonnistuminen palautetaan arvona, poikkeus on varattu
;; virheille, joita kutsuja ei voi järkevästi käsitellä paikan päällä.

;; @alku arvona
;; Kirjaston tapa: string->number palauttaa #f, ei heitä poikkeusta.
(define (jasenna-portti teksti)
  (define n (string->number teksti))
  (and (exact-nonnegative-integer? n) (<= 1 n 65535) n))

(displayln (map jasenna-portti '("8080" "http" "70000")))
;; @loppu arvona

;; @alku ketju
;; Peräkkäiset vaiheet, joista jokainen voi epäonnistua. `and` palauttaa
;; ensimmäisen #f:n tai viimeisen arvon, joten ketju katkeaa itsestään
;; eikä sisäkkäisiä ehtoja tarvita.
(define (portti-asetuksista asetukset avain)
  (let* ([teksti (hash-ref asetukset avain #f)]            ; ei avainta?
         [osat   (and teksti (string-split teksti ":"))]
         [portti (and osat (= (length osat) 2)             ; väärä muoto?
                      (jasenna-portti (second osat)))])    ; ei portti?
    portti))

(define asetukset (hash "api" "localhost:8080" "loki" "localhost"
                        "kanta" "db:kanta"))
(displayln (for/list ([a (in-list '("api" "loki" "kanta" "posti"))])
             (portti-asetuksista asetukset a)))
;; @loppu ketju

;; @alku oma
;; Oma poikkeustyyppi periytyy exn:fail-tyypistä ja kantaa lisätietoa.
(struct exn:fail:asetus exn:fail (rivi))

(define (jasenna-rivi teksti nro)
  (match (string-split teksti "=")
    [(list avain arvo) (cons (string-trim avain) (string-trim arvo))]
    [_ (raise (exn:fail:asetus
               (format "rivi ~a: odotettiin avain = arvo" nro)
               (current-continuation-marks)
               nro))]))

(define (lue-asetukset rivit)
  (for/hash ([r (in-list rivit)] [nro (in-naturals 1)])
    (define pari (jasenna-rivi r nro))
    (values (car pari) (cdr pari))))
;; @loppu oma

;; @alku kasittely
(define (yrita rivit)
  (with-handlers ([exn:fail:asetus?
                   (λ (e) (format "virhe (~a): ~a"
                                  (exn:fail:asetus-rivi e)
                                  (exn-message e)))])
    (hash-ref (lue-asetukset rivit) "portti")))

(displayln (yrita '("isanta = localhost" "portti = 8080")))
(displayln (yrita '("isanta = localhost" "portti 8080")))
;; @loppu kasittely
