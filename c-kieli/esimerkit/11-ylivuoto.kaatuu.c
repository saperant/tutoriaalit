#include <limits.h>
#include <stdio.h>

int kasvata(int x)
{
    return x + 1;   // määrittelemätöntä, jos x == INT_MAX
}

int main(void)
{
    int arvo = kasvata(INT_MAX);
    printf("%d\n", arvo);
}
