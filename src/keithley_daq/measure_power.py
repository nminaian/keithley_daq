"""Measure power."""

from collections import defaultdict
from contextlib import contextmanager
from time import sleep

import pandas as pd
import pygame
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
        sleep(18)

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
    NUM_CHANNELS = 3
    SIGNAL_NAMES = ["ratio", "vsense", "time"]
    SIGNALS_PER_CHANNEL = len(SIGNAL_NAMES)
    NUM_SIGNALS = NUM_CHANNELS * SIGNALS_PER_CHANNEL
    equal_length_data = list(
        zip(*[buffer[i::NUM_SIGNALS] for i in range(NUM_SIGNALS)], strict=False)
    )
    raw_data = defaultdict(list)
    for (
        ratio1,
        vsense1,
        time1,
        ratio2,
        vsense2,
        time2,
        ratio3,
        vsense3,
        time3,
    ) in equal_length_data:
        for name, signal in {
            "ratio1": ratio1,
            "vsense1": vsense1,
            "time1": time1,
            "ratio2": ratio2,
            "vsense2": vsense2,
            "time2": time2,
            "ratio3": ratio3,
            "vsense3": vsense3,
            "time3": time3,
        }.items():
            raw_data[name].append(signal)
    data = pd.DataFrame(raw_data).assign(**{
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
    data.to_csv("Data.csv")
    # alternate: **{"Current ": lambda df: df.vsense / SHUNT} or voltage=lambda df: df.ratio * df.vsense,


def main():
    # Initialize Pygame
    pygame.init()

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Set up the screen
    SCREEN_WIDTH = SCREEN_HEIGHT = 475

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PVC Gel Matrix")

    # Set up the squares
    square_size = 100
    square_padding = 100
    square1_pos = (square_padding, square_padding)
    square2_pos = (SCREEN_WIDTH - square_padding - square_size, square_padding)
    square3_pos = (square_padding, SCREEN_HEIGHT - square_padding - square_size)
    square4_pos = (
        SCREEN_WIDTH - square_padding - square_size,
        SCREEN_HEIGHT - square_padding - square_size,
    )

    # square1_color = WHITE
    # square2_color = WHITE
    # square3_color = WHITE
    # square4_color = WHITE

    # Set up the clock
    clock = pygame.time.Clock()

    # Read the DataFrame and populate list of voltages for each junction before iterating through animation loop
    volt_data = pd.read_excel(
        io=r"C:\Users\asenn\OneDrive\School\Research\Miscellaneous\SPIE 2023\Data\Position Sensor\positionsensing(processed).xlsx",
        header=18,
        index_col=0,
        usecols=["Time", "CH111", "CH112", "CH113", "CH114"],
    )

    j1_voltages = list(volt_data["CH111"])
    j2_voltages = list(volt_data["CH112"])
    j3_voltages = list(volt_data["CH113"])
    j4_voltages = list(volt_data["CH114"])

    # Now zip lists together to form a list of tuples (psuedo-array)
    # Be mindful to convert zip object to list
    volt_data = list(
        zip(j1_voltages, j2_voltages, j3_voltages, j4_voltages, strict=False)
    )

    # Main animation loop
    # Iterates through a list of tuples stored in # volt_data
    for volt_tuple in volt_data:
        # Find intensity of junction based on voltage
        intensity_list = volt_to_intensity(volt_tuple)

        # Change square colors based on intensity value
        junction_colors = intensity_to_RGB(intensity_list)

        square1_color = junction_colors[0]
        square2_color = junction_colors[1]
        square3_color = junction_colors[2]
        square4_color = junction_colors[3]

        # Draw the squares
        screen.fill(WHITE)
        pygame.draw.rect(
            screen,
            square1_color,
            (square1_pos[0], square1_pos[1], square_size, square_size),
        )
        pygame.draw.rect(
            screen,
            square2_color,
            (square2_pos[0], square2_pos[1], square_size, square_size),
        )
        pygame.draw.rect(
            screen,
            square3_color,
            (square3_pos[0], square3_pos[1], square_size, square_size),
        )
        pygame.draw.rect(
            screen,
            square4_color,
            (square4_pos[0], square4_pos[1], square_size, square_size),
        )

        # Update the screen
        pygame.display.update()

        # .2177
        sleep(0.095)
        # Set the frame rate
        clock.tick(60)


# Need to define a function that varies the intensity of the color based on the read voltage
# Threshold is 12 mV minimum to 39 mV max


def volt_to_intensity(volt_tuple):
    """
    Takes volt_tuple (voltage for all junctions) and returns a tuple of color
    intensity values related to each junction
    """
    # Initialize return intensity list
    intensity_list = []

    # This loop is taking volt_tuple (Kiethley data) and iterating through each element
    # (v1, v2, v3, v4) to yield an appropriate intensity value
    for volt_tuple_element in volt_tuple:
        if volt_tuple_element > 12 and volt_tuple_element < 39:
            # 12mV is minimum reference voltage so this is the new "zero"
            volt_tuple_element -= 12
            # Lower intensity yields darker colors
            volt_tuple_element = 255 - volt_tuple_element * 9.4444

        else:
            volt_tuple_element = 220

        intensity_list.append(volt_tuple_element)

    return intensity_list


# Generate a list populated with RGB tuples for each junction at each time instant
# Given an intensity_list
# [( (R, G, B), (R, G, B), (R, G, B), (R, G, B) ), ...]
def intensity_to_RGB(intensity_list):
    # initialize return
    color_profile = []
    for intensity in intensity_list:
        color = (255, intensity, intensity)
        color_profile.append(color)
    return color_profile


main()
