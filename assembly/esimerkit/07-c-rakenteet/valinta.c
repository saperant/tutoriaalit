// Tiheä switch käännetään hyppytauluksi.
long laske(int op, long a, long b) {
    switch (op) {
    case 0: return a + b;
    case 1: return a - b;
    case 2: return a * b;
    case 3: return a & b;
    case 4: return a | b;
    case 5: return a ^ b;
    case 6: return a << (b & 63);
    default: return 0;
    }
}
