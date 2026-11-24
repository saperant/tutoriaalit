SUMMARY = "Tutoriaalin pieni init-järjestelmä palveluineen"
LICENSE = "CC-BY-SA-4.0"
# Lisenssin tunniste tarkistetaan lähdetiedoston riveiltä 1-4.
LIC_FILES_CHKSUM = "file://minit.c;beginline=1;endline=4;\
md5=24bb0f3c39fd156371d4fd29cb533e5d"

SRC_URI = "file://minit.c file://palvelu.c file://palvelut.conf"
S = "${WORKDIR}"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} minit.c -o minit
    ${CC} ${CFLAGS} ${LDFLAGS} palvelu.c -o palvelu
}

do_install() {
    install -D -m 0755 minit ${D}${base_sbindir}/minit
    install -D -m 0755 palvelu ${D}${base_sbindir}/palvelu
    install -D -m 0644 palvelut.conf ${D}${sysconfdir}/palvelut.conf
}
