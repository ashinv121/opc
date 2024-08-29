const addButton = document.getElementById('add-device-button');
addButton.addEventListener('click', function() {
    // Check if a device form already exists
    if (document.querySelector('.device-form')) {
        alert('A device form is already open. Please save or remove the current form before adding a new one.');
        return;
    }

    // Disable the add button
    addButton.disabled = true;

    const deviceForm = document.createElement('div');
    deviceForm.className = 'device-form';
    
    deviceForm.innerHTML = `
        <h3>Add Device</h3>
        <label for="device-name">Device Name:</label>
        <input type="text" name="device-name" required>
        <label for="protocol">Protocol:</label>
        <select name="protocol">
            <option value="modbus">Modbus</option>
            <option value="s7">S7</option>
        </select>
        <div class="modbus-config" style="display: none;">
            <label for="modbus-ip">Modbus IP:</label>
            <input type="text" name="modbus-ip" placeholder="192.168.0.1">
            <label for="modbus-port">Modbus Port:</label>
            <input type="number" name="modbus-port" value="502">
        </div>
        <div class="s7-config" style="display: none;">
            <label for="s7-ip">S7 IP:</label>
            <input type="text" name="s7-ip" placeholder="192.168.0.1">
            <label for="s7-rack">S7 Rack:</label>
            <input type="number" name="s7-rack" value="0">
            <label for="s7-slot">S7 Slot:</label>
            <input type="number" name="s7-slot" value="1">
        </div>
        <button class="remove-device-button">Remove</button>
        <button class="save-device-button">Save</button>
    `;
    
    // Add event listeners for protocol selection
    const protocolSelect = deviceForm.querySelector('select[name="protocol"]');
    protocolSelect.addEventListener('change', function() {
        const modbusConfig = deviceForm.querySelector('.modbus-config');
        const s7Config = deviceForm.querySelector('.s7-config');
        if (this.value === 'modbus') {
            modbusConfig.style.display = 'block';
            s7Config.style.display = 'none';
        } else {
            modbusConfig.style.display = 'none';
            s7Config.style.display = 'block';
        }
    });
    protocolSelect.dispatchEvent(new Event('change'));


    // Add event listener for the remove button
    const removeButton = deviceForm.querySelector('.remove-device-button');
    removeButton.addEventListener('click', function() {
        deviceForm.remove();
    });

    // Add event listener for the save button
    const saveButton = deviceForm.querySelector('.save-device-button');
    saveButton.addEventListener('click', function() {
        const formData = {
            device_name: deviceForm.querySelector('input[name="device-name"]').value,
            protocol: deviceForm.querySelector('select[name="protocol"]').value,
            config: {}
        };

        if (formData.protocol === 'modbus') {
            formData.config = {
                ip: deviceForm.querySelector('input[name="modbus-ip"]').value,
                port: deviceForm.querySelector('input[name="modbus-port"]').value
            };
        } else if (formData.protocol === 's7') {
            formData.config = {
                ip: deviceForm.querySelector('input[name="s7-ip"]').value,
                rack: deviceForm.querySelector('input[name="s7-rack"]').value,
                slot: deviceForm.querySelector('input[name="s7-slot"]').value
            };
        }

        fetch('/add_device', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Remove the form
                deviceForm.remove();
                addButton.disabled = false;
                window.location.reload();

            } else {
                alert('Error adding device: ' + data.message);
            }
        });
    });

    // Append the new device form to the container
    document.getElementById('device-container').appendChild(deviceForm);
});

// Function to add device data to the tree
function addDeviceToTree(device) {
    const modbusTree = document.getElementById('modbus-tree');
    const s7Tree = document.getElementById('s7-tree');

    const deviceNode = document.createElement('li');
    deviceNode.textContent = `${device.device_name} (${device.protocol})`;

    // Add tags input and list
    const tagInput = document.createElement('input');
    tagInput.setAttribute('placeholder', 'Add tag');
    const tagList = document.createElement('ul');

    // Add event listener to handle tag addition
    tagInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const tag = tagInput.value.trim();
            if (tag) {
                const tagItem = document.createElement('li');
                tagItem.textContent = tag;
                tagList.appendChild(tagItem);
                tagInput.value = ''; // Clear input field
            }
        }
    });

    deviceNode.appendChild(tagInput);
    deviceNode.appendChild(tagList);

    // Append the device node to the appropriate tree
    if (device.protocol === 'modbus') {
        modbusTree.appendChild(deviceNode);
    } else if (device.protocol === 's7') {
        s7Tree.appendChild(deviceNode);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('/list_devices')
        .then(response => response.json())
        .then(data => {
            data.forEach((device, index) => {
                addDeviceToTree(device);
            });
        });
});


document.addEventListener("DOMContentLoaded", () => {
    const toggleServerButton = document.getElementById("toggle-server-button");

    toggleServerButton.addEventListener("click", () => {
        const serverStatus = toggleServerButton.textContent.includes("Start") ? "start" : "stop";
        const actionUrl = `/opcua/${serverStatus}`;

        fetch(actionUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                toggleServerButton.textContent = serverStatus === "start" ? "Stop Server" : "Start Server";
                alert(data.message);
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    });
});
