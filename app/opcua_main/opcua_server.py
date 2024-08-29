from opcua import ua, Server
import logging

class OPCUAServer:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4840", server_name="OPCUA Server"):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.server.set_server_name(server_name)
        self.namespace_uri = "http://examples.freeopcua.github.io"
        self.idx = self.server.register_namespace(self.namespace_uri)
        self.objects_node = self.server.get_objects_node()
        self.variables = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def add_object(self, object_name):
        return self.objects_node.add_object(self.idx, object_name)

    def add_variable_to_object(self, obj, var_name, initial_value):
        var = obj.add_variable(self.idx, var_name, initial_value)
        var.set_writable()
        return var

    def write_value(self, var_name, value):
        if var_name in self.variables:
            self.variables[var_name].set_value(value)
            self.logger.info(f"Value of {var_name} written as {value}")
        else:
            self.logger.warning(f"Variable {var_name} not found.")

    def read_value(self, var_name):
        if var_name in self.variables:
            value = self.variables[var_name].get_value()
            self.logger.info(f"Value of {var_name} is {value}")
            return value
        else:
            self.logger.warning(f"Variable {var_name} not found.")
            return None

    def start(self):
        try:
            self.server.start()
            self.logger.info(f"OPC UA Server started at {self.server.endpoint.geturl()}")
        except Exception as e:
            self.logger.error(f"Error starting OPC UA Server: {e}")

    def stop(self):
        try:
            self.server.stop()
            self.logger.info("OPC UA Server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping OPC UA Server: {e}")

    def is_running(self):
        return self.server.is_running
