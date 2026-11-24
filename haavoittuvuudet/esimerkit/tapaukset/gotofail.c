/* Applen "goto fail" 2014: SecureTransport, sslKeyExchange.c (ote).
 * Toinen goto fail on ehdon ulkopuolella, joten se suoritetaan aina,
 * ja err on tällöin 0 eli "onnistui". */
if ((err = SSLHashSHA1.update(&hashCtx, &serverRandom)) != 0)
    goto fail;
if ((err = SSLHashSHA1.update(&hashCtx, &signedParams)) != 0)
    goto fail;
    goto fail;
if ((err = SSLHashSHA1.final(&hashCtx, &hashOut)) != 0)
    goto fail;
/* ... allekirjoituksen tarkistus jää suorittamatta ... */
