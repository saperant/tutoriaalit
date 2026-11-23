#lang racket
;; Parametri on dynaamisesti sidottu arvo: parameterize asettaa sen
;; lohkon ja kaikkien sieltä kutsuttujen funktioiden ajaksi.

;; @alku loki
(define lokitaso (make-parameter 'info))
(define tasot '(debug info varoitus virhe))

(define (loki taso viesti)
  (when (>= (index-of tasot taso) (index-of tasot (lokitaso)))
    (printf "[~a] ~a\n" taso viesti)))

(define (synkronoi)
  (loki 'debug "avataan yhteys")
  (loki 'info "synkronoitu 42 tietuetta"))

(synkronoi)
(parameterize ([lokitaso 'debug])     ; vain tämän lohkon ajan
  (synkronoi))
(synkronoi)
;; @loppu loki

;; @alku tuloste
;; Standardikirjasto käyttää samaa mekanismia: current-output-port on
;; parametri, joten tulosteen voi kaapata esimerkiksi testissä.
(define kaapattu (with-output-to-string synkronoi))
(printf "kaapattiin ~s\n" kaapattu)
;; @loppu tuloste
