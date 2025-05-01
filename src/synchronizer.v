

`default_nettype none

module synchronizer (

    input wire clk,
    input wire rst_n,

    input wire copi,
    input wire n_cs,
    input wire sclk,

    output wire [6:0] address,
    output wire [7:0] data,
);

    reg[1:0] copi_sync, n_cs_sync, sclk_sync;

    always @(postedge clk) begin
        copi_sync <= {copi_sync[0], copi};
        n_cs_sync <= {n_cs_sync[0], n_cs};
        sclk_sync <= {sclk_sync[0], sclk};
    end

    reg [15:0] shift_reg;
    reg [3:0] num_bits;

    always @(postedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg <= 16'd0;
            address <= 7'd0;
            data <= 8'd0;
        end else begin
            if (!n_cs_sync[1]) begin
                if (sclk_sync == 2'b01 && num_bits < 16) begin
                    shift_reg <= {shift_reg[14:0], copi_sync[1]};
                    num_bits <= num_bits+1;
                end
            end

            if (n_cs_sync == 2'b01) begin
                if (num_bits == 16 && shift_reg[15] == 1'b1) begin
                    address <= shift_reg[14:8];
                    data <= shift_reg[7:0];
                end
                num_bits <= 0;
            end
        end
    end


endmodule