<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

#### SPI Peripheral
- Configuration:
    - COPI (control out-peripheral in): data transmission line
    - nCS: chip select, active low
    - sCLK: serial clock

16 Channels, each one has an out bit and a pwm mode bit.

#### PWM Peripheral 
- Configuration:
    - Duty Cycle:
        - 8 Bits (0-255)
        - Proportion that is high during period

When pwm mode is high and out is high for a channel, the duty cycle sends pulses.

## How to test

**Yeah tests make sure it works.**

Tests defined in 
```test/test.py```

- Checks for appropriate transmission over SPI
- Frequency of spi is 3 kHz as expected
    - Testing 0%, 50%, 100% duty cycles
- Duty cycle of pwm is as expected
    - Testing 0%, 50%, 100% duty cycles

## External hardware

Lots of hardware
Yeah lots of it, good thing there's lots on this planet
