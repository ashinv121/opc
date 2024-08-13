from opcua import ua, Server
import time

class OPCUAServer:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4840", server_name="OPCUA Server"):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.server.set_server_name(server_name)
        self.namespace_uri = "http://examples.freeopcua.github.io"
        self.idx = self.server.register_namespace(self.namespace_uri)
        self.objects_node = self.server.get_objects_node()
        self.variables = {}

    def add_object(self, object_name):
        self.my_object = self.objects_node.add_object(self.idx, object_name)

    def add_variable(self, var_name, initial_value):
        var = self.my_object.add_variable(self.idx, var_name, initial_value)
        var.set_writable()  # Allow clients to write to this variable
        self.variables[var_name] = var  # Store variable for easy access
        return var

    def write_value(self, var_name, value):
        if var_name in self.variables:
            self.variables[var_name].set_value(value)
            print(f"Value of {var_name} written as {value}")
        else:
            print(f"Variable {var_name} not found.")

    def read_value(self, var_name):
        if var_name in self.variables:
            value = self.variables[var_name].get_value()
            print(f"Value of {var_name} is {value}")
            return value
        else:
            print(f"Variable {var_name} not found.")
            return None

    def start(self):
        self.server.start()
        print(f"OPC UA Server started at {self.server.endpoint.geturl()}")

    def stop(self):
        self.server.stop()
        print("OPC UA Server stopped")



