module generated_ports (
    output pu_trim_0,
    output weakpu_trim_0,
    output weakpd_trim_0,
    output pu_trim_1,
    output weakpu_trim_1,
    output weakpd_trim_1,
    input [2:0] trim_din,
    output [4:0] ckouta_dr_en,
    input ckout_ocv_monitor,
    output ana_en,
    output pu_trim_2,
    output weakpu_trim_2,
    output weakpd_trim_2,
    input [3:0] lvcmos_en_din
);


assign weakpu_trim_0 = 1'b0;
assign weakpd_trim_0 = 1'b0;
assign pu_trim_0 = 1'b0;

assign weakpu_trim_1 = 1'b0;
assign weakpd_trim_1 = 1'b0;
assign pu_trim_1 = 1'b0;

assign weakpu_trim_2 = 1'b0;
assign weakpd_trim_2 = 1'b0;
assign pu_trim_2 = 1'b0;

always @(*)
a=trim_din;



endmodule