import numpy as np
import serial
import serial.tools.list_ports

class Robot:
    def __init__(self):
        # Opentrons max dimensions
        self.xlim = (0, 375)
        self.ylim = (0, 250)
        self.zlim = (-150, 100)

        # Position in Opentrons coordinates
        self.pos = np.array([0,0,0])

        # Serial connection to gerbl Arduino
        self.serial = serial.Serial()
        self.simulate = False
    
    def __del__(self):
        # Close serial connection on object deletion if open
        if self.serial.is_open:
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
        
        return pos
    
    def _send_cmd(self, cmd):
        # If simulating, print the sent command
        if self.simulate:
            print(cmd)
        # If live connection, send command over serial
        else:
            self.serial.write(str.encode(cmd + '\n'))

    def connect(self, port=None):
        # Get available composite ports
        ports = serial.tools.list_ports.comports()

        # Check if real connection
        if port != 'Simulate':
            # If no port is specified, choose first port connected to Arduino
            if port == None:
                for i in range(len(ports)):
                    port_info = str(ports[i]).split()
                    if port_info[2] == "Arduino":
                        port = port_info[0]
            
            # Open connection to arduino running gerbl 
            self.serial.baudrate = 115200 # baud rate used by gerbl
            self.serial.port = port
            self.serial.open()
        else:
            self.simulate = True

    def move_head(self, **pos):
        # Get coordinate axes to move
        axes = pos.keys()

        # Constrain target position to machine limits
        pos = self._update_position(pos)

        # GCode move command
        gcode = 'G0'

        # If x coordinate is specified append it to the GCode command
        if 'x' in axes:
            cnc_x = pos['x'] # CNC x-axis is equal to Opentrons coordinate
            gcode += f' X{cnc_x}'
        # If y coordinate is specified append it to the GCode command
        if 'y' in axes:
            cnc_y = self.ylim[1] - pos['y'] # CNC y-axis moves negative in Opentrons coordinates
            gcode += f' Y{cnc_y}'
        # If z coordinate is specified append it to the GCode command
        if 'z' in axes:
            cnc_z = self.zlim[1] - pos['z'] # CNC z-axis moves negative in Opentrons coordinates
            gcode += f' Z{cnc_z}'

        # Send GCode command
        self._send_cmd(gcode)

    def home(self, axes='xyz'):
        # Home all axes
        self._send_cmd('$H')

if __name__ == '__main__':
    robot = Robot()
    robot.connect('Simulate')
    robot.move_head(x=100,y=200, z=-50)
        


