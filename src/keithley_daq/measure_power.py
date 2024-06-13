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
        inst.write("*RST")
        yield inst
    finally:
        inst.close()  # type: ignore


with get_instrument() as inst:
    print(f"System version: {inst.query(':system:version?')}")
    try:
        # clears the buffer, creates the sensing buffer, and assigns all data to the buffer
        inst.write("TRAC:MAKE 'Sensing', 3000000, FULL")
        inst.write("TRACe:CLEar 'Sensing'")
        inst.write(":TRAC:FILL:MODE CONT, 'Sensing'")
        inst.write(":ROUT:SCAN:BUFF 'Sensing'")

        # define the scan list, set scan count to infinite, and a channel delay of 100 us
        inst.write(":ROUTe:SCAN:CRE (@101)")
        inst.write(":ROUT:SCAN:COUN:SCAN 0")

        # enable the graph and plot the data
        inst.write(":DISP:SCR HOME")
        inst.write(":DISP:WATC:CHAN (@101)")
        inst.write(":DISP:SCR GRAP")
        inst.write("FUNC 'VOLT:DC:RAT', (@101)")

        # begin data collection for at least 10 sec
        inst.write("INIT")
        time.sleep(10)

    except KeyboardInterrupt:
        print("Measurement stopped by user. \n")

    inst.write("ABORT")
    print("Reading Buffer \n")
    # Extract the data...

    buffersize = inst.query(':TRAC:ACTual:END? "Sensing"')
    print(buffersize)
    ass = inst.query(f'TRAC:DATA? 1, {buffersize}, "Sensing", READ, EXTR').split(",")
    buffer = [float(val) for val in ass]
    # Data = pd.DataFrame({'Voltage':buffer[0::3], 'Time':buffer[2::3], 'Channel':buffer[1::3]}).to_csv('Butt.csv')
    SHUNT = 0.91
    Data = pd.DataFrame({"ratio": buffer[0::3], "vsense": buffer[1::3]}).assign(**{
        "Current [mA]": lambda df: df.vsense / SHUNT,
        "Voltage [mV]": lambda df: df.ratio * df.vsense,
        "Power [mW]": lambda df: df.current * df.voltage,
    })

    # alternate: **{"Current ": lambda df: df.vsense / SHUNT} or voltage=lambda df: df.ratio * df.vsense,
