// Matriisitulo C = A * B, 4 x 4. Liukuhihnoitettu sarakesilmukka avaa
// sisimmän silmukan kokonaan: jokainen kierros tarvitsee neljä alkiota
// kummastakin taulukosta.
// @alku ydin
#define N 4

void matmul(const int a[N * N], const int b[N * N], int c[N * N]) {
rivi:
    for (int i = 0; i < N; i++) {
    sarake:
        for (int j = 0; j < N; j++) {
#pragma HLS pipeline II=1
            int s = 0;
            for (int k = 0; k < N; k++) {
                s += a[i * N + k] * b[k * N + j];
            }
            c[i * N + j] = s;
        }
    }
}
// @loppu ydin
