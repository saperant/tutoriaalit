#include <limits.h>
#include <stdio.h>

int main(void)
{
    // @alku koot
    printf("char:      %zu\n", sizeof(char));
    printf("short:     %zu\n", sizeof(short));
    printf("int:       %zu\n", sizeof(int));
    printf("long:      %zu\n", sizeof(long));
    printf("long long: %zu\n", sizeof(long long));
    printf("double:    %zu\n", sizeof(double));
    printf("osoitin:   %zu\n", sizeof(void *));
    printf("int-tyypin arvoalue: %d ... %d\n", INT_MIN, INT_MAX);
    // @loppu koot
}
