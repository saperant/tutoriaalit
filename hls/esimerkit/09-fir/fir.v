// Tuottanut minihls: fir
// @alku portit
module fir (
    input  wire               clk,
    input  wire               rst,
    input  wire               ap_start,
    output wire               ap_done,
    output wire               ap_idle,
    output wire               ap_ready,
    input  wire signed [31:0] x_TDATA,
    input  wire               x_TVALID,
    output wire               x_TREADY,
    output wire signed [31:0] y_TDATA,
    output wire               y_TVALID,
    input  wire               y_TREADY
);
// @loppu portit
    // Tilakone
    localparam S_IDLE = 2'd0;
    localparam S_LOHKO1 = 2'd1;
    localparam S_NAYTTEET = 2'd2;
    localparam S_DONE = 2'd3;
    reg [1:0] tila;
    reg [4:0] l2_n;
    reg [2:0] l2_v;
    wire l2_uusi = l2_v[0] && l2_n != 5'd31;
    wire [2:0] l2_vs = {l2_v[1:0], l2_uusi};
    wire l1_j0 = tila == S_LOHKO1;
    wire l2_j0 = tila == S_NAYTTEET && l2_v[0];
    wire l2_j1 = tila == S_NAYTTEET && l2_v[1];
    wire l2_j2 = tila == S_NAYTTEET && l2_v[2];
    assign ap_done = tila == S_DONE;
    assign ap_idle = tila == S_IDLE;
    assign ap_ready = tila == S_DONE;
// @alku virrat
    // Virrat: koko piiri pysähtyy, jos tarvittu
    // virta ei ole valmis
    wire x_tarve = l2_j0;
    wire x_ok = !x_tarve || x_TVALID;
    wire y_tarve = l2_j2;
    wire y_ok = !y_tarve || y_TREADY;
    wire en = x_ok && y_ok;
// @loppu virrat
    // Muuttujat ja vaiherekisterit
    reg signed [31:0] m_z_0;
    reg signed [31:0] m_z_1;
    reg signed [31:0] m_z_2;
    reg signed [31:0] m_z_3;
    reg signed [31:0] m_z_4;
    reg signed [31:0] m_z_5;
    reg signed [31:0] m_z_6;
    reg signed [31:0] m_z_7;
    reg signed [31:0] t18_v1;
    reg signed [31:0] t19_v1;
    reg signed [31:0] t21_v1;
    reg signed [31:0] t23_v1;
    reg signed [31:0] t25_v1;
    reg signed [31:0] t27_v1;
    reg signed [31:0] t28_v2;
    reg signed [31:0] t29_v1;
    reg signed [31:0] t29_v2;
    // Datapolku
    // lohko1: II 1, vaiheita 1
    // naytteet: II 1, vaiheita 3
    wire signed [31:0] t8 = m_z_6;
    wire signed [31:0] t9 = m_z_5;
    wire signed [31:0] t10 = m_z_4;
    wire signed [31:0] t11 = m_z_3;
    wire signed [31:0] t12 = m_z_2;
    wire signed [31:0] t13 = m_z_1;
    wire signed [31:0] t14 = m_z_0;
    wire signed [31:0] t15 = x_TDATA;
    wire signed [31:0] t16 = t15 * -32'sd3;
    wire signed [31:0] t17 = t14 * 32'sd12;
    wire signed [31:0] t18 = t16 + t17;
    wire signed [31:0] t19 = t13 * 32'sd37;
    wire signed [31:0] t20 = t18_v1 + t19_v1;
    wire signed [31:0] t21 = t12 * 32'sd82;
    wire signed [31:0] t22 = t20 + t21_v1;
    wire signed [31:0] t23 = t11 * 32'sd82;
    wire signed [31:0] t24 = t22 + t23_v1;
    wire signed [31:0] t25 = t10 * 32'sd37;
    wire signed [31:0] t26 = t24 + t25_v1;
    wire signed [31:0] t27 = t9 * 32'sd12;
    wire signed [31:0] t28 = t26 + t27_v1;
    wire signed [31:0] t29 = t8 * -32'sd3;
    wire signed [31:0] t30 = t28_v2 + t29_v2;
    wire signed [31:0] t31 = t30 >>> 32'sd8;
// @alku kytkennat
    // Portit
    assign x_TREADY = x_tarve && en;
    assign y_TDATA = t31;
    assign y_TVALID = y_tarve && x_ok;
// @loppu kytkennat
    always @(posedge clk) begin
        if (rst) begin
            tila <= S_IDLE;
        end else if (en) begin
            case (tila)
            S_IDLE: if (ap_start) begin
                tila <= S_LOHKO1;
            end
            S_LOHKO1: begin
                tila <= S_NAYTTEET;
                l2_n <= 0;
                l2_v <= 1;
            end
            S_NAYTTEET: begin
                l2_v <= l2_vs;
                if (l2_uusi) l2_n <= l2_n + 1'b1;
                if (l2_vs == 0) begin
                    tila <= S_DONE;
                end
            end
            S_DONE: tila <= S_IDLE;
            default: tila <= S_IDLE;
            endcase
        end
    end
    always @(posedge clk) if (en) begin
        if (l1_j0) m_z_0 <= 32'sd0;
        if (l1_j0) m_z_1 <= 32'sd0;
        if (l1_j0) m_z_2 <= 32'sd0;
        if (l1_j0) m_z_3 <= 32'sd0;
        if (l1_j0) m_z_4 <= 32'sd0;
        if (l1_j0) m_z_5 <= 32'sd0;
        if (l1_j0) m_z_6 <= 32'sd0;
        if (l1_j0) m_z_7 <= 32'sd0;
        if (l2_j0) m_z_0 <= t15;
        if (l2_j0) m_z_1 <= t14;
        if (l2_j0) m_z_2 <= t13;
        if (l2_j0) m_z_3 <= t12;
        if (l2_j0) m_z_4 <= t11;
        if (l2_j0) m_z_5 <= t10;
        if (l2_j0) m_z_6 <= t9;
        if (l2_j0) t18_v1 <= t18;
        if (l2_j0) t19_v1 <= t19;
        if (l2_j0) t21_v1 <= t21;
        if (l2_j0) t23_v1 <= t23;
        if (l2_j0) t25_v1 <= t25;
        if (l2_j0) t27_v1 <= t27;
        if (l2_j1) t28_v2 <= t28;
        if (l2_j0) t29_v1 <= t29;
        if (tila == S_NAYTTEET) t29_v2 <= t29_v1;
    end
endmodule
