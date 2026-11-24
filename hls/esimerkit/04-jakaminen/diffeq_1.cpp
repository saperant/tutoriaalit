// Sama differentiaaliyhtälö yhdellä kertojalla: kuusi kertolaskua
// jaetaan saman yksikön kesken eri jaksoille.
// @alku ydin
int diffeq(int x0, int y0, int u0, int dx) {
// @alku pragma
#pragma HLS allocation operation instances=mul limit=1
// @loppu pragma
    int x = x0;
    int y = y0;
    int u = u0;
askel:
    for (int k = 0; k < 4; k++) {
        int x1 = x + dx;
        int u1 = u - 3 * x * u * dx - 3 * y * dx;
        int y1 = y + u * dx;
        x = x1;
        u = u1;
        y = y1;
    }
    return y;
}
// @loppu ydin
