// @alku otsakkeet
/** Tuotannon tietoturvaotsakkeet. Sama asetus annetaan Viten
 *  esikatselupalvelimelle, joten päästä päähän -testit ajetaan sitä
 *  vastaan ja paljastavat, jos sovellus rikkoo käytäntöä. */
export const TURVAOTSAKKEET: Record<string, string> = {
  "Content-Security-Policy": [
    "default-src 'self'",
    "script-src 'self'",          // ei inline-skriptejä eikä eval()
    "style-src 'self'",
    "img-src 'self' data:",
    "connect-src 'self'",         // fetch vain omaan alkuperään
    "frame-ancestors 'none'",     // ei upotusta toisen sivun kehykseen
    "base-uri 'self'",
    "form-action 'self'",
  ].join("; "),
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
};
// @loppu otsakkeet
