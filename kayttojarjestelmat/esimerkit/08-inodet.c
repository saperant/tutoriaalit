// Nimet ja inodet: kova linkki on toinen nimi samalle inodelle,
// symbolinen linkki on oma tiedostonsa, joka sisältää polun.
#define _GNU_SOURCE
#include <dirent.h>
#include <fcntl.h>
#include <stdint.h>
#include <sys/stat.h>
#include <unistd.h>

#include "tarkista.h"

static const char *tyyppi(mode_t m) {
    return S_ISREG(m) ? "tavallinen" : S_ISDIR(m) ? "hakemisto"
         : S_ISLNK(m) ? "symbolinen linkki" : "muu";
}

static int vertaa(const void *a, const void *b) {
    return strcmp(*(char *const *)a, *(char *const *)b);
}

int main(void) {
    // @alku linkit
    int fd = TARKISTA(open("alkuperainen.txt",
                           O_WRONLY | O_CREAT | O_TRUNC, 0644));
    TARKISTA(write(fd, "sisältö\n", 9));
    TARKISTA(close(fd));
    TARKISTA(link("alkuperainen.txt", "kova.txt"));
    TARKISTA(symlink("alkuperainen.txt", "symbolinen.txt"));

    struct stat a, k, s, ls;
    TARKISTA(stat("alkuperainen.txt", &a));
    TARKISTA(stat("kova.txt", &k));
    TARKISTA(stat("symbolinen.txt", &s));    // seuraa linkkiä
    TARKISTA(lstat("symbolinen.txt", &ls));  // ei seuraa
    printf("kova linkki: sama inode %s, linkkejä %ju\n",
           a.st_ino == k.st_ino ? "kyllä" : "ei", (uintmax_t)a.st_nlink);
    printf("stat(symbolinen): %s, sama inode %s\n", tyyppi(s.st_mode),
           s.st_ino == a.st_ino ? "kyllä" : "ei");
    printf("lstat(symbolinen): %s, koko %jd = strlen(\"%s\")\n",
           tyyppi(ls.st_mode), (intmax_t)ls.st_size, "alkuperainen.txt");

    TARKISTA(unlink("alkuperainen.txt"));
    TARKISTA(stat("kova.txt", &k));
    printf("unlink: kova.txt linkkejä %ju, data tallessa\n",
           (uintmax_t)k.st_nlink);
    if (stat("symbolinen.txt", &s) == -1) {
        printf("symbolinen linkki roikkuu: %s\n", strerrorname_np(errno));
    }
    // @loppu linkit

    // @alku hakemisto
    TARKISTA(mkdir("hak", 0755));
    const char *nimet[] = {"hak/b", "hak/a", "hak/c"};
    for (int i = 0; i < 3; i++) {
        TARKISTA(close((int)TARKISTA(open(nimet[i], O_CREAT | O_WRONLY,
                                          0644))));
    }
    // readdir palauttaa nimet tiedostojärjestelmän omassa järjestyksessä.
    DIR *d = opendir("hak");
    if (d == nullptr) {
        perror("opendir");
        return 1;
    }
    char *loydetyt[8];
    int n = 0;
    for (struct dirent *e; (e = readdir(d)) != nullptr && n < 8;) {
        loydetyt[n++] = strdup(e->d_name);
    }
    closedir(d);
    qsort(loydetyt, (size_t)n, sizeof loydetyt[0], vertaa);
    printf("hak:");
    for (int i = 0; i < n; i++) {
        printf(" %s", loydetyt[i]);
        free(loydetyt[i]);
    }
    printf("\n");
    // @loppu hakemisto

    // @alku harva
    fd = TARKISTA(open("harva.bin", O_WRONLY | O_CREAT | O_TRUNC, 0644));
    TARKISTA(lseek(fd, 1 << 20, SEEK_SET));  // 1 MiB:n aukko
    TARKISTA(write(fd, "x", 1));
    TARKISTA(fstat(fd, &a));
    TARKISTA(close(fd));
    printf("harva tiedosto: koko %jd, levyllä alle 64 KiB: %s\n",
           (intmax_t)a.st_size,
           a.st_blocks * 512 < 64 * 1024 ? "kyllä" : "ei");
    // @loppu harva
    return 0;
}
