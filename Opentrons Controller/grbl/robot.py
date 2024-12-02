import numpy as np
import serial
import serial.tools.list_ports
import threading
import time

class Driver:
    def __init__(self):
        self.pos = np.array([0, 0, 0])

    def get_head_position(self):
        position = {'current': {}}
        axes = ['x', 'y', 'z']

        for i in range(3):
            ax = axes[i]
            position['current'][ax] = self.pos[i]

        return position


class Robot:
    def __init__(self):
        # Opentrons max dimensions
        self.xlim = (0, 375)
        self.ylim = (0, 250)
        self.zlim = (-150, 100)

        # gerbl CNC max dimensions
        self.cnc_xlim = (-377, 0)
        self.cnc_ylim = (-252, 0)
        self.cnc_zlim = (-252, 0)

        # Position in Opentrons coordinates
        self.pos = np.array([0, 250, 100])

        # Serial connection to gerbl Arduino
        self.serial = serial.Serial()
        self.simulate = False

        # Thread for reading serial messages
        self.read_thread = None
        self.keep_reading = False

        # For compatibility with Opentrons code
        self._driver = Driver()
        self._driver.pos = self.pos

        # Wait until command finished
        self.ok = False

    def __del__(self):
        # Close serial connection and stop reading thread on object deletion
        if self.serial.is_open:
            self.keep_reading = False
            if self.read_thread is not None:
                self.read_thread.join()
            self.serial.close()

    def _update_position(self, pos):
        axes = pos.keys()
        # Constrain x to limits
        if 'x' in axes:
            pos['x'] = min(self.xlim[1], max(self.xlim[0], pos['x']))
            self.pos[0] = pos['x']

        # Constrain y to limits
        if 'y' in axes:
            pos['y'] = min(self.ylim[1], max(self.ylim[0], pos['y']))
            self.pos[1] = pos['y']
        # Constrain z to limits
        if 'z' in axes:
            pos['z'] = min(self.zlim[1], max(self.zlim[0], pos['z']))
            self.pos[2] = pos['z']

        self._driver.pos = self.pos

        return pos

    def _send_cmd(self, cmd, wait_for_ok=True):
        if wait_for_ok:
            self.ok = False
        # If simulating, print the sent command
        if self.simulate:
            print(cmd)
        # If live connection, send command over serial
        else:
            self.serial.write(str.encode(cmd + '\n'))
            print('Sent: ' + cmd)
            while not self.ok and wait_for_ok:
                pass

    def connect(self, port=None):
        # Get available composite ports
        ports = serial.tools.list_ports.comports()

        # Check if real connection
        if not port in ['Simulate', 'Virtual Smoothie']:
            # If no port is specified, choose first port connected to Arduino
            if port is None:
                for i in range(len(ports)):
                    port_info = str(ports[i]).split()
                    if port_info[2] == "Arduino":
                        port = port_info[0]

            # Open connection to Arduino running gerbl
            self.serial.baudrate = 115200  # baud rate used by gerbl
            self.serial.port = port
            self.serial.open()

            # Start reading serial messages
            self.keep_reading = True
            self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.read_thread.start()

            time.sleep(2)
        else:
            self.simulate = True

    def read_serial(self):
        """Continuously read and print serial messages."""
        while self.keep_reading:
            if self.serial.is_open and self.serial.in_waiting > 0:
                try:
                    message = self.serial.readline().decode('utf-8').strip()
                    print(f"Received: {message}")
                    if message == 'ok':
                        self.ok = True
                except Exception as e:
                    print(f"Error reading from serial: {e}")

    def move_head(self, **pos):
        # Get coordinate axes to move
        axes = pos.keys()

        # Constrain target position to machine limits
        pos = self._update_position(pos)

        # GCode move command
        gcode = 'G0'

        # If x coordinate is specified append it to the GCode command
        if 'x' in axes:
            cnc_x = self.cnc_xlim[0] + 2 + pos['x']  # CNC x-axis is equal to Opentrons coordinate
            gcode += f' X{cnc_x}'
        # If y coordinate is specified append it to the GCode command
        if 'y' in axes:
            cnc_y = pos['y'] - self.ylim[1] - 2  # CNC y-axis moves negative in Opentrons coordinates
            gcode += f' Y{cnc_y}'
        # If z coordinate is specified append it to the GCode command
        if 'z' in axes:
            cnc_z = pos['z'] - self.zlim[1] - 2  # CNC z-axis moves negative in Opentrons coordinates
            gcode += f' Z{cnc_z}'

        # Wait for move to finish
        gcode += "G4P0"

        # Send GCode command
        self._send_cmd(gcode)

    def home(self, axes='xyz'):
        # Home all axes
        self._send_cmd('$H')


robot = Robot()

if __name__ == '__main__':
    robot.connect('Simulate')
    robot.move_head(x=100, y=200, z=-50)
