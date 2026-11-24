// Tuottanut minihls: diffeq
module diffeq (
    input  wire               clk,
    input  wire               rst,
    input  wire               ap_start,
    output wire               ap_done,
    output wire               ap_idle,
    output wire               ap_ready,
    input  wire signed [31:0] x0,
    input  wire signed [31:0] y0,
    input  wire signed [31:0] u0,
    input  wire signed [31:0] dx,
    output reg  signed [31:0] ap_return
);
    // Tilakone
    localparam S_IDLE = 3'd0;
    localparam S_LOHKO1 = 3'd1;
    localparam S_ASKEL = 3'd2;
    localparam S_LOHKO3 = 3'd3;
    localparam S_DONE = 3'd4;
    reg [2:0] tila;
    reg [1:0] l2_n;
    reg [2:0] l2_ks;
    wire l1_j0 = tila == S_LOHKO1;
    wire l2_j0 = tila == S_ASKEL && l2_ks == 3'd0;
    wire l2_j1 = tila == S_ASKEL && l2_ks == 3'd1;
    wire l2_j2 = tila == S_ASKEL && l2_ks == 3'd2;
    wire l2_j3 = tila == S_ASKEL && l2_ks == 3'd3;
    wire l2_j4 = tila == S_ASKEL && l2_ks == 3'd4;
    wire l2_j5 = tila == S_ASKEL && l2_ks == 3'd5;
    wire l3_j0 = tila == S_LOHKO3;
    assign ap_done = tila == S_DONE;
    assign ap_idle = tila == S_IDLE;
    assign ap_ready = tila == S_DONE;
    // Muuttujat ja vaiherekisterit
    reg signed [31:0] m_u;
    reg signed [31:0] m_x;
    reg signed [31:0] m_y;
    reg signed [31:0] t5_v0;
    reg signed [31:0] t6_v0;
    reg signed [31:0] t7_v0;
    reg signed [31:0] t9_v0;
    reg signed [31:0] t10_v0;
    reg signed [31:0] t11_v0;
    // Datapolku
    // lohko1: II 1, vaiheita 1
    // askel: II 6, vaiheita 1
    wire signed [31:0] t3 = m_x;
    wire signed [31:0] t4 = t3 + dx;
    wire signed [31:0] t5 = m_u;
    wire signed [31:0] t6 = mul0_y;
    wire signed [31:0] t7 = mul0_y;
    wire signed [31:0] t8 = mul0_y;
    wire signed [31:0] t9 = t5_v0 - t8;
    wire signed [31:0] t10 = m_y;
    wire signed [31:0] t11 = mul0_y;
    wire signed [31:0] t12 = mul0_y;
    wire signed [31:0] t13 = t9_v0 - t12;
    wire signed [31:0] t14 = mul0_y;
    wire signed [31:0] t15 = t10_v0 + t14;
    // lohko3: II 1, vaiheita 1
    wire signed [31:0] t19 = m_y;
// @alku kertoja
    // kertoja 0: 6 operaatiota
    wire signed [31:0] mul0_a = (l2_j0) ? t3 : (l2_j1) ? t6_v0 :
                                (l2_j2) ? t7_v0 : (l2_j3) ? t10 :
                                (l2_j4) ? t11_v0 : (l2_j5) ? t5_v0 : 32'sd0;
    wire signed [31:0] mul0_b = (l2_j0) ? 32'sd3 : (l2_j1) ? t5 :
                                (l2_j2) ? dx : (l2_j3) ? 32'sd3 :
                                (l2_j4) ? dx : (l2_j5) ? dx : 32'sd0;
    wire signed [31:0] mul0_y = mul0_a * mul0_b;
// @loppu kertoja
    // Portit
    always @(posedge clk) begin
        if (rst) begin
            tila <= S_IDLE;
        end else begin
            case (tila)
            S_IDLE: if (ap_start) begin
                tila <= S_LOHKO1;
            end
            S_LOHKO1: begin
                tila <= S_ASKEL;
                l2_n <= 0;
                l2_ks <= 0;
            end
            S_ASKEL: begin
                l2_ks <= l2_ks == 3'd5 ? 3'd0 : l2_ks + 1'b1;
                if (l2_ks == 3'd5) begin
                    if (l2_n != 2'd3) l2_n <= l2_n + 1'b1;
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
    always @(posedge clk) begin
        if (l1_j0) m_u <= u0;
        if (l1_j0) m_x <= x0;
        if (l1_j0) m_y <= y0;
        if (l2_j4) m_u <= t13;
        if (l2_j0) m_x <= t4;
        if (l2_j5) m_y <= t15;
        if (l2_j1) t5_v0 <= t5;
        if (l2_j0) t6_v0 <= t6;
        if (l2_j1) t7_v0 <= t7;
        if (l2_j2) t9_v0 <= t9;
        if (l2_j3) t10_v0 <= t10;
        if (l2_j3) t11_v0 <= t11;
        if (l3_j0) ap_return <= t19;
    end
endmodule
