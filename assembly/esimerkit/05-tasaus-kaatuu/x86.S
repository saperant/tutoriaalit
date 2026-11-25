# Virheellinen kutsu: pinoa ei tasata 16 tavun rajalle ennen kutsua.
    .text
# @alku vaarin
# void kutsu(void (*f)(double), double x)
    .globl kutsu
kutsu:
    call *%rdi                  # VIRHE: rsp on 16:n monikerta + 8
    ret
# @loppu vaarin
    .section .note.GNU-stack,"",@progbits
