import threading
import time
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from app.modbus.client import ModbusClient
from .opcua_main.opcua_server import OPCUAServer

app_routes = Blueprint('app_routes', __name__)
opcua_server = OPCUAServer()

# Temporary storage for devices
devices = []
server_running = False
update_thread = None

def update_tag_values():
    while server_running:
        for device in devices:
            if device['protocol'] == 'modbus' and 'tags' in device:
                device['client'].connect()
                for tag in device['tags']:
                    value = device['client'].read_holding_registers(address=0, count=1)
                    opcua_server.write_value(tag['name'], value)
                device['client'].close()
        time.sleep(5)

@app_routes.route('/')
def index():
    return render_template('index.html', devices=devices)

@app_routes.route('/add_device', methods=['POST'])
def add_device():
    data = request.json
    device_name = data.get('device_name')
    protocol = data.get('protocol')
    config = data.get('config')

    for device in devices:
        if device['name'] == device_name:
            return jsonify({'status': 'error', 'message': 'Device name already exists'}), 400
    
    # Validate and create the appropriate client based on protocol
    if protocol == 'modbus':
        client = ModbusClient(config['ip'], config['port'])
        opcua_server.add_object(device_name)
        devices.append({'name': device_name, 'protocol': protocol, 'ip': config['ip'], 'port': config['port'],'client': client})
    else:
        return jsonify({"status": "error", "message": "Invalid protocol"}), 400
    
    return jsonify({"status": "success"})

@app_routes.route('/list_devices', methods=['GET'])
def list_devices():
    # Return a list of devices in JSON format
    device_list = [{'name': device['name'], 'protocol': device['protocol']} for device in devices]
    return jsonify(device_list)

@app_routes.route('/add_device/<device_name>/add_tag', methods=['POST'])
def add_tag(device_name):
    data = request.json
    tag_name = data.get('tag_name')
    tag_value = data.get('tag_value')

    device = next((device for device in devices if device['name'] == device_name), None)

    if not device:
        return jsonify({'status': 'error', 'message': f'Device {device_name} not found'}), 404
    
    if 'tags' not in device:
        device['tags'] = []
    
    # Check for duplicate tags
    for tag in device['tags']:
        if tag['name'] == tag_name:
            return jsonify({'status': 'error', 'message': f'Tag {tag_name} already exists for this device'}), 400
    
    # Add the new tag
    device['tags'].append({'name': tag_name, 'value': tag_value})
    
    # Add tag to OPC UA server
    opcua_server.add_variable(tag_name, tag_value)

    return jsonify({'status': 'success', 'message': f'Tag {tag_name} added to device {device_name}'}), 200

@app_routes.route('/opcua/start', methods=['POST'])
def start_opcua_server():
    global server_running, update_thread
    if not server_running:
        opcua_server.start()
        server_running = True

        # Start a thread to update Modbus tag values in the OPC UA server
        update_thread = threading.Thread(target=update_tag_values)
        update_thread.daemon = True
        update_thread.start()

        return jsonify({'status': 'success', 'message': 'OPC UA Server started and Modbus tags updating'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'OPC UA Server is already running'}), 400

@app_routes.route('/opcua/stop', methods=['POST'])
def stop_opcua_server():
    global server_running
    if server_running:
        server_running = False
        opcua_server.stop()
        return jsonify({'status': 'success', 'message': 'OPC UA Server stopped'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'OPC UA Server is not running'}), 400

@app_routes.route('/opcua/get_tag_value/<tag_name>', methods=['GET'])
def get_tag_value(tag_name):
    # Get the value of a specific tag from the OPC UA server
    if not server_running:
        return jsonify({'status': 'error', 'message': 'OPC UA Server is not running'}), 400

    try:
        tag_value = opcua_server.read_value(tag_name)
        return jsonify({'status': 'success', 'tag_name': tag_name, 'value': tag_value}), 200
    except KeyError:
        return jsonify({'status': 'error', 'message': f'Tag {tag_name} not found'}), 404

@app_routes.route('/opcua/write_tag_value/<tag_name>', methods=['PUT'])
def put_tag_value(tag_name):
    global server_running
    if not server_running:
        return jsonify({'status': 'error', 'message': 'OPC UA Server is not running'}), 400

    new_value = request.json.get('value')  # Assuming the value is sent in the JSON body
    if new_value is None:
        return jsonify({'status': 'error', 'message': 'No value provided'}), 400

    # Find the device that has the tag
    for device in devices:
        if 'tags' in device:
            tag = next((t for t in device['tags'] if t['name'] == tag_name), None)
            if tag:
                try:
                    # Update the Modbus register with the new value
                    if device['protocol'] == 'modbus':
                        client = device['client']
                        client.connect()
                        # Assuming you write the new value to the first holding register (address 0)
                        client.write_register(address=0, value=new_value)
                        client.close()

                    # Write the new value to the OPC UA server
                    opcua_server.write_value(tag_name, new_value)

                    # Update the tag value in the device's tag list
                    tag['value'] = new_value

                    return jsonify({'status': 'success', 'tag_name': tag_name, 'new_value': new_value}), 200

                except KeyError:
                    return jsonify({'status': 'error', 'message': f'Tag {tag_name} not found'}), 404

    return jsonify({'status': 'error', 'message': f'Tag {tag_name} not found in any device'}), 404

@app_routes.route('/device/<device_name>/edit_tags', methods=['GET', 'POST'])
def edit_tags(device_name):
    device = next((device for device in devices if device['name'] == device_name), None)

    if not device:
        return jsonify({'status': 'error', 'message': f'Device {device_name} not found'}), 404

    if request.method == 'POST':
        new_tag_name = request.form.get('new_tag_name')
        new_tag_value = request.form.get('new_tag_value')
        
        # Check for duplicate tags or add new ones
        for tag in device.get('tags', []):
            if tag['name'] == new_tag_name:
                tag['value'] = new_tag_value
                break
        else:
            if new_tag_name:
                device.setdefault('tags', []).append({'name': new_tag_name, 'value': new_tag_value})
        
        return redirect(url_for('app_routes.edit_tags', device_name=device_name))

    return render_template('edit_tags.html', device=device)