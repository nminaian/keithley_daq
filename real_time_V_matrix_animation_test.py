from collections import defaultdict
from contextlib import contextmanager
from time import sleep

import pandas as pd
import pyvisa
from pyvisa.resources import MessageBasedResource

# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()
resources = rm.list_resources()


@contextmanager
def get_instrument():
    try:
        if not resources:
            raise RuntimeError("No VISA instruments detected.")

        inst: MessageBasedResource = rm.open_resource(
            resources[0],  # Assuming you want to access the first available resource
            read_termination="\n",
            write_termination="\n",
        )
        inst.timeout = 2000
        inst.write("*RST")  # Reset the DAQ6510
        yield inst

    finally:
        if "inst" in locals():  # Ensure inst is defined before closing
            inst.close()


def main():
    try:
        with get_instrument() as inst:
            print(f"System Version: {inst.query(':system:version?')}")
            try:
                # Clears the buffer, creates the sensing buffer, and assigns all data to the buffer
                inst.write("TRAC:MAKE 'Voltage', 3000000, 'DEF'")
                inst.write("TRAC:CLE 'Voltage'")
                inst.write("TRAC:FILL:MODE CONT, 'Voltage'")
                inst.write("ROUT:SCAN:BUFF 'Voltage'")

                # Define the scan list, set scan count to 5, and a channel delay of 60 seconds
                inst.write("ROUT:SCAN:CRE (@110,120)")
                inst.write("ROUT:SCAN:COUN 5")
                inst.write("ROUT:SCAN:INT 60")

                # Enable the graph and plot the data
                inst.write("DISP:SCR HOME")
                inst.write("DISP:WATC:CHAN (@110,120)")
                inst.write("DISP:SCR GRAP")
                inst.write("ROUT:CHAN:LAB 'PVC_Gel_1', (@110)")
                inst.write("ROUT:CHAN:LAB 'PVC_Gel_2', (@120)")

                inst.write("SENS:FUNC 'VOLT:DC', (@110,120)")

                # Begin data collection
                inst.write("INIT")
                sleep(18)  # This is the run time

            except KeyboardInterrupt:
                print("Measurement stopped by user.")

            inst.write("ABORT")
            print("Reading Buffer")
            # Extract the data
            buffersize = inst.query(':TRAC:ACTual:END? "Voltage"')
            print(f"Buffer size: {buffersize}")
            data = inst.query(
                f'TRAC:DATA? 1, {buffersize}, "Voltage", READ, REL'
            ).split(",")

            buffer = [float(val) for val in data]

            # Organize the data for processing
            NUM_CHANNELS = 2
            SIGNAL_NAMES = ["ratio", "vsense", "time"]
            SIGNALS_PER_CHANNEL = len(SIGNAL_NAMES)
            NUM_SIGNALS = NUM_CHANNELS * SIGNALS_PER_CHANNEL
            equal_length_data = list(
                zip(*[buffer[i::NUM_SIGNALS] for i in range(NUM_SIGNALS)], strict=False)
            )
            raw_data = defaultdict(list)
            for ratio1, vsense1, time1, ratio2, vsense2, time2 in equal_length_data:
                for name, signal in {
                    "ratio1": ratio1,
                    "vsense1": vsense1,
                    "time1": time1,
                    "ratio2": ratio2,
                    "vsense2": vsense2,
                    "time2": time2,
                }.items():
                    raw_data[name].append(signal)
            data = pd.DataFrame(raw_data).assign(**{
                "Voltage 1 [V]": lambda df: df.ratio1 * df.vsense1,
                "Voltage 2 [V]": lambda df: df.ratio2 * df.vsense2,
            })
            data.to_csv("Data.csv")

    except RuntimeError as e:
        print(f"Error: {e}")
        return
    except pyvisa.errors.VisaIOError as e:
        print(f"VISA Error: {e}")
        return


if __name__ == "__main__":
    main()
