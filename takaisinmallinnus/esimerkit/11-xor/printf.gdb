# Tulostaa jokaisen printf-kutsun merkkijonoargumentin. Ubuntun GCC
# kääntää -O2:lla printf-kutsut muotoon __printf_chk(lippu, muoto, ...),
# joten ensimmäinen muotoiltava argumentti on rekisterissä rdx.
# @alku printf
break __printf_chk
commands
    silent
    printf "> %s\n", (char *)$rdx
    continue
end
run > /dev/null
# @loppu printf
