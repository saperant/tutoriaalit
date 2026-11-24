this.default_map = create_map("reg_map", 0, 4, UVM_NO_ENDIAN);
this.CTRL = new("CTRL");
this.CTRL.configure(this);

this.CTRL.build();
this.default_map.add_reg(this.CTRL, 'h0);
this.STATUS = new("STATUS");
this.STATUS.configure(this);

this.STATUS.build();
this.default_map.add_reg(this.STATUS, 'h4);
