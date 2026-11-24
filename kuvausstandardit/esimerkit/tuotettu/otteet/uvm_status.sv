// reg - ajastin.STATUS
class ajastin__STATUS extends uvm_reg;
    rand uvm_reg_field VALMIS;

    function new(string name = "ajastin__STATUS");
        super.new(name, 32, UVM_NO_COVERAGE);
    endfunction : new

    virtual function void build();
        this.VALMIS = new("VALMIS");
        this.VALMIS.configure(this, 1, 0, "W1C", 1, 'h0, 1, 1, 0);
    endfunction : build
endclass : ajastin__STATUS
