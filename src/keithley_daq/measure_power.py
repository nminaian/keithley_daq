"""Measure power."""

import time
from contextlib import contextmanager

import pandas as pd
import pyvisa
from pyvisa.resources import MessageBasedResource

# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()
resources = rm.list_resources()


@contextmanager
def get_instrument():  # noqa: D103
    try:
        inst: MessageBasedResource = pyvisa.ResourceManager().open_resource(  # type: ignore
            resources[0],  # "USB0::0x05E6::0x6510::04495786::INSTR"
            read_termination="\n",
            write_termination="\n",
        )
        inst.timeout = 2000
        # reset instrument
        inst.write("*RST")  # Reset the DAQ6510
        yield inst
    finally:
        inst.close()  # type: ignore


with get_instrument() as inst:
    print(f"System Version: {inst.query(':system:version?')}")
    try:
        # clears the buffer, creates the sensing buffer, and assigns all data to the buffer
        inst.write("TRAC:MAKE 'Power', 3000000, FULL")
        inst.write("TRACe:CLEar 'Power'")
        inst.write(":TRAC:FILL:MODE CONT, 'Power'")
        inst.write(":ROUT:SCAN:BUFF 'Power'")

        # define the scan list, set scan count to infinite, and a channel delay of 100 us
        inst.write(":ROUT:SCAN:CRE (@101:103)")  # Generate the scan...
        inst.write(":ROUT:SCAN:COUN:SCAN 0")

        # enable the graph and plot the data
        inst.write(":DISP:SCR HOME")
        inst.write(":DISP:WATC:CHAN (@101:103)")
        inst.write(":DISP:SCR GRAP")
        inst.write("ROUT:CHAN:LAB 'IPMC1', (@101)")  # Apply a label to channel 101
        inst.write("ROUT:CHAN:LAB 'IPMC2', (@102)")  # Apply a label to channel 102
        inst.write("ROUT:CHAN:LAB 'IPMC3', (@103)")  # Apply a label to channel 103
        inst.write(
            "SENS:FUNC 'VOLT:DC:RAT', (@101:103)"
        )  # Set channels 101-103 for DC Voltage Ratio

        # begin data collection for at least xx sec
        inst.write("INIT")
        time.sleep(18)

    except KeyboardInterrupt:
        print("Measurement stopped by user. \n")

    inst.write("ABORT")
    print("Reading Buffer \n")
    # Extract the data...

    buffersize = inst.query(':TRAC:ACTual:END? "Power"')
    print(buffersize)
    ass = inst.query(f'TRAC:DATA? 1, {buffersize}, "Power", READ, EXTR, REL').split(",")
    buffer = [float(val) for val in ass]

    # Data = pd.DataFrame({'Voltage':buffer[0::3], 'Time':buffer[2::3], 'Channel':buffer[1::3]}).to_csv('Butt.csv')
    SHUNT = 10.3
    Data = pd.DataFrame({
        "ratio1": buffer[::9],
        "vsense1": buffer[1::9],
        "time1": buffer[2::9],
        "ratio2": buffer[3::9],
        "vsense2": buffer[4::9],
        "time2": buffer[5::9],
        "ratio3": buffer[6::9],
        "vsense3": buffer[7::9],
        "time3": buffer[8::9],
    }).assign(**{
        "Current 1 [A]": lambda df: df.vsense1 / SHUNT,
        "Voltage 1 [V]": lambda df: df.ratio1 * df.vsense1,
        "Power 1 [W]": lambda df: df["Current 1 [A]"] * df["Voltage 1 [V]"],
        "Current 2 [A]": lambda df: df.vsense2 / SHUNT,
        "Voltage 2 [V]": lambda df: df.ratio2 * df.vsense2,
        "Power 2 [W]": lambda df: df["Current 2 [A]"] * df["Voltage 2 [V]"],
        "Current 3 [A]": lambda df: df.vsense3 / SHUNT,
        "Voltage 3 [V]": lambda df: df.ratio3 * df.vsense3,
        "Power 3 [W]": lambda df: df["Current 3 [A]"] * df["Voltage 3 [V]"],
    })

    Data.to_csv("Data.csv")
    # alternate: **{"Current ": lambda df: df.vsense / SHUNT} or voltage=lambda df: df.ratio * df.vsense,
