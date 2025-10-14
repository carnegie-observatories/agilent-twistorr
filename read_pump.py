import socket

stx = b"\x02"
address = {"rs232": b"\x80"}
window = {
    "START/STOP": b"\x30\x30\x30",  # WIN 0
    "LOW SPEED ACTIVATION": b"\x30\x30\x31",  # WIN 1
    "SERIAL/REMOTE/FRONT/FIELDBUS CONFIGURATION": b"\x30\x30\x38",  # WIN 8
    "ENABLE/DISABLE SOFT START": b"\x31\x30\x30",  # WIN 100
    "R1 SET POINT TYPE": b"\x31\x30\x31",  # WIN 101
    "R1 SET POINT VALUE": b"\x31\x30\x32",  # WIN 102
    "R1 SET POINT DELAY": b"\x31\x30\x33",  # WIN 103
    "R1 SET POINT SIGNAL ACTIVATION TYPE": b"\x31\x30\x34",  # WIN 104
    "R1 SET POINT HYSTERESIS": b"\x31\x30\x35",  # WIN 105
    "ACTIVE STOP": b"\x31\x30\x37",  # WIN 107
    "SERIAL COMM. BAUD RATE": b"\x31\x30\x38",  # WIN 108
    "PUMP LIFE/CYCLE TIME/CYCLE NUMBER RESET": b"\x31\x30\x39",  # WIN 109
    "INTERLOCK TYPE": b"\x31\x31\x30",  # WIN 110
    "ANALOG OUTPUT TYPE": b"\x31\x31\x31",  # WIN 111
    "LOW SPEED FREQUENCY VALUE": b"\x31\x31\x37",  # WIN 117
    "ROTATIONAL FREQUENCY SETTING": b"\x31\x32\x30",  # WIN 120
    "SET VENT VALVE": b"\x31\x32\x32",  # WIN 122
    "SET THE VENT VALVE OPERATION": b"\x31\x32\x35",  # WIN 125
    "VENT VALVE OPENING DELAY": b"\x31\x32\x36",  # WIN 126
    "GAUGE SET POINT TYPE": b"\x31\x33\x36",  # WIN 136
    "GAUGE SET POINT VALUE": b"\x31\x33\x37",  # WIN 137
    "GAUGE SET POINT DELAY": b"\x31\x33\x38",  # WIN 138
    "GAUGE SET POINT SIGNAL ACTIVATION TYPE": b"\x31\x33\x39",  # WIN 139
    "GAUGE SET POINT HYSTERESIS": b"\x31\x34\x30",  # WIN 140
    "EXTERNAL FAN CONFIGURATION": b"\x31\x34\x33",  # WIN 143
    "EXTERNAL FAN ACTIVATION": b"\x31\x34\x34",  # WIN 144
    "VENT VALVE OPENING TIME": b"\x31\x34\x37",  # WIN 147
    "ACTUAL MAXIMUM POWER LIMIT": b"\x31\x35\x35",  # WIN 155
    "GAS LOAD TYPE": b"\x31\x35\x37",  # WIN 157
    "R1 SET POINT PRESSURE THRESHOLD": b"\x31\x36\x32",  # WIN 162
    "UNIT OF MEASURE FOR PRESSURE": b"\x31\x36\x33",  # WIN 163
    "STOP SPEED READING": b"\x31\x36\x37",  # WIN 167
    "R2 SET POINT TYPE": b"\x31\x37\x31",  # WIN 171
    "R2 SET POINT VALUE": b"\x31\x37\x32",  # WIN 172
    "R2 SET POINT DELAY": b"\x31\x37\x33",  # WIN 173
    "R2 SET POINT SIGNAL ACTIVATION TYPE": b"\x31\x37\x34",  # WIN 174
    "R2 SET POINT HYSTERESIS": b"\x31\x37\x35",  # WIN 175
    "R2 SET POINT PRESSURE THRESHOLD": b"\x31\x37\x36",  # WIN 176
    "START OUTPUT CONFIGURATION": b"\x31\x37\x37",  # WIN 177
    "GAUGE GAS TYPE": b"\x31\x38\x31",  # WIN 181
    "CORRECTION FACTOR FOR CUSTOM GAUGE": b"\x31\x38\x32",  # WIN 182
    "PUMP CURRENT": b"\x32\x30\x30",  # WIN 200
    "PUMP VOLTAGE": b"\x32\x30\x31",  # WIN 201
    "PUMP POWER": b"\x32\x30\x32",  # WIN 202
    "DRIVING FREQUENCY": b"\x32\x30\x33",  # WIN 203
    "PUMP TEMPERATURE": b"\x32\x30\x34",  # WIN 204
    "PUMP STATUS": b"\x32\x30\x35",  # WIN 205
    "ERROR CODE": b"\x32\x30\x36",  # WIN 206
    "CONTROLLER HEATSINK TEMPERATURE": b"\x32\x31\x31",  # WIN 211
    "CONTROLLER COOLING AIR TEMPERATURE": b"\x32\x31\x36",  # WIN 216
    "PRESSURE READING": b"\x32\x32\x34",  # WIN 224
    "ROTATION FREQUENCY": b"\x32\x32\x36",  # WIN 226
    "GAUGE STATUS": b"\x32\x35\x37",  # WIN 257
    "GAUGE POWER MODE": b"\x32\x36\x37",  # WIN 267
    "CYCLE TIME IN MINUTES": b"\x33\x30\x30",  # WIN 300
    "CYCLE NUMBER": b"\x33\x30\x31",  # WIN 301
    "PUMP LIFE IN HOURS": b"\x33\x30\x32",  # WIN 302
    "RS485 ADDRESS": b"\x35\x30\x33",  # WIN 503
    "SERIAL TYPE SELECTION": b"\x35\x30\x34",  # WIN 504
    "RUN UP TIME": b"\x37\x32\x34",  # WIN 724
    "RUN UP TIME CONTROL": b"\x37\x32\x35",  # WIN 725
}

window_rev = {v: k for k, v in window.items()}


command = {"read": b"\x30", "write": b"\x31"}
etx = b"\x03"  # end of transmission


class TwisTorr:

    def open(self, ip, port=8899):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))

    def calculate_crc(self, message):
        """Calculate CRC for Edwards pump protocol message.

        Args:
            message: Bytes starting after STX, including ETX
        Returns:
            Two character hex string representing CRC
        """
        crc = 0
        for byte in message:
            crc ^= byte
        return f"{crc:02X}".encode()


    def encode_message(self, address, window, command, data=""):
        """Create complete message with CRC.

        Args:
            address: Address byte (0x80 for RS232)
            window: Three digit window number as string
            command: Command byte (0x30 read, 0x31 write)
            data: Optional data string for write commands
        Returns:
            Complete message bytes including STX, message, ETX and CRC
        """
        message = address + window + command
        if data:
            message += data
        message += etx
        crc = self.calculate_crc(message)
        message = stx + message + crc
        return message


    def decode_message(self, message):
        """Decode message from TwisTorr pump protocol.

        Args:
            message: Complete message bytes including STX, message, ETX and CRC
        Returns:
            Decoded components: address, window, command, data, crc
        """
        if message[0] != stx[0] or message[-3] != etx[0]:
            raise ValueError("Invalid message format")
        
        address = message[1:2]
        window = message[2:5]
        command = message[5:6]
        data = message[6:-3]
        crc = message[-2:]

        calculated_crc = self.calculate_crc(message[1:-2])
        if crc != calculated_crc:
            raise ValueError("CRC mismatch")
        
        return address, window, command, data, crc

    def get_window_description(self, window):
        return window_rev.get(window, "Unknown window")

    def read(self, cmd):
        """Send command to pump and read response.
        Args:
            cmd: Command bytes to send
        Returns:            Decoded response message
        """
        aux = self.encode_message(address["rs232"], window[cmd], command["read"])
        self.sock.sendall(aux)
        response = self.sock.recv(1024)
        if not response:
            print("No response received from pump.")
        return self.decode_message(response)

    def test_message_encoding(self):
        # print(get_message(address["rs232"], window["PUMP STATUS"], command["read"]))
        print(self.encode_message(address["rs232"], window["CONTROLLER COOLING AIR TEMPERATURE"], command["read"]))
        print(self.encode_message(address["rs232"], window["SERIAL TYPE SELECTION"], command["read"]))

        print(self.decode_message(self.encode_message(address["rs232"], window["SERIAL TYPE SELECTION"], command["read"])), address["rs232"], window["SERIAL TYPE SELECTION"], command["read"])

        dec = self.decode_message(self.encode_message(address["rs232"], window["SERIAL TYPE SELECTION"], command["read"]))
        print(self.get_window_description(dec[1]), dec[1], dec[2], dec[3], dec[4])

        # ###

        print(self.encode_message(b"\x83", window["PUMP STATUS"], command["read"]), "02 83 32 30 35 30 03 38 37")
        print(self.encode_message(b"\x80", window["START/STOP"], command["write"], data=b"\x31"), "02 80 30 30 30 31 31 03 42 33")
        # sys.exit(0)


        # response = b"\x02\x802050000000\x0384" # pump status response - decode it...
        # test = b"\x02\x80\x32\x31\x36\x30\x03\x38\x37"  # controller cooling air temperature oC
        test = b"\x02\x80\x35\x30\x34\x30\x03\x38\x31"  # read serial type


        # chksum = 0
        # for x in ["\x80", "\x32", "\x31", "\x36", "\x30", "\x03"]:
        #     chksum ^= ord(x)
        # print(hex(chksum))

        # "\x80" ^ "\x32" ^ "\x31" ^ "\x36" ^ "\x30" ^ "\x03"

        # import socket




    def test_socket_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.connect(("10.7.45.147", 10001))
        # sock.connect(("localhost", 10001))
        sock.connect(("localhost", 8899)) # wifi
        # sock.sendall(encode_message(address["rs232"], window["CONTROLLER COOLING AIR TEMPERATURE"], command["read"]))
        print("test 1")
        sock.sendall(self.encode_message(address["rs232"], window["CYCLE NUMBER"], command["read"]))
        # sock.sendall(encode_message(address["rs232"], window["R1 SET_POINT_TYPE"], command["write"], data=b"\x32")) # 0x32 = time
        print("test 2")
        print(self.read(sock))
        print("test 3")
        sock.sendall(self.encode_message(address["rs232"], window["R1 SET_POINT_SIGNAL_ACTIVATION_TYPE"], command["write"], data=b"\x31"))
        print(self.read(sock))
        sock.close()


        # from serial import Serial

        # s = Serial("COM4", 9600, timeout=1)


        # def create_message(addr, window, command, data=""):
        #     """Create complete message with CRC.

        #     Args:
        #         addr: Address byte (0x80 for RS232)
        #         window: Three digit window number as string
        #         command: Command byte (0x30 read, 0x31 write)
        #         data: Optional data string for write commands
        #     Returns:
        #         Complete message bytes including STX, message, ETX and CRC
        #     """
        #     msg = bytes([addr]) + bytes([window]) + bytes([command])
        #     if data:
        #         msg += data.encode()
        #     msg += b"\x03"
        #     crc = calculate_crc(msg)
        #     return b"\x02" + msg + crc.encode()
