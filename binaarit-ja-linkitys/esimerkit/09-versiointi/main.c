#include <stdio.h>

int vertaa_tunnus(const char *a, const char *b);

int main(void)
{
    printf("Admin == admin: %s\n",
           vertaa_tunnus("Admin", "admin") ? "kyllä" : "ei");
    return 0;
}
