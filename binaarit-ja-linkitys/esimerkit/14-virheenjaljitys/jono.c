#include <stdio.h>
#include <stdlib.h>

struct jono {
    int *alkiot;
    int koko;
};

__attribute__((noinline)) static int viimeinen(const struct jono *j)
{
    return j->alkiot[j->koko - 1];   // tyhjällä jonolla alkiot == NULL
}

int main(int argc, char **argv)
{
    (void)argv;
    int taulu[] = {4, 8, 15};
    struct jono j = {argc > 1 ? NULL : taulu, argc > 1 ? 0 : 3};
    printf("viimeinen: %d\n", viimeinen(&j));
    return EXIT_SUCCESS;
}
