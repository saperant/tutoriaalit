# Globaali data x86-64:llä: osoitus käskyosoittimen suhteen.

# @alku osiot
    .section .rodata            # vain luettava data: vakiotaulukot
alkuluvut:
    .quad 2, 3, 5, 7, 11

    .data                       # alustettu, kirjoitettava data
    .globl laskuri
laskuri:
    .quad 100

    .bss                        # nollilla alustettu: ei vie tilaa
    .globl kutsuja              # ohjelmatiedostossa
kutsuja:
    .zero 8
# @loppu osiot

    .text
# @alku seuraava
# long seuraava(void): kasvattaa laskuria ja palauttaa uuden arvon.
    .globl seuraava
seuraava:
    incq kutsuja(%rip)          # muistioperandi: lue, kasvata, kirjoita
    mov laskuri(%rip), %rax     # osoite = rip + siirtymä
    inc %rax
    mov %rax, laskuri(%rip)
    ret
# @loppu seuraava

# @alku alkuluku
# long alkuluku(long i): taulukon i:s alkio.
    .globl alkuluku
alkuluku:
    lea alkuluvut(%rip), %rax   # taulukon osoite rekisteriin
    mov (%rax,%rdi,8), %rax
    ret
# @loppu alkuluku

# @alku vakio
# unsigned long vakio(void): 64-bittinen vakio käskyn sisällä.
    .globl vakio
vakio:
    movabs $0x123456789abcdef0, %rax
    ret
# @loppu vakio
    .section .note.GNU-stack,"",@progbits
