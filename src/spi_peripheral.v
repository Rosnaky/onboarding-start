

`default_nettype none

module spi_peripheral (
    input wire clk,
    input wire rst_n,

    input wire [6:0] address,
    input wire [7:0] data,
    input wire write_en,

    output reg [7:0] en_reg_out_7_0,
    output reg [7:0] en_reg_out_15_8,
    output reg [7:0] en_reg_pwm_7_0,
    output reg [7:0] en_reg_pwm_15_8,
    output reg [7:0] pwm_duty_cycle
);


    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            en_reg_out_7_0 <= 8'd0;
            en_reg_out_15_8 <= 8'd0;
            en_reg_pwm_7_0 <= 8'd0;
            en_reg_pwm_15_8 <= 8'd0;
            pwm_duty_cycle <= 8'd0;
        end else if (write_en) begin
            case (address)
                7'h00: en_reg_out_7_0 <= data;
                7'h01: en_reg_out_15_8 <= data;
                7'h02: en_reg_pwm_7_0 <= data;
                7'h03: en_reg_pwm_15_8 <= data;
                7'h04: pwm_duty_cycle <= data;
                default:;
            endcase
        end
    end

    
endmodule