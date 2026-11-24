// Satunnaisärsyke ilman tulostaulua: vain väitteet tarkistavat
// FIFOn. Siemen annetaan argumenttina +siemen=N.
module testipenkki;
    logic       clk = 1'b0, rst = 1'b1, push = 1'b0, pop = 1'b0;
    logic [7:0] din = '0, dout;
    logic       tyhja, taysi;
    logic [2:0] maara;
    logic       kaynnissa = 1'b1;

    fifo #(.SYVYYS(4), .LEVEYS(8)) dut (.*);
    initial while (kaynnissa) #5 clk = ~clk;

    initial begin
        int unsigned siemen = 1;
        void'($value$plusargs("siemen=%d", siemen));
        void'($urandom(siemen));
        repeat (2) @(negedge clk);
        rst = 1'b0;
        repeat (2000) begin
            @(negedge clk);
            push = ($urandom_range(99) < 50);
            pop  = ($urandom_range(99) < 50);
            din  = 8'($urandom);
        end
        $display("siemen %0d: 2000 jaksoa, väitteet läpi", siemen);
        $display("lopputila: maara=%0d tyhja=%b taysi=%b dout=%02h",
                 maara, tyhja, taysi, dout);
        kaynnissa = 1'b0;
    end
endmodule
