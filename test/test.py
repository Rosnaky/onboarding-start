# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
import cocotb.clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from cocotb.types import LogicArray
import cocotb.utils

async def await_half_sclk(dut):
    """Wait for the SCLK signal to go high or low."""
    start_time = cocotb.utils.get_sim_time(units="ns")
    while True:
        await ClockCycles(dut.clk, 1)
        # Wait for half of the SCLK period (10 us)
        if (start_time + 100*100*0.5) < cocotb.utils.get_sim_time(units="ns"):
            break
    return

def ui_in_logicarray(ncs, bit, sclk):
    """Setup the ui_in value as a LogicArray."""
    return LogicArray(f"00000{ncs}{bit}{sclk}")

async def send_spi_transaction(dut, r_w, address, data):
    """
    Send an SPI transaction with format:
    - 1 bit for Read/Write
    - 7 bits for address
    - 8 bits for data
    
    Parameters:
    - r_w: boolean, True for write, False for read
    - address: int, 7-bit address (0-127)
    - data: LogicArray or int, 8-bit data
    """
    # Convert data to int if it's a LogicArray
    if isinstance(data, LogicArray):
        data_int = int(data)
    else:
        data_int = data
    # Validate inputs
    if address < 0 or address > 127:
        raise ValueError("Address must be 7-bit (0-127)")
    if data_int < 0 or data_int > 255:
        raise ValueError("Data must be 8-bit (0-255)")
    # Combine RW and address into first byte
    first_byte = (int(r_w) << 7) | address
    # Start transaction - pull CS low
    sclk = 0
    ncs = 0
    bit = 0
    # Set initial state with CS low
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    await ClockCycles(dut.clk, 1)
    # Send first byte (RW + Address)
    for i in range(8):
        bit = (first_byte >> (7-i)) & 0x1
        # SCLK low, set COPI
        sclk = 0
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
        # SCLK high, keep COPI
        sclk = 1
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
    # Send second byte (Data)
    for i in range(8):
        bit = (data_int >> (7-i)) & 0x1
        # SCLK low, set COPI
        sclk = 0
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
        # SCLK high, keep COPI
        sclk = 1
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
    # End transaction - return CS high
    sclk = 0
    ncs = 1
    bit = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    await ClockCycles(dut.clk, 600)
    return ui_in_logicarray(ncs, bit, sclk)

async def get_period_ns(dut, timeout=0.5*1000000):
    
    start = cocotb.utils.get_sim_time(units="ns")
    # get low
    dut._log.info("Await stabilize low")
    while (dut.uo_out.value.integer & 1 == 1):
        if (cocotb.utils.get_sim_time(units="ns") - start > timeout):
            return -2
        
        await ClockCycles(dut.clk, 5)
    
    start = cocotb.utils.get_sim_time(units="ns")
    # get high
    dut._log.info("Await first rising edge")
    while (dut.uo_out.value.integer & 1 == 0):
        if (cocotb.utils.get_sim_time(units="ns") - start > timeout):
            return -1

        await ClockCycles(dut.clk, 5)

    t1 = cocotb.utils.get_sim_time(units="ns")
    
    start = cocotb.utils.get_sim_time(units="ns")
    
    # get low
    dut._log.info("Await stabilize low")
    dut._log.info(t1)
    while (dut.uo_out.value.integer & 1 == 1):
        if (cocotb.utils.get_sim_time(units="ns") - start > timeout):
            return -2
        await ClockCycles(dut.clk, 5)
    
    start = cocotb.utils.get_sim_time(units="ns")
    # get high
    dut._log.info("Await second rising edge")
    while (dut.uo_out.value.integer & 1 == 0):
        if (cocotb.utils.get_sim_time(units="ns") - start > timeout):
            return -1
        await ClockCycles(dut.clk, 5)

    t2 = cocotb.utils.get_sim_time(units="ns")
    
    return t2-t1

async def get_duty_cycle(dut, timeout=0.5*1000000):
    start = cocotb.utils.get_sim_time(units="ns")
    # get low
    dut._log.info("Await stabilize low")
    while (dut.uo_out.value.integer & 1 == 1):
        if (cocotb.utils.get_sim_time(units="ns") - start > timeout):
            return -2
        
        await ClockCycles(dut.clk, 5)
    
    start = cocotb.utils.get_sim_time(units="ns")
    # get high
    dut._log.info("Await first rising edge")
    while (dut.uo_out.value.integer & 1 == 0):
        if (cocotb.utils.get_sim_time(units="ns") - start > timeout):
            return -1

        await ClockCycles(dut.clk, 5)

    t1 = cocotb.utils.get_sim_time(units="ns")
    start = cocotb.utils.get_sim_time(units="ns")
    
    # get low
    dut._log.info("Await stabilize low")
    dut._log.info(t1)
    while (dut.uo_out.value.integer & 1 == 1):
        if (cocotb.utils.get_sim_time(units="ns") - start > timeout):
            return -2
        await ClockCycles(dut.clk, 5)
    
    t3 = cocotb.utils.get_sim_time(units="ns")
    start = cocotb.utils.get_sim_time(units="ns")
    # get high
    dut._log.info("Await second rising edge")
    while (dut.uo_out.value.integer & 1 == 0):
        if (cocotb.utils.get_sim_time(units="ns") - start > timeout):
            return -1
        await ClockCycles(dut.clk, 5)

    t2 = cocotb.utils.get_sim_time(units="ns")
    
    return ((t3-t1)/(t2-t1))*100


@cocotb.test()
async def test_spi(dut):
    dut._log.info("Start SPI test")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    ncs = 1
    bit = 0
    sclk = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Test project behavior")
    dut._log.info("Write transaction, address 0x00, data 0xF0")
    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xF0)  # Write transaction
    assert dut.uo_out.value == 0xF0, f"Expected 0xF0, got {dut.uo_out.value}"
    await ClockCycles(dut.clk, 1000) 

    dut._log.info("Write transaction, address 0x01, data 0xCC")
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xCC)  # Write transaction
    assert dut.uio_out.value == 0xCC, f"Expected 0xCC, got {dut.uio_out.value}"
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x30 (invalid), data 0xAA")
    ui_in_val = await send_spi_transaction(dut, 1, 0x30, 0xAA)
    await ClockCycles(dut.clk, 100)

    dut._log.info("Read transaction (invalid), address 0x00, data 0xBE")
    ui_in_val = await send_spi_transaction(dut, 0, 0x30, 0xBE)
    assert dut.uo_out.value == 0xF0, f"Expected 0xF0, got {dut.uo_out.value}"
    await ClockCycles(dut.clk, 100)
    
    dut._log.info("Read transaction (invalid), address 0x41 (invalid), data 0xEF")
    ui_in_val = await send_spi_transaction(dut, 0, 0x41, 0xEF)
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x02, data 0xFF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xFF)  # Write transaction
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x04, data 0xCF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xCF)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0xFF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xFF)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0x00")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x00)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0x01")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x01)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("SPI test completed successfully")

@cocotb.test()
async def test_pwm_freq(dut):
    dut._log.info("Start PWM frequency tests")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    ncs = 1
    bit = 0
    sclk = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Test project behavior")
    dut._log.info("Write transaction, address 0x02, data 0xF0")
    await send_spi_transaction(dut, 1, 0x00, 0x01)
    await send_spi_transaction(dut, 1, 0x02, 0x01)
    await send_spi_transaction(dut, 1, 0x04, 0x80)
    await ClockCycles(dut.clk, 1000)

    period_ns = await get_period_ns(dut)
    freq_hz = (1000000000/period_ns)

    assert 2970 <= freq_hz and freq_hz <= 3030, f"Frequency invalid, got {freq_hz}"

    # max duty cycle
    await send_spi_transaction(dut, 1, 0x04, 0xFF)
    await ClockCycles(dut.clk, 1000)

    period_ns = await get_period_ns(dut)

    assert period_ns == -2, f"Frequency invalid, got {freq_hz}"

    # min duty cycle
    await send_spi_transaction(dut, 1, 0x04, 0x00)
    await ClockCycles(dut.clk, 1000)

    period_ns = await get_period_ns(dut)

    assert period_ns == -1, f"Frequency invalid, got {freq_hz}"

    dut._log.info("PWM Frequency test completed successfully")


@cocotb.test()
async def test_pwm_duty(dut):

    dut._log.info("Start PWM duty (haha) tests")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    ncs = 1
    bit = 0
    sclk = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Test project behavior")
    dut._log.info("Write transaction, address 0x02, data 0xF0")
    await send_spi_transaction(dut, 1, 0x00, 0x01)
    await send_spi_transaction(dut, 1, 0x02, 0x01)
    await send_spi_transaction(dut, 1, 0x04, 0x7F)
    await ClockCycles(dut.clk, 1000)

    duty_cycle = await get_duty_cycle(dut)

    assert 49 <= duty_cycle and duty_cycle <= 51, f"Duty (haha) cycle invalid, got {duty_cycle}"

    # max duty cycle
    await send_spi_transaction(dut, 1, 0x04, 0xFF)
    await ClockCycles(dut.clk, 1000)

    period_ns = await get_period_ns(dut)

    assert period_ns == -2, f"Duty (haha) cycle invalid, got {duty_cycle}"

    # min duty cycle
    await send_spi_transaction(dut, 1, 0x04, 0x00)
    await ClockCycles(dut.clk, 1000)

    period_ns = await get_period_ns(dut)

    assert period_ns == -1, f"Duty (haha) cycle invalid, got {duty_cycle}"

    dut._log.info("PWM Duty Cycle test completed successfully")
