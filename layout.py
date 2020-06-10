from skidl import *
from skidl_lib.connector import pinheader, terminal

GND  = Net("GND")
V33  = Net("3V3")
V5   = Net("5V")
VREL = Net("VREL")

term = terminal("supply", ["VREL", "GND", "5V"])

for i,j in zip([VREL, GND, V5],["VREL", "GND", "5V"]):
    i += term[j]

pi_conn = pinheader("pi_conn", [
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
],
rows=2)

for i,j in zip([V33, GND, V5],["3V3", "GND", "5V"]):
    i += pi_conn[j]

display = pinheader("disp", ["SDA","SCL","VCC","GND"])
for i,j in zip([pi_conn["TWI1_SDA"],pi_conn["TWI1_SCK"],V33, GND],["SDA","SCL","VCC","GND"]):
    i += display[j]

driver = Part("Transistor_Array.lib", 
    "ULN2003A", footprint="Package_DIP:DIP-16_W7.62mm_Socket_LongPads")
GND += driver["GND"]
GND += driver["COM"]

drvin = pinheader("drvin", [f"DIN{n+1}" for n in range(7)])

drvout = pinheader("drvout", [f"DOUT{n+1}" for n in range(7)])

for i in range(7):
    drvin[f"DIN{i+1}"] += driver[f"I{i+1}"]
    drvout[f"DOUT{i+1}"] += driver[f"O{i+1}"]

unused = []

for i in range(26):
    if not (pin := pi_conn[i+1]).is_connected():
        unused += pin

extra_pin = pinheader("extra_pins", list([x.name for x in unused]))

for num, pin in enumerate(unused, start=1):
    pin += extra_pin[num]


print("\n\nERC check \n")

term = []

for i in range(9):
    
    if i % 3 == 0:
        t = terminal("", [f"P{x}" for x in range(3)])
        term.append(t)
    p = (i%3)+1 
    if i < 7:
        term[-1][p] += drvout[f"DOUT{i+1}"]
    else:
        term[-1][p] += VREL
ERC()
generate_netlist()
