// Mittalaitteen vientityökalu: kirjoittaa jokaisen syöterivin eteen
// dokumentoimattoman 16-bittisen tarkisteen. Analyysi selvittää
// tarkistealgoritmin riisutusta ohjelmasta, jotta muut ohjelmat voivat
// tuottaa ja tarkistaa yhteensopivia tiedostoja.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

[[gnu::noinline]] static uint16_t tarkiste(const uint8_t *data, size_t n)
{
    unsigned a = 1, b = 0;
    for (size_t i = 0; i < n; i++) {
        a = (a + data[i]) % 251u;
        b = (b + a) % 251u;
    }
    return (uint16_t)(((b << 8) | a) ^ 0x5A5Au);
}

int main(void)
{
    char rivi[256];
    while (fgets(rivi, sizeof rivi, stdin) != NULL) {
        size_t n = strcspn(rivi, "\n");
        rivi[n] = '\0';
        printf("%04x %s\n", tarkiste((const uint8_t *)rivi, n), rivi);
    }
    return 0;
}
