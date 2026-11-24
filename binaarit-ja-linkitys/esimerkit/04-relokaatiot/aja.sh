#!/usr/bin/env bash
# Relokaatiot: kääntäjä jättää viittausten osoitteet linkkerille.
source ./yhteinen.sh

"$CC" "${CFLAGS[@]}" -c varasto.c -o varasto.o
"$CC" "${CFLAGS[@]}" -c main.c -o main.o

# Konekieli ilman osoitteita ja tavuja, vain funktio tilaa.
tilaa_konekieli() {
    objdump "$@" --no-show-raw-insn --no-addresses --disassemble=tilaa |
        sed -n '/<tilaa>:/,/^$/p' | sed '/^$/d' | expand -t 4 |
        sed -E 's/0x[1-9a-f][0-9a-f]*\(%rip\)/SIIRTYMA(%rip)/; s/ +# / # /'
}

otsikko "tilaa ennen linkitystä (objdump -dr main.o)"
# @alku ennen
tilaa_konekieli -dr main.o
# @loppu ennen

otsikko "relokaatiot (readelf -r main.o)"
# @alku relokaatiot
readelf -r -W main.o | awk '/^[0-9a-f]+ / && $5 ~ /^(saldo|lisaa)/ {
    print $3, $5 }'
# @loppu relokaatiot

otsikko "tilaa linkityksen jälkeen"
"$CC" main.o varasto.o -o tilaus
# @alku jalkeen
tilaa_konekieli -d tilaus
# @loppu jalkeen
./tilaus
