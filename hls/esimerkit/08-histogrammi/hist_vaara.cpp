// VÄÄRIN: pragma väittää, ettei kierrosten välillä ole riippuvuutta,
// vaikka peräkkäisten kierrosten luokka voi olla sama.
// @alku ydin
#define N 256
#define B 16

void hist(const int x[N], int h[B]) {
// @alku pragma
#pragma HLS dependence variable=h type=inter dependent=false
// @loppu pragma
laskenta:
    for (int i = 0; i < N; i++) {
#pragma HLS pipeline II=1
        h[x[i]] += 1;
    }
}
// @loppu ydin
