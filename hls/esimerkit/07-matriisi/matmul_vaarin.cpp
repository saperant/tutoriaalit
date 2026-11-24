// Väärä jako: B:n alkiot b[k * N + j] eivät jakaudu syklisesti
// pankkeihin käännösaikana tunnetulla tavalla.
// @alku ydin
#define N 4

void matmul(const int a[N * N], const int b[N * N], int c[N * N]) {
// @alku jako
#pragma HLS array_partition variable=a type=cyclic factor=4
#pragma HLS array_partition variable=b type=cyclic factor=4
// @loppu jako
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
