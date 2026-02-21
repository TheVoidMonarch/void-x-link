#!/usr/bin/env python3
"""
VoidLink Device ID Utility

This utility retrieves or generates the device ID used for account binding.
"""

import os
import sys
import json
import argparse

# Add parent directory to path to ensure modules can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import device_id module
try:
    from core.device_id import get_device_id, verify_device_id
except ImportError:
    print("Error: Could not import device_id module")
    sys.exit(1)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="VoidLink Device ID Utility")
    parser.add_argument("--regenerate", action="store_true", 
                        help="Regenerate the device ID even if it exists")
    parser.add_argument("--verify", type=str, metavar="DEVICE_ID",
                        help="Verify if the given device ID matches this device")
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format")
    
    args = parser.parse_args()
    
    if args.verify:
        # Verify device ID
        result = verify_device_id(args.verify)
        
        if args.json:
            print(json.dumps({"verified": result}))
        else:
            if result:
                print("Device ID verification: PASSED")
            else:
                print("Device ID verification: FAILED")
                print(f"Stored ID: {args.verify}")
                print(f"Current ID: {get_device_id()}")
        
        sys.exit(0 if result else 1)
    
    # Get or regenerate device ID
    device_id = get_device_id(regenerate=args.regenerate)
    
    if args.json:
        print(json.dumps({"device_id": device_id}))
    else:
        print(f"Device ID: {device_id}")
        print("\nThis ID uniquely identifies your device for VoidLink account registration.")
        print("Your account can be used on multiple devices.")
        print("However, your username and password cannot be changed after account creation.")

if __name__ == "__main__":
    main()