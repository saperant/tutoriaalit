// Väärin tasattu pino kaataa ohjelman, kun kutsuttu funktio olettaa
// tasauksen (printf tallentaa XMM-rekisterit movaps-käskyllä).
#include <stdio.h>

void kutsu(void (*f)(double), double x);

static void tulosta(double x) {
    printf("x = %.1f\n", x);
}

int main(void) {
    kutsu(tulosta, 2.5);
    return 0;
}
