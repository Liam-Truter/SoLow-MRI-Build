import serial.tools.list_ports

from motor import Motor



class Controller:
    def __init__(self):
        self.position=[0,0,0]
        self.target_position=[0,0,0]
        self.motors={'x': Motor(0,0),
                     'y': Motor(1,1),
                     'z': Motor(2,2)}
        
        ports = serial.tools.list_ports.comports()
        self.serial_connection = serial.Serial()

        for x in range(len(ports)):
            port_info = str(ports[x]).split()
            if port_info[2] == "Arduino":
                port = port_info[0]

        self.serial_connection.baudrate = 9600
        self.serial_connection.port = port
        self.serial_connection.open()

    def update(self):
        lines = self.serial_connection.readlines()
        for i in range(len(lines)):
            line = lines[-i]
            if line.startswith('POS: '):
                resistances = line.split(' ')[1:]
                break
        for m in self.motors.items():
            idx = m.pot
            r = resistances[idx]
            self.position[idx] = m.get_position(r)