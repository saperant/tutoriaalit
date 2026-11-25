# Asennussäännöt. PREFIX on hakemisto, josta tiedostot löytyvät
# käytössä; DESTDIR on väliaikainen juuri, jonka alle ne kopioidaan
# paketointia varten:
#
#   make -f asennus.mk install PREFIX=/usr DESTDIR=/tmp/paketti

# @alku asennus
PREFIX     ?= /usr/local
LIBDIR     := $(PREFIX)/lib
INCLUDEDIR := $(PREFIX)/include

.PHONY: install
install: libtilasto.a lahde/tilasto.h tilasto.pc.in
	install -d $(DESTDIR)$(LIBDIR)/pkgconfig $(DESTDIR)$(INCLUDEDIR)
	install -m 644 libtilasto.a $(DESTDIR)$(LIBDIR)/
	install -m 644 lahde/tilasto.h $(DESTDIR)$(INCLUDEDIR)/
	sed 's|@PREFIX@|$(PREFIX)|' tilasto.pc.in \
	    > $(DESTDIR)$(LIBDIR)/pkgconfig/tilasto.pc
# @loppu asennus
