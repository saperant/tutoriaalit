// Avoin uudelleenohjaus ja turvallisuusotsakkeet.

// @alku ohjaus
// Kirjautumisen jälkeen palataan sivulle, jolta tultiin. Haavoittuva
// versio ohjaa minne tahansa: https://pankki.example/ulos?seuraava=
// https://pankki-kirjaudu.example näyttää luotettavalta linkiltä.
export function seuraavaHaavoittuva(arvo: string): string {
  return arvo;
}

export function seuraava(arvo: string): string {
  // Vain saman sivuston polut: alkaa yhdellä vinoviivalla, ei "//"
  // eikä "/\" (selaimet tulkitsevat molemmat toiseksi palvelimeksi).
  const u = new URL(arvo, "https://oma.invalid");
  if (u.origin !== "https://oma.invalid" || !arvo.startsWith("/") ||
      arvo.startsWith("//") || arvo.startsWith("/\\")) {
    return "/";
  }
  return u.pathname + u.search + u.hash;
}
// @loppu ohjaus

// @alku otsakkeet
export function turvaotsakkeet(nonce: string): Record<string, string> {
  return {
    // Vain HTTPS vuoden ajan, myös aliverkkotunnuksille.
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": [
      "default-src 'self'", `script-src 'nonce-${nonce}' 'strict-dynamic'`,
      "object-src 'none'", "base-uri 'none'", "frame-ancestors 'none'",
      "form-action 'self'", "require-trusted-types-for 'script'",
    ].join("; "),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
  };
}
// @loppu otsakkeet
