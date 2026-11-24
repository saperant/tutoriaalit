# Valinnaiset esimerkit, jotka tarvitsevat ympäristöltä jotain, mitä
# kaikissa ei ole: KVM-laitteen (/dev/kvm) tai kirjoitettavan
# cgroup-tiedostojärjestelmän. Ne ajetaan, jos mahdollista, ja muuten
# ohitetaan ilmoituksella. KVM-esimerkki käännetään aina.
#
#   make           kääntää ja ajaa valinnaiset esimerkit
#   make siivoa    poistaa käännöstuotteet

CC := $(shell command -v gcc-14 || command -v gcc)
CFLAGS := -std=c23 -Wall -Wextra -Wpedantic -Werror

.PHONY: kaikki kvm cgroups siivoa

kaikki: kvm cgroups

valinnaiset/kvm/kvm: valinnaiset/kvm/kvm.c
	$(CC) $(CFLAGS) -o $@ $<

kvm: valinnaiset/kvm/kvm
	@if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then \
	    ./valinnaiset/kvm/kvm | diff -u valinnaiset/kvm/kvm.odotettu - \
	        && echo "OK: KVM-esimerkki"; \
	else \
	    echo "kvm: /dev/kvm ei ole käytettävissä, ajo ohitetaan" >&2; \
	fi

cgroups:
	@tulos=$$(bash valinnaiset/cgroups/pids.sh) && rc=0 || rc=$$?; \
	if [ $$rc -eq 77 ]; then \
	    echo "cgroups: ei kirjoitusoikeutta, ajo ohitetaan" >&2; \
	elif [ $$rc -ne 0 ]; then \
	    echo "cgroups: virhe ($$rc)" >&2; exit 1; \
	else \
	    echo "$$tulos" | diff -u valinnaiset/cgroups/pids.odotettu - \
	        && echo "OK: cgroups-esimerkki"; \
	fi

siivoa:
	rm -f valinnaiset/kvm/kvm
