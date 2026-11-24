# Käynnistysketju Cortex-M3:lle (QEMU mps2-an385).
#
#   make           rakentaa käynnistimen ja kuvat ja ajaa skenaariot
#   make siivoa    poistaa rakennushakemiston
#
# Skenaarion tuloste ja paluuarvo verrataan tiedostoon
# testit/<skenaario>.odotettu.

CC      := arm-none-eabi-gcc
OBJCOPY := arm-none-eabi-objcopy
CFLAGS  := -mcpu=cortex-m3 -mthumb -Os -std=c11 -Wall -Wextra -Werror \
           -ffreestanding -ffunction-sections -fdata-sections
LDFLAGS := -nostartfiles --specs=nano.specs --specs=nosys.specs \
           -Wl,--gc-sections
R       := rakennus
TYOKALU := python3 ../03-kuvatyokalu.py
# RFC 8032:n testiavaimet: julkisia, joten vain kokeiluihin.
VALMISTAJA := 9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60
VIERAS     := 4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb
QEMU := timeout 60 qemu-system-arm -M mps2-an385 -nographic -monitor none \
        -serial none -semihosting-config enable=on,target=native

SKENAARIOT := perus peukaloitu palautus vieras-avain ab-paivitys

.PHONY: kaikki siivoa
kaikki: $(SKENAARIOT:%=$(R)/%.tulos)

$(R):
	mkdir -p $@

$(R)/julkinen_avain.h: ../03-kuvatyokalu.py | $(R)
	$(TYOKALU) julkinen $(VALMISTAJA) > $@

$(R)/kaynnistin.elf: lahde/kaynnistin.c lahde/sha512.c lahde/ed25519.c \
                     lahde/semihost.c ulkoiset/monocypher/monocypher.c \
                     laite.ld $(R)/julkinen_avain.h
	$(CC) $(CFLAGS) -Ilahde -Iulkoiset/monocypher -I$(R) -Tlaite.ld \
	    $(LDFLAGS) $(filter %.c,$^) -o $@

# Sovellukset: rakennus/sovellus-<paikka>-v<versio>.bin
$(R)/sovellus-%.ld: sovellus.ld.in | $(R)
	sed 's/@ALKU@/$(if $(filter A,$*),0x00100100,0x00180100)/' $< > $@

$(R)/sovellus-A-v%.elf: lahde/sovellus.c lahde/semihost.c $(R)/sovellus-A.ld
	$(CC) $(CFLAGS) -DVERSIO=$* -Ilahde -T$(R)/sovellus-A.ld $(LDFLAGS) \
	    $(filter %.c,$^) -o $@
$(R)/sovellus-B-v%.elf: lahde/sovellus.c lahde/semihost.c $(R)/sovellus-B.ld
	$(CC) $(CFLAGS) -DVERSIO=$* -Ilahde -T$(R)/sovellus-B.ld $(LDFLAGS) \
	    $(filter %.c,$^) -o $@
$(R)/%.bin: $(R)/%.elf
	$(OBJCOPY) -O binary -j .text $< $@

# Allekirjoitetut kuvat: valmistajan avaimella tai vieraalla avaimella.
$(R)/kuva-%.bin: $(R)/sovellus-%.bin ../03-kuvatyokalu.py
	$(TYOKALU) kuva $(VALMISTAJA) $(lastword $(subst -v, ,$*)) $< $@
$(R)/vieras-%.bin: $(R)/sovellus-%.bin ../03-kuvatyokalu.py
	$(TYOKALU) kuva $(VIERAS) $(lastword $(subst -v, ,$*)) $< $@
$(R)/peukaloitu-%.bin: $(R)/kuva-%.bin
	cp $< $@ && $(TYOKALU) peukaloi $@
$(R)/otp-%.bin: ../03-kuvatyokalu.py | $(R)
	$(TYOKALU) otp $* $@

A = -device loader,file=$(1),addr=0x00100000
B = -device loader,file=$(1),addr=0x00180000
OTP = -device loader,file=$(R)/otp-$(1).bin,addr=0x003F0000

# aja,skenaario,qemu-valitsimet: tuloste ja paluuarvo vertailuun.
define aja
	@{ $(QEMU) -kernel $(R)/kaynnistin.elf $(2); \
	   echo "paluuarvo $$?"; } > $(R)/$(1).tuloste 2>&1
	@diff -u testit/$(1).odotettu $(R)/$(1).tuloste
	@touch $@
endef

# @alku skenaariot
$(R)/perus.tulos: $(R)/kaynnistin.elf $(R)/kuva-A-v3.bin $(R)/otp-2.bin
	$(call aja,perus,$(call A,$(R)/kuva-A-v3.bin) $(call OTP,2))

$(R)/peukaloitu.tulos: $(R)/kaynnistin.elf $(R)/peukaloitu-A-v3.bin \
                       $(R)/kuva-B-v2.bin $(R)/otp-2.bin
	$(call aja,peukaloitu,$(call A,$(R)/peukaloitu-A-v3.bin) \
	    $(call B,$(R)/kuva-B-v2.bin) $(call OTP,2))

$(R)/palautus.tulos: $(R)/kaynnistin.elf $(R)/kuva-A-v1.bin $(R)/otp-2.bin
	$(call aja,palautus,$(call A,$(R)/kuva-A-v1.bin) $(call OTP,2))

$(R)/vieras-avain.tulos: $(R)/kaynnistin.elf $(R)/vieras-A-v3.bin \
                         $(R)/otp-2.bin
	$(call aja,vieras-avain,$(call A,$(R)/vieras-A-v3.bin) $(call OTP,2))

$(R)/ab-paivitys.tulos: $(R)/kaynnistin.elf $(R)/kuva-A-v2.bin \
                        $(R)/kuva-B-v3.bin $(R)/otp-2.bin
	$(call aja,ab-paivitys,$(call A,$(R)/kuva-A-v2.bin) \
	    $(call B,$(R)/kuva-B-v3.bin) $(call OTP,2))
# @loppu skenaariot

siivoa:
	rm -rf $(R)
