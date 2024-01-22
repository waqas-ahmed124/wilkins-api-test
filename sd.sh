#!/bin/bash

# Replace these variables with your actual values
SSH_KEY_PATH="BeyondGen.pem"
SSH_USERNAME="azureuser"
VM_IP="172.203.185.112"

# SSH command to connect to the VM
ssh -i "$SSH_KEY_PATH" "$SSH_USERNAME@$VM_IP"
echo "Script ran successfully!"
