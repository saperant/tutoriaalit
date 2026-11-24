// Field: ajastin.STATUS.VALMIS
always_comb begin
    automatic logic [0:0] next_c;
    automatic logic load_next_c;
    next_c = field_storage.STATUS.VALMIS.value;
    load_next_c = '0;
    if(decoded_reg_strb.STATUS && decoded_req_is_wr) begin // SW write 1 clear
        next_c = field_storage.STATUS.VALMIS.value & ~(decoded_wr_data[0:0] &
                decoded_wr_biten[0:0]);
        load_next_c = '1;
    end else if(hwif_in.STATUS.VALMIS.hwset) begin // HW Set
        next_c = '1;
        load_next_c = '1;
    end
    field_combo.STATUS.VALMIS.next = next_c;
    field_combo.STATUS.VALMIS.load_next = load_next_c;
end
always_ff @(posedge clk) begin
    if(rst) begin
        field_storage.STATUS.VALMIS.value <= 1'h0;
    end else begin
        if(field_combo.STATUS.VALMIS.load_next) begin
            field_storage.STATUS.VALMIS.value <=
                    field_combo.STATUS.VALMIS.next;
        end
    end
end
assign hwif_out.STATUS.intr =
    |(field_storage.STATUS.VALMIS.value & field_storage.CTRL.IE.value);
