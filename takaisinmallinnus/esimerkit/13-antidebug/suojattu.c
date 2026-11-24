// Ohjelma, joka yrittää havaita debuggerin kahdella tavalla.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>

// @alku havaitse
// Prosessilla voi olla vain yksi jäljittäjä: jos debuggeri jäljittää
// jo, PTRACE_TRACEME epäonnistuu.
static int ptrace_epaonnistuu(void)
{
    return ptrace(PTRACE_TRACEME, 0, NULL, NULL) == -1;
}

// /proc/self/status kertoo jäljittäjän prosessinumeron (0 = ei ole).
[[gnu::noinline]] static int jaljittajan_pid(void)
{
    FILE *f = fopen("/proc/self/status", "r");
    char rivi[128];
    int pid = 0;
    while (f != NULL && fgets(rivi, sizeof rivi, f) != NULL) {
        if (strncmp(rivi, "TracerPid:", 10) == 0) {
            pid = atoi(rivi + 10);
        }
    }
    if (f != NULL) {
        fclose(f);
    }
    return pid;
}

// TracerPid tarkistetaan ensin: onnistunut PTRACE_TRACEME tekee
// vanhemmasta (esim. komentotulkista) jäljittäjän.
[[gnu::noinline]] int debuggeri_havaittu(void)
{
    if (jaljittajan_pid() != 0) {
        puts("tarkistus 1: TracerPid ei ole 0");
        return 1;
    }
    if (ptrace_epaonnistuu()) {
        puts("tarkistus 2: ptrace epäonnistui");
        return 1;
    }
    return 0;
}
// @loppu havaitse

int main(void)
{
    if (debuggeri_havaittu()) {
        puts("debuggeri havaittu, lopetetaan");
        return 3;
    }
    puts("suojattu toiminto suoritettu");
    return 0;
}
