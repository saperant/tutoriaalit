// Kaksi säiettä kasvattaa samaa säiekohtaista muuttujaa: kumpikin
// näkee oman kopionsa.
#include "laskuri.h"
#include <pthread.h>
#include <stdio.h>

// @alku saie
static void *tyo(void *arg) {
    int kertoja = *(int *)arg;
    int viimeinen = 0;
    for (int i = 0; i < kertoja; i++) {
        viimeinen = kasvata();
    }
    *(int *)arg = viimeinen;
    return NULL;
}

int main(void) {
    int a = 3, b = 5;
    pthread_t sa, sb;
    pthread_create(&sa, NULL, tyo, &a);
    pthread_create(&sb, NULL, tyo, &b);
    pthread_join(sa, NULL);
    pthread_join(sb, NULL);
    printf("säie a: %d, säie b: %d, pääsäie: %d\n", a, b, kasvata());
    return 0;
}
// @loppu saie
