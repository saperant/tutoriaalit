// Kantoluku, ylivuoto ja vertailu.
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

int lisaa_u64(uint64_t a, uint64_t b, uint64_t *tulos);
int lisaa_i64(int64_t a, int64_t b, int64_t *tulos);
long vertaa(long a, long b);

int main(void) {
    uint64_t u;
    int k = lisaa_u64(UINT64_MAX, 1, &u);
    printf("UINT64_MAX + 1 = %" PRIu64 ", kanto %d\n", u, k);
    k = lisaa_u64(40, 2, &u);
    printf("40 + 2 = %" PRIu64 ", kanto %d\n", u, k);

    int64_t s;
    int y = lisaa_i64(INT64_MAX, 1, &s);
    printf("INT64_MAX + 1 = %" PRId64 ", ylivuoto %d\n", s, y);
    y = lisaa_i64(-5, 3, &s);
    printf("-5 + 3 = %" PRId64 ", ylivuoto %d\n", s, y);

    const long parit[][2] = {{1, 2}, {2, 2}, {3, 2}, {-1, 1}};
    for (int i = 0; i < 4; i++) {
        printf("vertaa(%ld, %ld) = %ld\n", parit[i][0], parit[i][1],
               vertaa(parit[i][0], parit[i][1]));
    }
    return 0;
}
