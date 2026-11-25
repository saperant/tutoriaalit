# Pikku-SoC:n esimerkit: rekisterien generointi, ohjelmisto ja simulaatio.
#
#   make             kaikki tarkistukset ja simulaatiot (vertaa odotettuun)
#   make generoi     generoi rekisterilohkot uudelleen gen/-hakemistoon
#   make aja-dma     ajaa yhden ohjelman simulaatiossa ja näyttää tulosteen
#   make siivoa      poistaa build/-hakemiston
#
# Työkalut: Verilator 5, gcc-riscv64-unknown-elf ja Python 3 (ruff, mypy).

RAKENNUS := build
OHJELMAT := kaynnistys keskeytykset dma virheet

# @alku kaannos
CROSS   := riscv64-unknown-elf-
CFLAGS  := -march=rv32i_zicsr -mabi=ilp32 -O2 -std=gnu17 \
           -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns \
           -Wall -Wextra -Werror --param=min-pagesize=0 \
           -Isw -Igen
LDFLAGS := -nostdlib -nostartfiles -T sw/soc.ld -Wl,--gc-sections \
           -Wl,--no-warn-rwx-segments
TUKI    := sw/start.S sw/tuki.c
# @loppu kaannos

RTL := rtl/vaylat.sv gen/syscon_regs.sv gen/gpio_regs.sv \
       rtl/ydin.sv rtl/silta.sv rtl/kytkin.sv rtl/ram.sv rtl/apb_silta.sv \
       rtl/uart.sv rtl/gpio.sv rtl/clint.sv rtl/plic.sv rtl/dma.sv \
       rtl/axil_tarkistin.sv rtl/soc.sv
VFLAGS := --binary -Wall --assert -j 2

.PHONY: kaikki generoitu generoi siivoa cocotb $(addprefix aja-,$(OHJELMAT))

kaikki: generoitu $(OHJELMAT:%=$(RAKENNUS)/%.ok) \
        $(RAKENNUS)/tarkistin.ok $(RAKENNUS)/tehoalue.ok \
        $(RAKENNUS)/purske.ok $(RAKENNUS)/kaavio.ok cocotb

# Generoitujen tiedostojen on vastattava kuvauksia.
generoitu:
	ruff check --no-cache --quiet gen/rekisterit.py
	mypy --strict --no-error-summary \
	    --cache-dir=$(RAKENNUS)/mypy gen/rekisterit.py
	@mkdir -p $(RAKENNUS)/gen
	python3 gen/rekisterit.py gen/syscon.toml $(RAKENNUS)/gen
	python3 gen/rekisterit.py gen/gpio.toml $(RAKENNUS)/gen
	@for f in $(RAKENNUS)/gen/*; do \
	    diff -u gen/$$(basename $$f) $$f || \
	    { echo "gen/ ei ole ajan tasalla: make generoi"; exit 1; }; \
	done

generoi:
	python3 gen/rekisterit.py gen/syscon.toml gen
	python3 gen/rekisterit.py gen/gpio.toml gen

# @alku ohjelma
$(RAKENNUS)/%.elf: sw/%.c $(TUKI) sw/soc.h sw/tuki.h sw/soc.ld \
                   gen/syscon_regs.h gen/gpio_regs.h
	@mkdir -p $(RAKENNUS)
	$(CROSS)gcc $(CFLAGS) $(LDFLAGS) $(TUKI) $< -lgcc -o $@

$(RAKENNUS)/%.hex: $(RAKENNUS)/%.elf
	$(CROSS)objcopy -O verilog --verilog-data-width=4 $< $@
# @loppu ohjelma

$(RAKENNUS)/malli/Vtestipenkki: $(RTL) tb/testipenkki.sv
	@mkdir -p $(RAKENNUS)
	MAKEFLAGS= verilator $(VFLAGS) --top-module testipenkki \
	    -Mdir $(RAKENNUS)/malli -o Vtestipenkki $(RTL) tb/testipenkki.sv \
	    > $(RAKENNUS)/malli.log

# Simulaation tuloste verrataan odotettuun. $finish-ilmoitus poistetaan.
$(RAKENNUS)/%.ok: $(RAKENNUS)/%.hex $(RAKENNUS)/malli/Vtestipenkki \
                  odotettu/%.odotettu
	$(RAKENNUS)/malli/Vtestipenkki +ohjelma=$< \
	    | grep -v 'Verilog \$$finish' > $(RAKENNUS)/$*.tuloste
	diff -u odotettu/$*.odotettu $(RAKENNUS)/$*.tuloste
	@touch $@

$(addprefix aja-,$(OHJELMAT)): aja-%: $(RAKENNUS)/%.hex \
                                     $(RAKENNUS)/malli/Vtestipenkki
	$(RAKENNUS)/malli/Vtestipenkki +ohjelma=$<

# Protokollatarkistin: virheellinen orja on havaittava (simulaatio
# päättyy virheeseen, ja ilmoitus kertoo rikotun säännön).
$(RAKENNUS)/tarkistin.ok: rtl/vaylat.sv rtl/axil_tarkistin.sv \
                          tb/huono_orja.sv odotettu/tarkistin.odotettu
	@mkdir -p $(RAKENNUS)
	MAKEFLAGS= verilator $(VFLAGS) --top-module huono_orja \
	    -Mdir $(RAKENNUS)/tarkistin -o Vhuono_orja rtl/vaylat.sv \
	    rtl/axil_tarkistin.sv tb/huono_orja.sv > $(RAKENNUS)/tark.log
	! $(RAKENNUS)/tarkistin/Vhuono_orja > $(RAKENNUS)/tarkistin.tuloste 2>&1
	grep -o 'huono: R muuttui ennen kättelyä' \
	    $(RAKENNUS)/tarkistin.tuloste | head -1 \
	    | diff -u odotettu/tarkistin.odotettu -
	@touch $@

$(RAKENNUS)/tehoalue.ok: rtl/tehoalue.sv tb/tb_tehoalue.sv \
                         odotettu/tehoalue.odotettu
	@mkdir -p $(RAKENNUS)
	MAKEFLAGS= verilator $(VFLAGS) --top-module tb_tehoalue \
	    -Mdir $(RAKENNUS)/tehoalue -o Vtb_tehoalue rtl/tehoalue.sv \
	    tb/tb_tehoalue.sv > $(RAKENNUS)/teho.log
	$(RAKENNUS)/tehoalue/Vtb_tehoalue \
	    | grep -v 'Verilog \$$finish' > $(RAKENNUS)/tehoalue.tuloste
	diff -u odotettu/tehoalue.odotettu $(RAKENNUS)/tehoalue.tuloste
	@touch $@

# AXI4-purskeet (luku 4): sama kopio sana kerrallaan ja purskeina omassa
# testipenkissään. Lohko ei kuulu SoC:hen, jonka kytkin on AXI4-Lite.
PURSKE := rtl/ram_purske.sv rtl/axi_purske_tarkistin.sv tb/tb_purske.sv
$(RAKENNUS)/purske.ok: $(PURSKE) odotettu/purske.odotettu
	@mkdir -p $(RAKENNUS)
	MAKEFLAGS= verilator $(VFLAGS) --top-module tb_purske \
	    -Mdir $(RAKENNUS)/purske -o Vtb_purske $(PURSKE) \
	    > $(RAKENNUS)/purske.log
	$(RAKENNUS)/purske/Vtb_purske \
	    | grep -v 'Verilog \$$finish' > $(RAKENNUS)/purske.tuloste
	diff -u odotettu/purske.odotettu $(RAKENNUS)/purske.tuloste
	@touch $@

# Kirjan ajoituskaavio (luku 5) tuotetaan käynnistysohjelman
# simulaatiosta: ensimmäinen kirjoitus UARTiin AXI4-Lite-puolelta
# APB-puolelle. Tulos verrataan tiedostoon kaaviot/uart-kirjoitus.json;
# PAIVITA=1 kirjoittaa sen uudelleen.
KAAVIO := python3 ../../yhteiset/kaaviot.py vcd
AXI_S := awvalid=AWVALID,awready=AWREADY,awaddr=AWADDR,wvalid=WVALID
AXI_S := $(AXI_S),wready=WREADY,wdata=WDATA,bvalid=BVALID,bready=BREADY
APB_S := psel=PSEL,penable=PENABLE,pwrite=PWRITE,paddr=PADDR
APB_S := $(APB_S),pwdata=PWDATA,pready=PREADY
TEHO_S := sammuta,kaynnista,vaihe,eristys,kello_paalla,virta
TEHO_S := $(TEHO_S),alue_nollaus_n,sisainen,lahto
# Keskeytys (luku 9): GPIO:n tulon reunasta ytimen ansaan.
KESK_S := g_tulo=tulo,g_reunat=REUNAT[0],g_kesk=gpio_kesk,meip=MEIP
KESK_S := $(KESK_S),y_tila=ydin,y_pc=pc,y_mcause=mcause
# DMA (luku 10): yksi sana DMA:n isäntäportissa ja ytimen haut.
DMA_S := d_tila=DMA,d_arvalid=ARVALID,d_arready=ARREADY,d_rvalid=RVALID
DMA_S := $(DMA_S),d_awvalid=AWVALID,d_wvalid=WVALID,d_bvalid=BVALID
DMA_S := $(DMA_S),y_arvalid=ydin:ARVALID,y_rvalid=ydin:RVALID
# Purske (luku 4): neljän sanan luku ja kirjoitus.
PUR_S := arvalid=ARVALID,arready=ARREADY,arlen=ARLEN,rvalid=RVALID
PUR_S := $(PUR_S),rready=RREADY,rdata=RDATA,rlast=RLAST,awvalid=AWVALID
PUR_S := $(PUR_S),awready=AWREADY,wvalid=WVALID,wready=WREADY,wdata=WDATA
PUR_S := $(PUR_S),wlast=WLAST,bvalid=BVALID,bready=BREADY
MUOTOILE := python3 -m json.tool --indent 1 --no-ensure-ascii
KAAVIOT := uart-kirjoitus tehoalue keskeytys dma-sana purske
$(RAKENNUS)/kaavio.ok: $(RTL) tb/testipenkki.sv $(RAKENNUS)/kaynnistys.hex \
                       $(RAKENNUS)/keskeytykset.hex $(RAKENNUS)/dma.hex \
                       $(KAAVIOT:%=kaaviot/%.json) $(PURSKE) \
                       rtl/tehoalue.sv tb/tb_tehoalue.sv
	MAKEFLAGS= verilator $(VFLAGS) --trace -DJALJITYS \
	    --top-module testipenkki -Mdir $(RAKENNUS)/jalki -o Vtestipenkki \
	    $(RTL) tb/testipenkki.sv > $(RAKENNUS)/jalki.log
	$(RAKENNUS)/jalki/Vtestipenkki +ohjelma=$(RAKENNUS)/kaynnistys.hex \
	    > /dev/null
	$(KAAVIO) $(RAKENNUS)/jalki.vcd --kello kello --alku 161 --jaksot 8 \
	    --signaalit $(AXI_S),$(APB_S) \
	    | python3 -m json.tool --indent 1 --no-ensure-ascii \
	    > $(RAKENNUS)/uart-kirjoitus.json
	rm -f $(RAKENNUS)/jalki.vcd
	if [ "$(PAIVITA)" = 1 ]; then \
	    cp $(RAKENNUS)/uart-kirjoitus.json kaaviot/; fi
	diff -u kaaviot/uart-kirjoitus.json $(RAKENNUS)/uart-kirjoitus.json
	MAKEFLAGS= verilator $(VFLAGS) --trace -DJALJITYS \
	    --top-module tb_tehoalue \
	    -Mdir $(RAKENNUS)/tehojalki -o Vtb_tehoalue rtl/tehoalue.sv \
	    tb/tb_tehoalue.sv > $(RAKENNUS)/tehojalki.log
	$(RAKENNUS)/tehojalki/Vtb_tehoalue > /dev/null
	$(KAAVIO) $(RAKENNUS)/tehoalue.vcd --kello kello --alku 8 --jaksot 16 \
	    --signaalit $(TEHO_S) \
	    | python3 -m json.tool --indent 1 --no-ensure-ascii \
	    > $(RAKENNUS)/tehoalue.json
	rm -f $(RAKENNUS)/tehoalue.vcd
	if [ "$(PAIVITA)" = 1 ]; then cp $(RAKENNUS)/tehoalue.json kaaviot/; fi
	diff -u kaaviot/tehoalue.json $(RAKENNUS)/tehoalue.json
	$(RAKENNUS)/jalki/Vtestipenkki +ohjelma=$(RAKENNUS)/keskeytykset.hex \
	    > /dev/null
	$(KAAVIO) $(RAKENNUS)/jalki.vcd --kello kello --alku 9242 --jaksot 16 \
	    --signaalit $(KESK_S) --luettelo y_tila=HAE:SUORITA:MUISTI \
	    | $(MUOTOILE) > $(RAKENNUS)/keskeytys.json
	$(RAKENNUS)/jalki/Vtestipenkki +ohjelma=$(RAKENNUS)/dma.hex > /dev/null
	$(KAAVIO) $(RAKENNUS)/jalki.vcd --kello kello --alku 8969 --jaksot 14 \
	    --signaalit $(DMA_S) \
	    --luettelo d_tila=VAPAA:LUE:ODOTA_R:KIRJOITA:ODOTA_B \
	    | $(MUOTOILE) > $(RAKENNUS)/dma-sana.json
	rm -f $(RAKENNUS)/jalki.vcd
	MAKEFLAGS= verilator $(VFLAGS) --trace -DJALJITYS \
	    --top-module tb_purske -Mdir $(RAKENNUS)/purskejalki \
	    -o Vtb_purske $(PURSKE) > $(RAKENNUS)/purskejalki.log
	$(RAKENNUS)/purskejalki/Vtb_purske > /dev/null
	$(KAAVIO) $(RAKENNUS)/purske.vcd --kello kello --alku 4 --jaksot 13 \
	    --naytteistys ennen --kanta d --signaalit $(PUR_S) \
	    | $(MUOTOILE) > $(RAKENNUS)/purske.json
	rm -f $(RAKENNUS)/purske.vcd
	for k in keskeytys dma-sana purske; do \
	    if [ "$(PAIVITA)" = 1 ]; then cp $(RAKENNUS)/$$k.json kaaviot/; fi; \
	    diff -u kaaviot/$$k.json $(RAKENNUS)/$$k.json || exit 1; \
	done
	@touch $@

.PRECIOUS: $(RAKENNUS)/%.elf $(RAKENNUS)/%.hex

# --- Luku 13: cocotb-testit -------------------------------------------
#
# RAM (AXI4-Lite) ja GPIO (APB) testataan Pythonilla Icarus Verilogissa
# (cocotb-testit/aja.py). Kääreet tb/cocotb_*.sv tuovat väylän signaalit
# erillisinä portteina. Tuloste verrataan tiedostoon
# cocotb-testit/odotettu/<ajo>.odotettu; mutaatioajoissa lähteeseen
# istutetaan vika, ja testien on huomattava se (paluuarvo 1).

COCOTB := python3 cocotb-testit/aja.py
RAM_C  := --top cocotb_ram --moduuli test_ram --lahde rtl/vaylat.sv \
          --lahde rtl/ram.sv --lahde tb/cocotb_ram.sv
GPIO_C := --top cocotb_gpio --moduuli test_gpio --lahde rtl/vaylat.sv \
          --lahde gen/gpio_regs.sv --lahde rtl/gpio.sv \
          --lahde tb/cocotb_gpio.sv

# cocotb_ajo NIMI ODOTETTU_PALUUARVO VALITSIMET
define cocotb_ajo
$(RAKENNUS)/cocotb-$(1).ok: cocotb-testit/odotettu/$(1).odotettu \
    $(wildcard cocotb-testit/*.py rtl/*.sv gen/*.sv tb/cocotb_*.sv)
	@mkdir -p $(RAKENNUS)
	@$(COCOTB) $(3) > $(RAKENNUS)/cocotb-$(1).tuloste; tila=$$$$?; \
	diff -u cocotb-testit/odotettu/$(1).odotettu \
	    $(RAKENNUS)/cocotb-$(1).tuloste || exit 1; \
	[ $$$$tila -eq $(2) ] || \
	    { echo "cocotb $(1): paluuarvo $$$$tila"; exit 1; }
	@touch $$@
COCOTB_AJOT += $(RAKENNUS)/cocotb-$(1).ok
endef

$(eval $(call cocotb_ajo,ram,0,$(RAM_C)))
$(eval $(call cocotb_ajo,ram-rready,1,$(RAM_C) \
    --mutaatio 'end else if (m.rready) begin=>end else begin'))
$(eval $(call cocotb_ajo,ram-wstrb,1,$(RAM_C) \
    --mutaatio '| (m.wdata & maski)=>| m.wdata'))
$(eval $(call cocotb_ajo,gpio,0,$(GPIO_C)))
# Mutaatiossa on pariton sulkumerkki, joten se annetaan muuttujana.
W1C_VIKA := "(reunat_q & ~8'(=>(reunat_q & 8'("
$(eval $(call cocotb_ajo,gpio-w1c,1,$(GPIO_C) --mutaatio $(W1C_VIKA)))
$(eval $(call cocotb_ajo,gpio-pslverr,1,$(GPIO_C) \
    --mutaatio "apb_s.pslverr = kirjoita;=>apb_s.pslverr = 1'b0;"))

cocotb: $(COCOTB_AJOT)
	@cd cocotb-testit && ruff check -q --no-cache . \
	    && mypy --no-error-summary --cache-dir=/dev/null .

siivoa:
	rm -rf $(RAKENNUS) cocotb-testit/__pycache__
