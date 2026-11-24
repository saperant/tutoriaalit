// Vaihtuvanmittaiset kokonaisluvut (varint, LEB128) ja zigzag-koodaus,
// kuten Protocol Buffersissa: pienet luvut vievät vähän tilaa.
#include <inttypes.h>
#include <stdio.h>

// @alku varint
// 7 bittiä tavua kohden, vähiten merkitsevät ensin. Ylin bitti kertoo,
// jatkuuko luku. 64-bittinen luku vie enintään 10 tavua.
static size_t koodaa_varint(uint64_t x, uint8_t *b) {
    size_t n = 0;
    while (x >= 0x80) {
        b[n++] = (uint8_t)(x | 0x80);
        x >>= 7;
    }
    b[n++] = (uint8_t)x;
    return n;
}

// Palauttaa käytettyjen tavujen määrän tai 0, jos syöte loppui kesken
// tai luku on liian pitkä.
static size_t pura_varint(const uint8_t *b, size_t n, uint64_t *x) {
    *x = 0;
    for (size_t i = 0; i < n && i < 10; i++) {
        *x |= (uint64_t)(b[i] & 0x7f) << (7 * i);
        if ((b[i] & 0x80) == 0) {
            return i + 1;
        }
    }
    return 0;
}

// Zigzag: 0, -1, 1, -2, 2 ... -> 0, 1, 2, 3, 4, jotta pienet negatiiviset
// luvut eivät vie kymmentä tavua.
static uint64_t zigzag(int64_t x) {
    return ((uint64_t)x << 1) ^ (uint64_t)(x >> 63);
}

static int64_t unzigzag(uint64_t z) {
    return (int64_t)(z >> 1) ^ -(int64_t)(z & 1);
}
// @loppu varint

int main(void) {
    const int64_t luvut[] = {0, 1, 127, 128, 300, -1, -64, 1LL << 32};
    for (size_t i = 0; i < sizeof luvut / sizeof luvut[0]; i++) {
        uint8_t b[10];
        size_t n = koodaa_varint(zigzag(luvut[i]), b);
        uint64_t z;
        bool ok = pura_varint(b, n, &z) == n && unzigzag(z) == luvut[i];
        printf("%11" PRId64 " -> %zu tavua:", luvut[i], n);
        for (size_t j = 0; j < n; j++) {
            printf(" %02x", b[j]);
        }
        printf("%*s takaisin: %s\n", (int)(3 * (5 - n)), "",
               ok ? "ok" : "VIRHE");
    }
    uint8_t kesken[] = {0x80, 0x80};
    uint64_t x;
    printf("katkennut varint: %zu tavua purettu\n",
           pura_varint(kesken, 2, &x));
    return 0;
}
