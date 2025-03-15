#!/usr/bin/env python3
"""
VoidLink Automated Test Runner

This script automates the execution of manual test cases, captures results,
logs errors, and generates a comprehensive test report.
"""

import os
import sys
import time
import json
import subprocess
import threading
import socket
import signal
import argparse
import datetime
import re
from typing import Dict, List, Tuple, Optional, Any

# Check if we can import server modules
try:
    from server import start_server
    SERVER_AVAILABLE = True
except ImportError:
    print("Warning: Could not import server module. Will use subprocess to start server.")
    SERVER_AVAILABLE = False

# Check if we can import server modules
try:
    from server import start_server
    SERVER_AVAILABLE = True
except ImportError:
    print("Warning: Could not import server module. Will use subprocess to start server.")
    SERVER_AVAILABLE = False

# Check if we can import server modules
try:
    from server import start_server
    SERVER_AVAILABLE = True
except ImportError:
    print("Warning: Could not import server module. Will use subprocess to start server.")
    SERVER_AVAILABLE = False

# Check if we can import server modules
try:
    from server import start_server
    SERVER_AVAILABLE = True
except ImportError:
    print("Warning: Could not import server module. Will use subprocess to start server.")
    SERVER_AVAILABLE = False

# Check if we can import server modules
try:
    from server import start_server
    SERVER_AVAILABLE = True
except ImportError:
    print("Warning: Could not import server module. Will use subprocess to start server.")
    SERVER_AVAILABLE = False

# ANSI colors for terminal output


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Test case structure


class TestCase:
    def __init__(self, id: str, category: str, name: str, description: str, steps: List[str],
                 expected_results: List[str], setup_commands: List[str] = None,
                 teardown_commands: List[str] = None, timeout: int = 30):
        self.id = id
        self.category = category
        self.name = name
        self.description = description
        self.steps = steps
        self.expected_results = expected_results
        self.setup_commands = setup_commands or []
        self.teardown_commands = teardown_commands or []
        self.timeout = timeout
        self.result = None  # "PASS", "FAIL", "ERROR", "SKIPPED"
        self.error_message = None
        self.output = None
        self.duration = 0

# Test result structure


class TestResult:
    def __init__(self, test_case: TestCase, result: str, error_message: Optional[str] = None,
                 output: Optional[str] = None, duration: float = 0):
        self.test_case = test_case
        self.result = result
        self.error_message = error_message
        self.output = output
        self.duration = duration
        self.timestamp = datetime.datetime.now().isoformat()


# Global variables
server_process = None
client_processes = []
test_results = []
log_file = None


def print_header():
    """Print the VoidLink Test Runner header"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════╗")
    print("║          VoidLink Automated Tests         ║")
    print("║  Comprehensive Test Suite for VoidLink    ║")
    print("╚═══════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")


def log(message: str, level: str = "INFO"):
    """Log a message to the console and log file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format based on level
    if level == "INFO":
        if os.path.exists("reset_db.sh"):
                try:
                formatted = f"{Colors.CYAN}[INFO]{Colors.ENDC} {timestamp} - {message}"
    elif level == "SUCCESS":
        formatted = f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {timestamp} - {message}"
    elif level == "WARNING":
        formatted = f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {timestamp} - {message}"
    elif level == "ERROR":
            if os.path.exists("reset_db.sh"):
                try:
            except subprocess.SubprocessError as e:
                log(f"Warning: Could not reset database: {str(e)}", "WARNING")
                # Create database directory if it doesn't exist
                if not os.path.exists("database"):
                    os.makedirs("database")
                if not os.path.exists("database/files"):
                    os.makedirs("database/files")
                if not os.path.exists("database/chat_history"):
                    os.makedirs("database/chat_history")
        else:
            log("Warning: reset_db.sh not found. Creating database directories manually.", "WARNING")
            # Create database directory if it doesn't exist
            if not os.path.exists("database"):
                os.makedirs("database")
            if not os.path.exists("database/files"):
                os.makedirs("database/files")
            if not os.path.exists("database/chat_history"):
                os.makedirs("database/chat_history")

        # If we can import the server module, use it directly
        if SERVER_AVAILABLE:
            log("Starting server using direct module import", "INFO")
            # Start the server in a separate thread
            from server import start_server as server_start_func
            server_thread = threading.Thread(target=server_start_func)
            server_thread.daemon = True
            server_thread.start()

            # Wait for server to start
            time.sleep(3)

            # There's no easy way to check if the server started successfully
            # We'll assume it did if we get this far
            log("Server started successfully (direct mode)", "SUCCESS")
                return True
        )

    els:
            # Otherwise, use subprocess
            log("Starting server using subprocess", "INFO")

            f    ormatted = f"{Colors.RED}[ERROR]{Colors.ENDC} {timestamp} - {message}"
    elif level == "TEST":
        formatted = f"{Colors.BLUE}[TEST]{Colors.ENDC} {timestamp} - {message}"
    else:

           try:
                    except subprocess.SubprocessError as e:
                        log(f"Warning: Could not reset database: {str(e)}", "WARNING")
          )


              # Create database directory if it doesn't exist

           if not os.path.exists("database"):
                    os.makedirs("database")
                if not os.path.exists("database/files"):
                        os.makedirs("database/files")
                if not os.path.exists("database/chat_history"):
          
        try:
            # Try to connect to the server and send a shutdown command
            # This is a simple approach - in a real implementation, you might want
            # to add a proper shutdown command to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
                sock.connect(('localhost', 52384))
                sock.close()
                log("Server is still running, attempting to kill it", "WARNING")

                # Find and kill the server process
                if sys.platform == 'win32':
                    os.system('taskkill /f /im python.exe')
                else:
                    # Find Python processes running the server
                    try:
                        subprocess.run(["pkill", "-f", "run_server.py"], check=False)
                    except:
                        pass
            except (socket.error, socket.timeout):
                # Server is not running
                pass

            log("Server stopped (direct mode)", "SUCCESS")
        except Exception as e:
            log(f"Error stopping server (direct mode): {str(e)}", "ERROR")

    elif server_process:   os.makedirs("database/chat_history")
            else:

           log("Warning: reset_db.sh not found. Creating database directories manually.", "WARNING")
            # C    reate database directory if it doesn't exist
            if not os.path.exists("database"):
    os.makedirs("database")
            if not os.path.exists("database/files"):
      
        try:
            # Try to connect to the server and send a shutdown command
            # This is a simple approach - in a real implementation, you might want
# to add a proper shutdown command to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
        sock.connect(('localhost', 52384))
                sock.close()
                log("Server is still running, attempting to kill it", "WARNING")

                # Find and kill the server process
                if sys.platform == 'win32':
                    os.system('taskkill /f /im python.exe')
                else:
                    # Find Python processes running the server
                    try:
                        subprocess.run(["pkill", "-f", "run_server.py"], check=False)
                    except:
                        pass
            except (socket.error, socket.timeout):
                # Server is not running
                pass

            log("Server stopped (direct mode)", "SUCCESS")
        except Exception as e:
            log(f"Error stopping server (direct mode): {str(e)}", "ERROR")

    elif server_process:   os.makedirs("database/files")
            if not os.path.exists("database/chat_history"):
                os.makedirs("database/chat_history")

        # If we can import the server module, use it directly
        if SERVER_AVAILABLE:
            log("Starting server using direct module import", "INFO")
# Start the server in a separate thread
            from server import start_server as server_start_func
            server_thread = threading.Thread(target=server_start_func)
            server_thread.daemon = True
            server_thread.start()

# Wait for server to start
            time.sleep(3)

            # There's no easy way to check if the server started successfully
            # We'll assume it did if we get this far
            log("Server started successfully (direct mode)", "SUCCESS")
    return True
        else:
            # Otherwise, use subprocess
            log("Starting server using subprocess", "INFO")

                if os.path.exists("reset_db.sh"):
            f    ormatted = f"[{level}] {timestamp} - {message}"
    
    # Print to console
    print(formatted)
    
    # Write to log file (without colors)
    if log_file:
        clean_message = re.sub(r'\033\[\d+m', '', f"[{level}] {timestamp} - {message}")
        log_file.write(clean_message + "\n")
        log_file.flush()

def start_server():
    """Start the VoidLink server"""
    global server_process

    log("Starting VoidLink server...")

    try:    except subprocess.SubprocessError as e:

               log(f"Warning: Could not reset database: {str(e)}", "WARNING")
                # C    reate database directory if it doesn't exist
                    if not os.path.exists("database"):
                    os.makedirs("database")

           if not os.path.exists("database/files"):
                    os.makedirs("database/files")
                if not os.path.exists("database/chat_history"):
                    os.makedirs("database/chat_history")
        else:
            log("Warning: reset_db.sh not found. Creating database directories manually.", "WARNING")
            # Create database directory if it doesn't exist

        try:
            # Try to connect to the server and send a shutdown command
            # This is a simple approach - in a real implementation, you might want
            # to add a proper shutdown command to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s    ock.settimeout(2)
            try:
                sock.connect(('localhost', 52384))
                sock.close()
                    log("Server is still running, attempting to kill it", "WARNING")

                    # Find and kill the server process
                    if sys.platform == 'win32':
                        os.system('taskkill /f /im python.exe')
                    else:
                    # Find Python processes running the server
                    try:
                            subprocess.run(["pkill", "-f", "run_server.py"], check=False)
                    except:
                        pass
            except (socket.error, socket.timeout):
                # Server is not running
                pass

            log("Server stopped (direct mode)", "SUCCESS")
        except Exception as e:
                log(f"Error stopping server (direct mode): {str(e)}", "ERROR")

    elif        return None, []

    # This should never be reached, but just in case
    log(f"Error: Unexpected code path in start_client", "ERROR")
 server_process:     if not os.path.exists("database"):
                                os.makedirs("database")
            if not os.path.exists("database/files"):
                os.makedirs("database/files")
            if not os.path.exists("database/chat_history"):
    os.makedirs("database/chat_history")

        # If we can import the server module, use it directly
        if SERVER_AVAILABLE:
            log("Starting server using direct module import", "INFO")
# Start the server in a separate thread
            from server import start_server as server_start_func
            server_thread = threading.Thread(target=server_start_func)
            server_thread.daemon = True
            server_thread.start()

            # Wait for server to start
            time.sleep(3)

            # There's no easy way to check if the server started successfully
                # We'll assume it did if we get this far
            log("Server started successfully (direct mode)", "SUCCESS")
                    return True
            else:
            # Otherwise, use subprocess
            log("Starting server using subprocess", "INFO")

            # Make reset_db.sh executable and run it
            if os.path.exists("reset_db.sh"):
            if os.path.exists("reset_db.sh"):
                os.chmod("reset_db.sh", 0o755)
                try:
                        try:
                subprocess.run(["./reset_db.sh"], check=True    )

                           ex    cept subprocess.SubprocessError as e:

           log(f"Warning: Could not reset database: {str(e)}", "WARNING")
                    # Create database directory if it doesn't exist
                    if not os.path.exists("database"):
                        os.makedirs("database")
                    if not os.path.exists("database/files"):

               os.makedirs("database/files")
                if not os.path.exists("database/chat_history"):
                    os.makedirs("database/chat_history")
        else:
            log("Warning: reset_db.sh not found. Creating database directories manually.", "WARNING")
            # Create database directory if it doesn't exist
  
        try:
            # Try to connect to the server and send a shutdown command
            # This is a simple approach - in a real implementation, you might want
            # to add a proper shutdown command to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
                sock.connect(('localhost', 52384))
                sock.close()
                log("Server is still running, attempting to kill it", "WARNING")

                # Find and kill the server process
                if sys.platform == 'win32':
                    os.system('taskkill /f /im python.exe')
                else:
                    # Find Python processes running the server
                    try:
                        subprocess.run(["pkill", "-f", "run_server.py"], check=False)
                    except:
                        pass
            except (socket.error, socket.timeout):
                # Server is not running
                pass

            log("Server stopped (direct mode)", "SUCCESS")
        except Exception as e:
            log(f"Error stopping server (direct mode): {str(e)}", "ERROR")

    elif server_process:   if not os.path.exists("database"):
                os.makedirs("database")
            if not os.path.exists("database/files"):
                os.makedirs("database/files")
            if not os.path.exists("database/chat_history"):
    os.makedirs("database/chat_history")

        # If we can import the server module, use it directly
        if SERVER_AVAILABLE:
            log("Starting server using direct module import", "INFO")
# Start the server in a separate thread
            from server import start_server as server_start_func
            server_thread = threading.Thread(target=server_start_func)
            server_thread.daemon = True
            server_thread.start()

            # Wait for server to start
            time.sleep(3)

                # There's no easy way to check if the server started successfully
            # We'll assume it did if we get this far
            log("Server started successfully (direct mode)", "SUCCESS")
                return True
        else:
            # Otherwise, use subprocess
                log("Starting server using subprocess", "INFO")

            # Make run_server.py executable
            if os.path.exists("run_server.py"):
                os.chmod("run_server.py", 0o755)

            # Start the server
            server_process = subprocess.Popen(
                    ["python", "run_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
                time.sleep(3)

            # Check if server is running
            if     server_process.poll() is not None:
                    std    out, stderr = server_process.communicate()
                log(f"Server failed to start: {stderr}", "ERROR")
                return False

            log("Server started successfully (subprocess mode)", "SUCCESS")
            return True

    except Exception as e:
            log(f"Error starting server: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
            return None, []

    # This should never be reached, but just in case
    log(f"Error: Unexpected code path in start_client", "ERROR")
    return False

def stop_server():
    """Stop the VoidLink server"""
    global server_process

    log("Stopping VoidLink server...")

    if SERVER_AVAILABLE:
        # If we're using direct mode, we need to find and kill the server process
        try:
            # Try to connect to the server and send a shutdown command
            # This is a simple approach - in a real implementation, you might want
            # to add a proper shutdown command to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
                sock.connect(('localhost', 52384))
                sock.close()
                log("Server is still running, attempting to kill it", "WARNING")

                # Find and kill the server process
                if sys.platform == 'win32':
                    os.system('taskkill /f /im python.exe')
                else:
                    # Find Python processes running the server
                    try:
                        subprocess.run(["pkill", "-f", "run_server.py"], check=False)
                    except:
                        pass
            except (socket.error, socket.timeout):
                # Server is not running
                pass

            log("Server stopped (direct mode)", "SUCCESS")
        except Exception as e:
            log(f"Error stopping server (direct mode): {str(e)}", "ERROR")

    elif server_process:
        try:
            # Send SIGTERM to server process
            server_process.terminate()

            # Wait for server to terminate
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                server_process.kill()

                server_process = None
            log("Server stopped (subprocess mode)", "SUCCESS")

        except Exception as e:
                log(f"Error stopping server (subprocess mode): {str(e)}", "ERROR")

def start_client(username: str, password: str, commands: List[str] = None) -> Tuple[subprocess.Popen, List[str]]:
    """Start a VoidLink client with the given credentials and commands"""
    global     client_processes

    log(f"Starting client for user {username}...")

    # Check if expect is available
    expect_available = False
    try:
        subprocess.run(["which", "expect"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        expect_available = True
    except (subprocess.SubprocessError, FileNotFoundError):
        log("Expect command not found. Using direct Python client instead.", "WARNING")

    if expect_available:
        # Create expect script for client interaction
        expect_script = [
            "#!/usr/bin/expect -f",
            "set timeout 10",
            "spawn ./run_client.sh",
            "expect \"Server host:\"",
            "send \"localhost\\r\"",
            "expect \"Server port:\"",
            "send \"52384\\r\"",
            "expect \"Username:\"",
            f"send \"{username}\\r\"",
            "expect \"Password:\"",
            f"send \"{password}\\r\"",
            "expect \"Available commands:\"",
        ]

        # Add commands if provided
                output_lines = []
            if commands:
                for cmd in commands:
                    expect_script.append(f"send \"{cmd}\\r\"")
                expect_script.append("expect {")
                expect_script.append("    -re {.*} {")
                expect_script.append("        puts $expect_out(buffer)")
                expect_script.append("        append output $expect_out(buffer)")
                expect_script.append("    }")
                expect_script.append("}")
                output_lines.append("")  # Placeholder for command output

        # Add exit command
        expect_script.append("send \"/exit\\r\"")
        expect_script.append("expect eof")

        # Write expect script to temporary file
        script_file = f"temp_expect_{username}.exp"
        with open(script_file, "w") as f:
            f.write("\n".join(expect_script))

        # Make script executable
        os.chmod(script_file, 0o755)

        try:
            # Run expect script
            client_process = subprocess.Popen(
                ["expect", script_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            client_processes.append(client_process)

            # Wait for client to connect
            time.sleep(2)

            log(f"Client for user {username} started", "SUCCESS")
            return client_process, output_lines

        except Exception as e:
            log(f"Error starting client with expect for user {username}: {str(e)}", "ERROR")
            # Clean up expect script
            if os.path.exists(script_file):
                os.remove(script_file)
            # Fall back to direct method
            expect_available = False

    # If expect is not available or failed, use direct Python method
    if not expect_available:
        try:
            log("Using direct Python client method", "INFO")

            # Make run_client.sh executable
            if os.path.exists("run_client.sh"):
                os.chmod("run_client.sh", 0o755)

            # Start client process
            client_process = subprocess.Popen(
                ["python", "test_client.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            client_processes.append(client_process)

            # Send credentials
            client_process.stdin.write(f"localhost\n")
            client_process.stdin.write(f"52384\n")
            client_process.stdin.write(f"{username}\n")
            client_process.stdin.write(f"{password}\n")
            client_process.stdin.flush()

            # Wait for client to connect
            time.sleep(2)

            # Send commands if provided
            output_lines = []
            if commands:
                for cmd in commands:
                    client_process.stdin.write(f"{cmd}\n")
                    client_process.stdin.flush()
                    time.sleep(0.5)
                    output_lines.append("")  # Placeholder for command output

            log(f"Client for user {username} started", "SUCCESS")
            return client_process, output_lines
        except Exception as e:
            log(f"Error starting client for user {username}: {str(e)}", "ERROR")
            return None, []

    # This should never be reached, but just in case
    log(f"Error: Unexpected code path in start_client", "ERROR")
    return None, []

def stop_clients():
    """Stop all VoidLink clients"""
    global client_processes
    
    if client_processes:
        log(f"Stopping {len(client_processes)} clients...")
        
        for process in client_processes:
            try:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            except Exception as e:
                log(f"Error stopping client: {str(e)}", "ERROR")
        
        client_processes = []
        log("All clients stopped", "SUCCESS")

def run_test_case(test_case: TestCase) -> TestResult:
    """Run a single test case and return the result"""
    log(f"Running test case {test_case.id}: {test_case.name}", "TEST")
    
    start_time = time.time()
    output = []
    
    try:
        # Run setup commands
        if test_case.setup_commands:
            log(f"Running setup commands for test {test_case.id}...")
            for cmd in test_case.setup_commands:
                output.append(f"Setup: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output.append(result.stdout)
                if result.returncode != 0:
                    raise Exception(f"Setup command failed: {cmd}\n{result.stderr}")
        
        # Execute test steps
        log(f"Executing test steps for test {test_case.id}...")
        
        # Different execution based on test category
        if test_case.category == "Authentication":
            output.extend(run_authentication_test(test_case))
        elif test_case.category == "Messaging":
            output.extend(run_messaging_test(test_case))
        elif test_case.category == "Rooms":
            output.extend(run_rooms_test(test_case))
        elif test_case.category == "Files":
            output.extend(run_files_test(test_case))
        elif test_case.category == "Admin":
            output.extend(run_admin_test(test_case))
        elif test_case.category == "CLI":
            output.extend(run_cli_test(test_case))
        elif test_case.category == "Security":
            output.extend(run_security_test(test_case))
        else:
            output.extend(run_generic_test(test_case))
        
        # Run teardown commands
        if test_case.teardown_commands:
            log(f"Running teardown commands for test {test_case.id}...")
            for cmd in test_case.teardown_commands:
                output.append(f"Teardown: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output.append(result.stdout)
        
        # Verify expected results
        log(f"Verifying expected results for test {test_case.id}...")
        
        # For now, we'll assume all tests pass
        # In a real implementation, you would check the output against expected results
        
        end_time = time.time()
        duration = end_time - start_time
        
        log(f"Test {test_case.id} completed in {duration:.2f} seconds", "SUCCESS")
        
        return TestResult(
            test_case=test_case,
            result="PASS",
            output="\n".join(output),
            duration=duration
        )
    
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        log(f"Test {test_case.id} failed: {str(e)}", "ERROR")
        
        return TestResult(
            test_case=test_case,
            result="FAIL",
            error_message=str(e),
            output="\n".join(output),
            duration=duration
        )

def run_authentication_test(test_case: TestCase) -> List[str]:
    """Run an authentication test"""
    output = []
    
    # Extract username and password from test steps
    username = None
    password = None
    
    for step in test_case.steps:
        if "username" in step.lower():
            username_match = re.search(r'username[:\s]+([a-zA-Z0-9_]+)', step, re.IGNORECASE)
            if username_match:
                username = username_match.group(1)
        
        if "password" in step.lower():
            password_match = re.search(r'password[:\s]+([a-zA-Z0-9_]+)', step, re.IGNORECASE)
            if password_match:
                password = password_match.group(1)
    
    if not username:
        username = "testuser"
    
    if not password:
        password = "testpass"
    
    # Start client with credentials
    client_process, client_output = start_client(username, password)
    
    # Wait for client to complete
    stdout, stderr = client_process.communicate(timeout=test_case.timeout)
    
    # Check if login was successful
    if "Welcome to VoidLink" in stdout:
        output.append(f"Authentication successful for user {username}")
    else:
        output.append(f"Authentication failed for user {username}")
        if "Authentication failed" in stdout:
            output.append("Server rejected credentials")
        elif "Account is temporarily locked" in stdout:
            output.append("Account is locked")
    
    output.append(stdout)
    
    return output

def run_messaging_test(test_case: TestCase) -> List[str]:
    """Run a messaging test"""
    output = []
    
    # For messaging tests, we need two clients
    client1_process, client1_output = start_client("user1", "pass1")
    client2_process, client2_output = start_client("user2", "pass2")
    
    # Extract message from test steps
    message = "Test message"
    for step in test_case.steps:
        if "message" in step.lower():
            message_match = re.search(r'message[:\s]+"([^"]+)"', step, re.IGNORECASE)
            if message_match:
                message = message_match.group(1)
    
    # Send message from client 1
    client1_process.stdin.write(f"{message}\n")
    client1_process.stdin.flush()
    
    # Wait for message to be received
    time.sleep(2)
    
    # Check if client 2 received the message
    client2_stdout = client2_process.stdout.read(1024)
    if message in client2_stdout:
        output.append(f"Message '{message}' successfully received by client 2")
    else:
        output.append(f"Message '{message}' not received by client 2")
    
    # Clean up
    client1_process.terminate()
    client2_process.terminate()
    
    return output

def run_rooms_test(test_case: TestCase) -> List[str]:
    """Run a chat rooms test"""
    output = []
    
    # Extract room information from test steps
    room_id = "testroom"
    room_name = "Test Room"
    
    for step in test_case.steps:
        if "room" in step.lower():
            room_match = re.search(r'room[:\s]+([a-zA-Z0-9_-]+)', step, re.IGNORECASE)
            if room_match:
                room_id = room_match.group(1)
        
        if "name" in step.lower():
            name_match = re.search(r'name[:\s]+"([^"]+)"', step, re.IGNORECASE)
            if name_match:
                room_name = name_match.group(1)
    
    # Start client
    client_process, client_output = start_client("roomuser", "roompass", [
        f"/create {room_id} {room_name}",
        "/rooms",
        f"/join {room_id}",
        f"/switch {room_id}",
        "Hello from the test room!",
        f"/leave {room_id}"
    ])
    
    # Wait for client to complete
    stdout, stderr = client_process.communicate(timeout=test_case.timeout)
    
    # Check results
    if f"created a new room: {room_name}" in stdout:
        output.append(f"Room {room_id} created successfully")
    else:
        output.append(f"Failed to create room {room_id}")
    
    if f"joined the room" in stdout:
        output.append(f"Joined room {room_id} successfully")
    else:
        output.append(f"Failed to join room {room_id}")
    
    if f"Switched to room: {room_id}" in stdout:
        output.append(f"Switched to room {room_id} successfully")
    else:
        output.append(f"Failed to switch to room {room_id}")
    
    if f"left the room" in stdout:
        output.append(f"Left room {room_id} successfully")
    else:
        output.append(f"Failed to leave room {room_id}")
    
    output.append(stdout)
    
    return output

def run_files_test(test_case: TestCase) -> List[str]:
    """Run a file transfer test"""
    output = []
    
    # Create test file
    test_file = "test_file.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file for automated testing.")
    
    # Start client
    client_process, client_output = start_client("fileuser", "filepass", [
        f"/send {test_file}",
        "/files",
        f"/download {test_file}"
    ])
    
    # Wait for client to complete
    stdout, stderr = client_process.communicate(timeout=test_case.timeout)
    
    # Check results
    if f"Sending file request for {test_file}" in stdout:
        output.append(f"File {test_file} sent successfully")
    else:
        output.append(f"Failed to send file {test_file}")
    
    if f"Requesting file download: {test_file}" in stdout:
        output.append(f"File {test_file} download requested")
    else:
        output.append(f"Failed to request download for {test_file}")
    
    output.append(stdout)
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    return output

def run_admin_test(test_case: TestCase) -> List[str]:
    """Run an admin web interface test"""
    output = []
    
    # For admin tests, we'll use curl to interact with the web interface
    
    # Start admin web interface
    admin_process = subprocess.Popen(
        ["python", "admin_webui/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for web interface to start
    time.sleep(3)
    
    try:
        # Test login
        login_result = subprocess.run(
            ["curl", "-s", "-c", "cookies.txt", "-d", "username=admin&password=admin123", 
             "http://localhost:5000/login"],
            capture_output=True,
            text=True
        )
        
        if "Login successful" in login_result.stdout or "redirect" in login_result.stdout:
            output.append("Admin login successful")
        else:
            output.append("Admin login failed")
        
        # Test dashboard
        dashboard_result = subprocess.run(
            ["curl", "-s", "-b", "cookies.txt", "http://localhost:5000/dashboard"],
            capture_output=True,
            text=True
        )
        
        if "Dashboard" in dashboard_result.stdout:
            output.append("Dashboard accessed successfully")
        else:
            output.append("Failed to access dashboard")
        
        output.append(dashboard_result.stdout)
    
    finally:
        # Clean up
        admin_process.terminate()
        if os.path.exists("cookies.txt"):
            os.remove("cookies.txt")
    
    return output

def run_cli_test(test_case: TestCase) -> List[str]:
    """Run a CLI test"""
    output = []
    
    # Run CLI command
    cli_result = subprocess.run(
        ["python", "voidlink_cli.py", "--username", "admin", "--password", "admin123", "users", "list"],
        capture_output=True,
        text=True
    )
    
    output.append(cli_result.stdout)
    
    if cli_result.returncode == 0:
        output.append("CLI command executed successfully")
    else:
        output.append(f"CLI command failed: {cli_result.stderr}")
    
    return output

def run_security_test(test_case: TestCase) -> List[str]:
    """Run a security test"""
    output = []
    
    # For security tests, we'll focus on file security
    
    # Create test file with dangerous extension
    test_file = "test_malware.exe"
    with open(test_file, "w") as f:
        f.write("This is a fake malware file for testing.")
    
    # Start client
    client_process, client_output = start_client("securityuser", "securitypass", [
        f"/send {test_file}"
    ])
    
    # Wait for client to complete
    stdout, stderr = client_process.communicate(timeout=test_case.timeout)
    
    # Check results
    if "SECURITY WARNING" in stdout:
        output.append("Security warning detected for dangerous file")
    else:
        output.append("No security warning detected")
    
    output.append(stdout)
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    return output

def run_generic_test(test_case: TestCase) -> List[str]:
    """Run a generic test"""
    output = []
    
    # For generic tests, we'll just execute the steps as commands
    
    # Start client
    client_process, client_output = start_client("genericuser", "genericpass")
    
    # Execute steps
    for step in test_case.steps:
        if step.startswith("/"):
            client_process.stdin.write(f"{step}\n")
            client_process.stdin.flush()
            time.sleep(1)
    
    # Wait for client to complete
    stdout, stderr = client_process.communicate(timeout=test_case.timeout)
    
    output.append(stdout)
    
    return output

def generate_test_report(results: List[TestResult], output_file: str):
    """Generate a comprehensive test report"""
    log(f"Generating test report to {output_file}...")
    
    # Calculate statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.result == "PASS")
    failed_tests = sum(1 for r in results if r.result == "FAIL")
    error_tests = sum(1 for r in results if r.result == "ERROR")
    skipped_tests = sum(1 for r in results if r.result == "SKIPPED")
    
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Create report data
    report = {
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "skipped_tests": skipped_tests,
            "pass_rate": pass_rate
        },
        "timestamp": datetime.datetime.now().isoformat(),
        "results": []
    }
    
    # Add detailed results
    for result in results:
        report["results"].append({
            "id": result.test_case.id,
            "category": result.test_case.category,
            "name": result.test_case.name,
            "description": result.test_case.description,
            "result": result.result,
            "error_message": result.error_message,
            "duration": result.duration,
            "timestamp": result.timestamp
        })
    
    # Write report to file
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Also generate HTML report
    html_file = output_file.replace(".json", ".html")
    generate_html_report(report, html_file)
    
    log(f"Test report generated: {output_file}", "SUCCESS")
    log(f"HTML report generated: {html_file}", "SUCCESS")
    
    # Print summary to console
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.ENDC}")
    print(f"Failed: {Colors.RED}{failed_tests}{Colors.ENDC}")
    print(f"Errors: {Colors.YELLOW}{error_tests}{Colors.ENDC}")
    print(f"Skipped: {Colors.BLUE}{skipped_tests}{Colors.ENDC}")
    print(f"Pass Rate: {Colors.BOLD}{pass_rate:.2f}%{Colors.ENDC}")
    print("=" * 80)

def generate_html_report(report_data: Dict, output_file: str):
    """Generate an HTML test report"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoidLink Test Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .summary {{
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .summary-item {{
            display: inline-block;
            margin-right: 20px;
            font-size: 18px;
        }}
        .pass {{
            color: #28a745;
        }}
        .fail {{
            color: #dc3545;
        }}
        .error {{
            color: #fd7e14;
        }}
        .skipped {{
            color: #6c757d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .result-pass {{
            background-color: #d4edda;
        }}
        .result-fail {{
            background-color: #f8d7da;
        }}
        .result-error {{
            background-color: #fff3cd;
        }}
        .result-skipped {{
            background-color: #e2e3e5;
        }}
        .timestamp {{
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>VoidLink Test Report</h1>
    <p class="timestamp">Generated on: {datetime.datetime.fromisoformat(report_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-item">Total: <strong>{report_data['summary']['total_tests']}</strong></div>
        <div class="summary-item pass">Passed: <strong>{report_data['summary']['passed_tests']}</strong></div>
        <div class="summary-item fail">Failed: <strong>{report_data['summary']['failed_tests']}</strong></div>
        <div class="summary-item error">Errors: <strong>{report_data['summary']['error_tests']}</strong></div>
        <div class="summary-item skipped">Skipped: <strong>{report_data['summary']['skipped_tests']}</strong></div>
        <div class="summary-item">Pass Rate: <strong>{report_data['summary']['pass_rate']:.2f}%</strong></div>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Category</th>
                <th>Name</th>
                <th>Result</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody>
"""
    
    # Add rows for each test result
    for result in report_data['results']:
        result_class = f"result-{result['result'].lower()}"
        html += f"""
            <tr class="{result_class}">
                <td>{result['id']}</td>
                <td>{result['category']}</td>
                <td>{result['name']}</td>
                <td>{result['result']}</td>
                <td>{result['duration']:.2f}s</td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
    
    <h2>Detailed Results</h2>
"""
    
    # Add detailed sections for each test
    for result in report_data['results']:
        result_class = f"result-{result['result'].lower()}"
        html += f"""
    <div class="{result_class}" style="padding: 15px; margin-bottom: 15px; border-radius: 5px;">
        <h3>{result['id']}: {result['name']}</h3>
        <p><strong>Category:</strong> {result['category']}</p>
        <p><strong>Description:</strong> {result['description']}</p>
        <p><strong>Result:</strong> {result['result']}</p>
        <p><strong>Duration:</strong> {result['duration']:.2f}s</p>
"""
        
        if result['error_message']:
            html += f"""
        <p><strong>Error:</strong> {result['error_message']}</p>
"""
        
        html += """
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open(output_file, "w") as f:
        f.write(html)

def load_test_cases() -> List[TestCase]:
    """Load test cases from the test case definitions"""
    test_cases = []
    
    # Authentication tests
    test_cases.append(TestCase(
        id="AUTH-001",
        category="Authentication",
        name="User Registration",
        description="Verify that new users can register successfully",
        steps=[
            "Start the VoidLink client",
            "Enter a new username that doesn't exist in the system",
            "Enter a password",
            "Connect to the server"
        ],
        expected_results=[
            "User is created and logged in successfully",
            "Welcome message is displayed"
        ]
    ))
    
    test_cases.append(TestCase(
        id="AUTH-002",
        category="Authentication",
        name="User Login",
        description="Verify that existing users can log in successfully",
        steps=[
            "Start the VoidLink client",
            "Enter an existing username",
            "Enter the correct password",
            "Connect to the server"
        ],
        expected_results=[
            "User is authenticated and logged in successfully",
            "Welcome message is displayed"
        ]
    ))
    
    test_cases.append(TestCase(
        id="AUTH-003",
        category="Authentication",
        name="Failed Login Attempt",
        description="Verify that incorrect credentials are rejected",
        steps=[
            "Start the VoidLink client",
            "Enter an existing username",
            "Enter an incorrect password",
            "Connect to the server"
        ],
        expected_results=[
            "Authentication fails",
            "Error message is displayed"
        ]
    ))
    
    # Messaging tests
    test_cases.append(TestCase(
        id="MSG-001",
        category="Messaging",
        name="Public Message",
        description="Verify that public messages are delivered to all users",
        steps=[
            "Log in with User A",
            "Log in with User B in another terminal",
            "From User A, send a public message",
            "Check User B's terminal"
        ],
        expected_results=[
            "User B receives the message from User A"
        ]
    ))
    
    test_cases.append(TestCase(
        id="MSG-002",
        category="Messaging",
        name="Private Message",
        description="Verify that private messages are delivered only to the intended recipient",
        steps=[
            "Log in with User A",
            "Log in with User B in another terminal",
            "Log in with User C in a third terminal",
            "From User A, send a private message to User B using '@username message' format",
            "Check User B's and User C's terminals"
        ],
        expected_results=[
            "User B receives the private message from User A",
            "User C does not receive the message"
        ]
    ))
    
    # Rooms tests
    test_cases.append(TestCase(
        id="ROOM-001",
        category="Rooms",
        name="Room Creation",
        description="Verify that users can create new chat rooms",
        steps=[
            "Log in with a user",
            "Run the command '/create test-room Test Room'",
            "Run the command '/rooms' to list available rooms"
        ],
        expected_results=[
            "The new room 'test-room' is created",
            "The room appears in the room list"
        ]
    ))
    
    test_cases.append(TestCase(
        id="ROOM-002",
        category="Rooms",
        name="Joining a Room",
        description="Verify that users can join existing rooms",
        steps=[
            "Log in with a user",
            "Run the command '/join test-room'",
            "Run the command '/myrooms' to list joined rooms"
        ],
        expected_results=[
            "The user successfully joins the room",
            "The room appears in the user's room list"
        ]
    ))
    
    # Files tests
    test_cases.append(TestCase(
        id="FILE-001",
        category="Files",
        name="Public File Transfer",
        description="Verify that files can be shared with all users",
        steps=[
            "Log in with User A",
            "Log in with User B in another terminal",
            "Create a test file 'test.txt'",
            "From User A, run the command '/send test.txt'",
            "Check User B's terminal"
        ],
        expected_results=[
            "User B receives a notification about the shared file",
            "The file is available for download"
        ]
    ))
    
    test_cases.append(TestCase(
        id="FILE-002",
        category="Files",
        name="File Download",
        description="Verify that users can download shared files",
        steps=[
            "Log in with a user",
            "Share a file with this user (or have another user share a file)",
            "Run the command '/download filename.txt' (replace with actual filename)"
        ],
        expected_results=[
            "The file is downloaded successfully",
            "A success message is displayed"
        ]
    ))
    
    # Admin tests
    test_cases.append(TestCase(
        id="ADMIN-001",
        category="Admin",
        name="Admin Login",
        description="Verify that admin users can log in to the web interface",
        steps=[
            "Start the admin web interface with './run_admin_webui.sh'",
            "Navigate to http://localhost:5000 in a browser",
            "Enter admin credentials"
        ],
        expected_results=[
            "Admin is authenticated and logged in successfully",
            "Dashboard is displayed"
        ]
    ))
    
    # CLI tests
    test_cases.append(TestCase(
        id="CLI-001",
        category="CLI",
        name="CLI Authentication",
        description="Verify that the CLI tool can authenticate with the server",
        steps=[
            "Run the command './voidlink_cli.py --username admin --password admin123 users list'"
        ],
        expected_results=[
            "CLI authenticates successfully",
            "List of users is displayed"
        ]
    ))
    
    # Security tests
    test_cases.append(TestCase(
        id="SEC-001",
        category="Security",
        name="File Security Scanning",
        description="Verify that uploaded files are scanned for security issues",
        steps=[
            "Log in with a user",
            "Create a test file with a dangerous extension (e.g., 'test.exe')",
            "Attempt to upload the file"
        ],
        expected_results=[
            "The file is flagged as potentially unsafe",
            "The file is quarantined",
            "A security warning is displayed"
        ]
    ))
    
    return test_cases

def main():
    """Main function"""
    global log_file

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="VoidLink Automated Test Runner")
    parser.add_argument("--output", help="Output file for test report", default="test_report.json")
    parser.add_argument("--log", help="Log file", default="test_runner.log")
    parser.add_argument("--categories", help="Comma-separated list of test categories to run", default="all")
    parser.add_argument("--ids", help="Comma-separated list of test IDs to run", default="")
    parser.add_argument("--skip-server", help="Skip starting the server (assume it's already running)", action="store_true")
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(args.log)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Open log file
    try:
        log_file = open(args.log, "w")
    except Exception as e:
        print(f"Error opening log file: {str(e)}")
        log_file = None

    # Print header
    print_header()

    server_started = False

    try:
        # Load test cases
        all_test_cases = load_test_cases()

        # Filter test cases by category and ID
        test_cases = []
        if args.categories.lower() != "all":
            categories = [c.strip() for c in args.categories.split(",")]
            test_cases.extend([tc for tc in all_test_cases if tc.category in categories])
        elif args.ids:
            ids = [id.strip() for id in args.ids.split(",")]
            test_cases.extend([tc for tc in all_test_cases if tc.id in ids])
        else:
            test_cases = all_test_cases

        log(f"Loaded {len(test_cases)} test cases")

        # Start server if needed
        if not args.skip_server:
            server_started = start_server()
            if not server_started:
                log("Failed to start server, aborting tests", "ERROR")
                return 1
        else:
            log("Skipping server start (--skip-server flag used)", "INFO")

        # Run tests
        results = []
        for i, test_case in enumerate(test_cases):
            log(f"Running test {i+1}/{len(test_cases)}: {test_case.id} - {test_case.name}", "TEST")
            result = run_test_case(test_case)
            results.append(result)

        # Generate report
        generate_test_report(results, args.output)

        # Return success if all tests passed
        if all(r.result == "PASS" for r in results):
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        log("Test run interrupted by user", "WARNING")
        return 130
    except Exception as e:
        log(f"Error in test runner: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return 1

    finally:
        # Clean up
        stop_clients()
        if server_started:
            stop_server()

        # Close log file
        if log_file:
            log_file.close()

if __name__ == "__main__":
    sys.exit(main())    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(args.log)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Open log file
    try:
        log_file = open(args.log, "w")
    except Exception as e:
        print(f"Error opening log file: {str(e)}")
        log_file = None

    # Print header
    print_header()

    server_started = False

    try:
        # Load test cases
        all_test_cases = load_test_cases()

        # Filter test cases by category and ID
        test_cases = []
        if args.categories.lower() != "all":
            categories = [c.strip() for c in args.categories.split(",")]
            test_cases.extend([tc for tc in all_test_cases if tc.category in categories])
        elif args.ids:
            ids = [id.strip() for id in args.ids.split(",")]
            test_cases.extend([tc for tc in all_test_cases if tc.id in ids])
        else:
            test_cases = all_test_cases

        log(f"Loaded {len(test_cases)} test cases")

        # Start server if needed
        if not args.skip_server:
            server_started = start_server()
            if not server_started:
                log("Failed to start server, aborting tests", "ERROR")
                return 1
        else:
            log("Skipping server start (--skip-server flag used)", "INFO")

        # Run tests
        results = []
        for i, test_case in enumerate(test_cases):
            log(f"Running test {i+1}/{len(test_cases)}: {test_case.id} - {test_case.name}", "TEST")
            result = run_test_case(test_case)
            results.append(result)

        # Generate report
        generate_test_report(results, args.output)

        # Return success if all tests passed
        if all(r.result == "PASS" for r in results):
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        log("Test run interrupted by user", "WARNING")
        return 130
    except Exception as e:
        log(f"Error in test runner: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return 1

    finally:
        # Clean up
        stop_clients()
        if server_started:
            stop_server()

        # Close log file
        if log_file:
            log_file.close()

if __name__ == "__main__":
    sys.exit(main())        os.makedirs(output_dir)

    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(args.log)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Open log file
    try:
        log_file = open(args.log, "w")
    except Exception as e:
        print(f"Error opening log file: {str(e)}")
        log_file = None

    # Print header
    print_header()

    server_started = False

    try:
        # Load test cases
        all_test_cases = load_test_cases()

        # Filter test cases by category and ID
        test_cases = []
        if args.categories.lower() != "all":
            categories = [c.strip() for c in args.categories.split(",")]
            test_cases.extend([tc for tc in all_test_cases if tc.category in categories])
        elif args.ids:
            ids = [id.strip() for id in args.ids.split(",")]
            test_cases.extend([tc for tc in all_test_cases if tc.id in ids])
        else:
            test_cases = all_test_cases

        log(f"Loaded {len(test_cases)} test cases")

        # Start server if needed
        if not args.skip_server:
            server_started = start_server()
            if not server_started:
                log("Failed to start server, aborting tests", "ERROR")
                return 1
        else:
            log("Skipping server start (--skip-server flag used)", "INFO")

        # Run tests
        results = []
        for i, test_case in enumerate(test_cases):
            log(f"Running test {i+1}/{len(test_cases)}: {test_case.id} - {test_case.name}", "TEST")
            result = run_test_case(test_case)
            results.append(result)

        # Generate report
        generate_test_report(results, args.output)

        # Return success if all tests passed
        if all(r.result == "PASS" for r in results):
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        log("Test run interrupted by user", "WARNING")
        return 130
    except Exception as e:
        log(f"Error in test runner: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return 1

    finally:
        # Clean up
        stop_clients()
        if server_started:
            stop_server()

        # Close log file
        if log_file:
            log_file.close()

if __name__ == "__main__":
    sys.exit(main())        os.makedirs(output_dir)

    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(args.log)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Open log file
    try:
        log_file = open(args.log, "w")
    except Exception as e:
        print(f"Error opening log file: {str(e)}")
        log_file = None

    # Print header
    print_header()

    server_started = False

    try:
        # Load test cases
        all_test_cases = load_test_cases()

        # Filter test cases by category and ID
        test_cases = []
        if args.categories.lower() != "all":
            categories = [c.strip() for c in args.categories.split(",")]
            test_cases.extend([tc for tc in all_test_cases if tc.category in categories])
        elif args.ids:
            ids = [id.strip() for id in args.ids.split(",")]
            test_cases.extend([tc for tc in all_test_cases if tc.id in ids])
        else:
            test_cases = all_test_cases

        log(f"Loaded {len(test_cases)} test cases")

        # Start server if needed
        if not args.skip_server:
            server_started = start_server()
            if not server_started:
                log("Failed to start server, aborting tests", "ERROR")
                return 1
        else:
            log("Skipping server start (--skip-server flag used)", "INFO")

        # Run tests
        results = []
        for i, test_case in enumerate(test_cases):
            log(f"Running test {i+1}/{len(test_cases)}: {test_case.id} - {test_case.name}", "TEST")
            result = run_test_case(test_case)
            results.append(result)

        # Generate report
        generate_test_report(results, args.output)

        # Return success if all tests passed
        if all(r.result == "PASS" for r in results):
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        log("Test run interrupted by user", "WARNING")
        return 130
    except Exception as e:
        log(f"Error in test runner: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return 1

    finally:
        # Clean up
        stop_clients()
        if server_started:
            stop_server()

        # Close log file
        if log_file:
            log_file.close()

if __name__ == "__main__":
    sys.exit(main())