// Tuottanut minihls: mac
// @alku portit
module mac (
    input  wire               clk,
    input  wire               rst,
    input  wire               ap_start,
    output wire               ap_done,
    output wire               ap_idle,
    output wire               ap_ready,
    output wire         [2:0] a_address0,
    output wire               a_ce0,
    input  wire signed [31:0] a_q0,
    output wire         [2:0] b_address0,
    output wire               b_ce0,
    input  wire signed [31:0] b_q0,
    output reg  signed [31:0] ap_return
);
// @loppu portit
// @alku tilakone
    // Tilakone
    localparam S_IDLE = 3'd0;
    localparam S_LOHKO1 = 3'd1;
    localparam S_KERTOLASKU = 3'd2;
    localparam S_LOHKO3 = 3'd3;
    localparam S_DONE = 3'd4;
    reg [2:0] tila;
    reg [2:0] l2_n;
    reg [0:0] l2_ks;
    wire l1_j0 = tila == S_LOHKO1;
    wire l2_j0 = tila == S_KERTOLASKU && l2_ks == 1'd0;
    wire l2_j1 = tila == S_KERTOLASKU && l2_ks == 1'd1;
    wire l3_j0 = tila == S_LOHKO3;
    assign ap_done = tila == S_DONE;
    assign ap_idle = tila == S_IDLE;
    assign ap_ready = tila == S_DONE;
// @loppu tilakone
// @alku datapolku
    // Muuttujat ja vaiherekisterit
    reg signed [31:0] m_s;
    // Datapolku
    // lohko1: II 1, vaiheita 1
    // kertolasku: II 2, vaiheita 1
    wire signed [31:0] t1 = m_s;
    wire signed [31:0] t2 = {29'd0, l2_n};
    wire signed [31:0] t3 = a_q0;
    wire signed [31:0] t4 = b_q0;
    wire signed [31:0] t5 = t3 * t4;
    wire signed [31:0] t6 = t1 + t5;
    // lohko3: II 1, vaiheita 1
    wire signed [31:0] t8 = m_s;
// @loppu datapolku
// @alku kytkennat
    // Portit
    assign a_address0 = t2[2:0];
    assign a_ce0 = l2_j0;
    assign b_address0 = t2[2:0];
    assign b_ce0 = l2_j0;
// @loppu kytkennat
// @alku ohjaus
    always @(posedge clk) begin
        if (rst) begin
            tila <= S_IDLE;
        end else begin
            case (tila)
            S_IDLE: if (ap_start) begin
                tila <= S_LOHKO1;
            end
            S_LOHKO1: begin
                tila <= S_KERTOLASKU;
                l2_n <= 0;
                l2_ks <= 0;
            end
            S_KERTOLASKU: begin
                l2_ks <= l2_ks == 1'd1 ? 1'd0 : l2_ks + 1'b1;
                if (l2_ks == 1'd1) begin
                    if (l2_n != 3'd7) l2_n <= l2_n + 1'b1;
                    else begin
                        tila <= S_LOHKO3;
                    end
                end
            end
            S_LOHKO3: begin
                tila <= S_DONE;
            end
            S_DONE: tila <= S_IDLE;
            default: tila <= S_IDLE;
            endcase
        end
    end
// @loppu ohjaus
// @alku paivitykset
    always @(posedge clk) begin
        if (l1_j0) m_s <= 32'sd0;
        if (l2_j1) m_s <= t6;
        if (l3_j0) ap_return <= t8;
    end
// @loppu paivitykset
endmodule
