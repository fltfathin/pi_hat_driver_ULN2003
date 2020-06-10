#! /usr/bin/env python

from skidl import generate_netlist, Net, Part, ERC
from lib.connector import single_conn, double_conn, t_block

GND  = Net("GND")
V33  = Net("3V3")
V5   = Net("5V")
VREL = Net("VREL")

print("making power rails")

conn_power = t_block("power", ["5V","GND","VREL"])
V5 += conn_power["5V"]
VREL += conn_power["VREL"]
GND += conn_power["GND"]


print("making orangepi connector")

conn_opi:Part = double_conn("bpi_conn",[
    "3V3",      "5V",
    "PA12",     "5V",
    "PA11",     "GND",
    "PA06",     "UART1_TX",
    "GND",      "UART1_RX",
    "UART2_RX", "PA07",
    "UART2_TX", "GND",
    "UART2_CTS","TWI1_SDA",
    "3V3",      "TWI1_SCK",
    "SPI1_MOSI","GND", 
    "SPI1_MISO","UART2_RTS",
    "SPI1_CLK", "SPI1_CS",
    "GND",      "PA21"
])

GND += conn_opi["GND"]
V33 += conn_opi["3V3"]
V5  += conn_opi["5V"]

print("making relay driver")

driver = Part("Transistor_Array.lib", 
    "ULN2003A", footprint="Package_DIP:DIP-16_W7.62mm_Socket_LongPads")
GND += driver["GND"]
GND += driver["COM"]

print("making lcd connector")

display = single_conn("disp", ["SDA","SCL","VCC","GND"])
GND += display["GND"]
V33 += display["VCC"]
display["SCL"] += conn_opi["TWI1_SCK"]
display["SDA"] += conn_opi["TWI1_SDA"]

tp = []

for i in range(2):
    cnn = single_conn("3V3",["3V3"])
    V33 += cnn["3V3"]

relay_conns = []
for i in range(7):
    relay = single_conn(f"Rel{i+1}",["DRV","VCC"])
    driver[f"O{i+1}"] += relay["DRV"]
    VREL += relay["VCC"]
    relay_conns.append(relay)


# connect the unconnected nets to 

unused = 0
_pins = []
for i in range(26):
    pin = conn_opi[i+1]
    if not pin.is_connected():
        unused += 1
        _pins.append(pin.name)
        # print(pin)
        # NC += pin
print(f"{unused=}")

rest = single_conn("rest", _pins)
for i in _pins:
    conn_opi[i] += rest[i]

patch = single_conn("patch",[f"I{n+1}" for n in range(7)])
for i in range(7):
    driver[f"I{i+1}"] += patch[f"I{i+1}"]
    if i > 0:
        jumper = Part("Device.lib","Jumper_NO_Small",footprint="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
        driver[f"I{i}"] += jumper[1]
        driver[f"I{i+1}"] += jumper[2]

        jumper2 = Part("Device.lib","Jumper_NO_Small",footprint="Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
        driver[f"O{i}"] += jumper2[1]
        driver[f"O{i+1}"] += jumper2[2]

fan = single_conn("fan", ["5V","GND"])
V5 += fan["5V"]
GND += fan["GND"]

ERC()
a = generate_netlist()