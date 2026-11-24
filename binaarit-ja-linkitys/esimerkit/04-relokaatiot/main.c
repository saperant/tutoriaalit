#include <stdio.h>

// @alku main
extern int saldo;               // määritelty jossain muualla
int lisaa(int maara);

__attribute__((noipa))          // pysyy omana funktionaan
int tilaa(void)
{
    return lisaa(2) + saldo;
}
// @loppu main

int main(void)
{
    printf("tilauksen jälkeen: %d\n", tilaa());
    return 0;
}
