from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

class ModbusClient:
    def __init__(self, host='localhost', port=502):
        self.host = host
        self.port = port
        self.client = None
    
    def connect(self):
        """Establish connection to the Modbus server."""
        try:
            self.client = ModbusTcpClient(self.host, port=self.port)
            if not self.client.connect():
                raise ConnectionError("Unable to connect to Modbus server.")
            print("Connected to Modbus server.")
        except ModbusException as e:
            print(f"Modbus error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def read_holding_registers(self, address, count=1):
        """Read holding registers from the Modbus server."""
        if self.client is None:
            raise ConnectionError("Not connected to Modbus server.")
        try:
            response = self.client.read_holding_registers(address, count)
            if response.isError():
                raise ModbusException(f"Error reading holding registers: {response}")
            return response.registers
        except ModbusException as e:
            print(f"Modbus error: {e}")
            return None

    def write_register(self, address, value):
        """Write a single register to the Modbus server."""
        if self.client is None:
            raise ConnectionError("Not connected to Modbus server.")
        try:
            response = self.client.write_register(address, value)
            if response.isError():
                raise ModbusException(f"Error writing register: {response}")
            return response
        except ModbusException as e:
            print(f"Modbus error: {e}")
            return None

    def close(self):
        """Close the connection to the Modbus server."""
        if self.client is not None:
            self.client.close()
            self.client = None
            print("Disconnected from Modbus server.")



if __name__ == "__main__":
    client = ModbusClient(host='127.0.0.1', port=502)
    client.connect()
    
    # Read holding registers
    registers = client.read_holding_registers(address=0, count=10)
    print(f"Registers: {registers}")
    
    # Write to a register
    response = client.write_register(address=1, value=123)
    print(f"Write Response: {response}")

    client.close()