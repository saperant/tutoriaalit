// Kaksi säiettä kasvattaa samaa laskuria ilman synkronointia.
#include <pthread.h>
#include <stdio.h>

static long laskuri;

static void *kasvata(void *arg)
{
    (void)arg;
    for (int i = 0; i < 100000; i++)
        laskuri++;
    return NULL;
}

int main(void)
{
    pthread_t a, b;
    pthread_create(&a, NULL, kasvata, NULL);
    pthread_create(&b, NULL, kasvata, NULL);
    pthread_join(a, NULL);
    pthread_join(b, NULL);
    printf("laskuri %s\n", laskuri <= 200000 ? "ok" : "?");
    return 0;
}
