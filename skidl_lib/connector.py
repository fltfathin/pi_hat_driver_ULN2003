from skidl import Part
import math


def name_pins(conn, connlist):
    print(f"connector {conn.value}")
    for i, name in enumerate(connlist, start=1):
        conn[i].name = name
        print(f"  pin {i:02} = {name}")
    return conn


def pinheader(conn_name, connlist, rows=1):
    size = math.ceil(len(connlist) / rows)
    if rows > 2 or rows < 1:
        raise ValueError("unsupported row count")
    elif rows == 2:
        variant = "_Odd_Even"
    else:
        variant = ""
    conn = Part(
        "Connector_Generic.lib",
        f"Conn_0{rows}x{size:02}{variant}",
        value=conn_name,
        footprint=f"Connector_PinHeader_2.54mm:PinHeader_{rows}x{size:02}_P2.54mm_Vertical",
    )
    conn = name_pins(conn, connlist)
    return conn


def terminal(conn_name, connlist):
    size = len(connlist)
    conn = Part(
        "Connector_Generic.lib",
        f"Conn_01x{len(connlist):02}",
        value=conn_name,
        footprint=f"TerminalBlock_Altech_AK300-{size}_P5.00mm",
    )

    conn = name_pins(conn, connlist)
    return conn
