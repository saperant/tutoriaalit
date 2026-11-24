// Kirkkaus (luma) RGB-pikselistä kokonaisluvuilla: kertoimet 0,299,
// 0,587 ja 0,114 kerrottuina 256:lla, tulos rajataan välille 0...255.
// @alku ydin
int luma(int r, int g, int b) {
    int y = (77 * r + 150 * g + 29 * b) >> 8;
    if (y > 255) {
        y = 255;
    }
    if (y < 0) {
        y = 0;
    }
    return y;
}
// @loppu ydin
