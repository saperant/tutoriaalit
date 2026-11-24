/* Heartbleed 2014: OpenSSL:n korjaus (ote, d1_both.c ja t1_lib.c).
 * Korjaus vertaa viestin ilmoittamaa pituutta saapuneen tietueen
 * todelliseen pituuteen ennen kopiointia. */
/* Read type and payload length first */
if (1 + 2 + 16 > s->s3->rrec.length)
    return 0; /* silently discard */
hbtype = *p++;
n2s(p, payload);
if (1 + 2 + payload + 16 > s->s3->rrec.length)
    return 0; /* silently discard per RFC 6520 sec. 4 */
pl = p;
