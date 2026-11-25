// Adler-32: assembly-toteutusta verrataan C-viitetoteutukseen.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

uint32_t adler32(const uint8_t *data, size_t n);

// @alku viite
static uint32_t adler32_c(const uint8_t *data, size_t n) {
    uint32_t a = 1, b = 0;
    for (size_t i = 0; i < n; i++) {
        a = (a + data[i]) % 65521;
        b = (b + a) % 65521;
    }
    return (b << 16) | a;
}
// @loppu viite

static void tarkista(const char *nimi, const uint8_t *data, size_t n) {
    uint32_t asm = adler32(data, n);
    printf("%-14s %08x %s\n", nimi, asm,
           asm == adler32_c(data, n) ? "(sama kuin C)" : "(ERI!)");
}

int main(void) {
    tarkista("0 tavua", (const uint8_t *)"", 0);
    const char *w = "Wikipedia";
    tarkista("\"Wikipedia\"", (const uint8_t *)w, strlen(w));
    static uint8_t iso[100000];
    for (size_t i = 0; i < sizeof iso; i++) {
        iso[i] = (uint8_t)(i * 7 + (i >> 8));
    }
    tarkista("100 000 tavua", iso, sizeof iso);
    static uint8_t ffs[5552];
    memset(ffs, 0xff, sizeof ffs);
    tarkista("5552 x 0xff", ffs, sizeof ffs);
    return 0;
}
