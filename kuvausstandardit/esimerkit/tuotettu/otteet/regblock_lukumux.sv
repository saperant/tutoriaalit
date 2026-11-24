if(rd_mux_addr == 4'h0) begin
    readback_data_var[0] = field_storage.CTRL.EN.value;
    readback_data_var[1] = field_storage.CTRL.IE.value;
    readback_data_var[15:8] = field_storage.CTRL.JAKAJA.value;
end
if(rd_mux_addr == 4'h4) begin
    readback_data_var[0] = field_storage.STATUS.VALMIS.value;
end
if(rd_mux_addr == 4'h8) begin
    readback_data_var[15:0] = hwif_in.LASKURI.ARVO.next;
end
if(rd_mux_addr == 4'hc) begin
    readback_data_var[15:0] = field_storage.VERTAA.ARVO.value;
end
