// Ohjelma ilman C-kirjastoa: oma _start ja järjestelmäkutsut.
// @alku irrallinen
static long kirjoita(int fd, const void *p, unsigned long n)
{
    long r;
    __asm__ volatile("syscall"
                     : "=a"(r)
                     : "a"(1L), "D"((long)fd), "S"(p), "d"(n)
                     : "rcx", "r11", "memory");
    return r;
}

static const char viesti[] = "hei ilman C-kirjastoa\n";

__attribute__((noreturn)) void _start(void)
{
    kirjoita(1, viesti, sizeof viesti - 1);
    __asm__ volatile("syscall" : : "a"(60L), "D"(0L));   // exit(0)
    __builtin_unreachable();
}
// @loppu irrallinen
