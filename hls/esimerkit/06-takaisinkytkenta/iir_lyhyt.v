// Tuottanut minihls: iir
module iir (
    input  wire               clk,
    input  wire               rst,
    input  wire               ap_start,
    output wire               ap_done,
    output wire               ap_idle,
    output wire               ap_ready,
    output wire         [3:0] x_address0,
    output wire               x_ce0,
    input  wire signed [31:0] x_q0,
    output wire         [3:0] y_address1,
    output wire               y_we1,
    output wire signed [31:0] y_d1
);
    // Tilakone
    localparam S_IDLE = 2'd0;
    localparam S_LOHKO1 = 2'd1;
    localparam S_SUODATUS = 2'd2;
    localparam S_DONE = 2'd3;
    reg [1:0] tila;
// @alku vaiheet
    reg [3:0] l2_n;
    reg [3:0] l2_v;
    wire l2_uusi = l2_v[0] && l2_n != 4'd15;
    wire [3:0] l2_vs = {l2_v[2:0], l2_uusi};
    wire l1_j0 = tila == S_LOHKO1;
    wire l2_j0 = tila == S_SUODATUS && l2_v[0];
    wire l2_j1 = tila == S_SUODATUS && l2_v[1];
    wire l2_j2 = tila == S_SUODATUS && l2_v[2];
    wire l2_j3 = tila == S_SUODATUS && l2_v[3];
// @loppu vaiheet
    assign ap_done = tila == S_DONE;
    assign ap_idle = tila == S_IDLE;
    assign ap_ready = tila == S_DONE;
// @alku muuttujat
    // Muuttujat ja vaiherekisterit
    reg signed [31:0] m_tila;
    reg signed [31:0] t3_v1;
    reg signed [31:0] t3_v2;
    reg signed [31:0] t3_v3;
    reg signed [31:0] t5_v2;
    reg signed [31:0] t7_v3;
// @loppu muuttujat
// @alku datapolku
    // Datapolku
    // lohko1: II 1, vaiheita 1
    // suodatus: II 1, vaiheita 4
    wire signed [31:0] t1 = m_tila;
    wire signed [31:0] t2 = t1 * 32'sd179;
    wire signed [31:0] t3 = {28'd0, l2_n};
    wire signed [31:0] t4 = x_q0;
    wire signed [31:0] t5 = t4 * 32'sd77;
    wire signed [31:0] t6 = t2 + t5_v2;
    wire signed [31:0] t7 = t6 >>> 32'sd8;
// @loppu datapolku
// @alku kytkennat
    // Portit
    assign x_address0 = t3[3:0];
    assign x_ce0 = l2_j0;
    assign y_address1 = t3_v3[3:0];
    assign y_we1 = l2_j3;
    assign y_d1 = t7_v3;
// @loppu kytkennat
    always @(posedge clk) begin
        if (rst) begin
            tila <= S_IDLE;
        end else begin
            case (tila)
            S_IDLE: if (ap_start) begin
                tila <= S_LOHKO1;
            end
            S_LOHKO1: begin
                tila <= S_SUODATUS;
                l2_n <= 0;
                l2_v <= 1;
            end
// @alku ohjaus
            S_SUODATUS: begin
                l2_v <= l2_vs;
                if (l2_uusi) l2_n <= l2_n + 1'b1;
                if (l2_vs == 0) begin
                    tila <= S_DONE;
                end
            end
// @loppu ohjaus
            S_DONE: tila <= S_IDLE;
            default: tila <= S_IDLE;
            endcase
        end
    end
// @alku paivitykset
    always @(posedge clk) begin
        if (l1_j0) m_tila <= 32'sd0;
        if (l2_j2) m_tila <= t7;
        if (l2_j0) t3_v1 <= t3;
        if (tila == S_SUODATUS) t3_v2 <= t3_v1;
        if (tila == S_SUODATUS) t3_v3 <= t3_v2;
        if (l2_j1) t5_v2 <= t5;
        if (l2_j2) t7_v3 <= t7;
    end
// @loppu paivitykset
endmodule
