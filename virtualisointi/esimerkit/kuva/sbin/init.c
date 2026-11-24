// Minikontin init: ensimmäinen prosessi omissa nimiavaruuksissaan.
// Käännetään staattisesti, koska kontin juuressa ei ole kirjastoja.
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <unistd.h>

static int prosesseja(void)
{
    int n = 0;
    DIR *d = opendir("/proc");
    if (d == NULL)
        return -1;
    for (struct dirent *e; (e = readdir(d)) != NULL;)
        n += e->d_name[0] >= '0' && e->d_name[0] <= '9';
    closedir(d);
    return n;
}

int main(void)
{
    // @alku init
    if (sethostname("minikontti", 10) != 0 ||
        mount("proc", "/proc", "proc", 0, NULL) != 0) {
        perror("init");
        return 1;
    }
    char nimi[64];
    gethostname(nimi, sizeof nimi);
    printf("PID %d, konenimi %s, näkyviä prosesseja %d\n",
           (int)getpid(), nimi, prosesseja());

    // Verkkonimiavaruudessa on aluksi vain silmukkaliitäntä.
    FILE *f = fopen("/proc/net/dev", "r");
    char rivi[256];
    while (f != NULL && fgets(rivi, sizeof rivi, f) != NULL)
        if (strchr(rivi, ':') != NULL)
            printf("verkkoliitäntä: %s", strtok(rivi, " :"));
    if (f != NULL) {
        fclose(f);
        puts("");
    }

    // Kirjoitus kohdistuu overlayn ylimpään, kirjoitettavaan kerrokseen.
    FILE *t = fopen("/data/terveiset.txt", "w");
    if (t == NULL || fputs("hei kontista\n", t) == EOF || fclose(t))
        return 1;
    // @loppu init
    return 0;
}
