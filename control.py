#!/usr/bin/env python3
"""
FCU Drone Controller Client
Network-based interactive control for FCU core with enhanced UI
"""

import socket
import threading
import time
import sys
import signal
import json
import readline
import os
from typing import Dict, List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Apply color to text"""
        return f"{color}{text}{Colors.END}"


class DroneController:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = True

        # Command mapping with descriptions
        self.commands = {
            'a': {'name': 'Unlock', 'description': 'Unlock the drone'},
            'd': {'name': 'Lock', 'description': 'Lock the drone'},
            't': {'name': 'Takeoff', 'description': 'Take off the drone'},
            'l': {'name': 'Land', 'description': 'Land the drone'},
            'r': {'name': 'Run', 'description': 'Start mission'},
            's': {'name': 'Stop', 'description': 'Stop mission'},
            '1': {'name': 'Position 1', 'description': 'Go to position 1'},
            '2': {'name': 'Position 2', 'description': 'Go to position 2'},
            '3': {'name': 'Position 3', 'description': 'Go to position 3'},
            '4': {'name': 'Position 4', 'description': 'Go to position 4'},
            'p': {'name': 'Position Info', 'description': 'Get current position and orientation'},
            'i': {'name': 'Topic Info', 'description': 'List all ROS topics'},
            'h': {'name': 'Help', 'description': 'Show this help'},
            'q': {'name': 'Quit', 'description': 'Exit the program'}
        }

        # Setup readline for autocomplete
        self.setup_readline()

        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)

    def setup_readline(self):
        """Setup readline for autocomplete and history"""
        # Set up tab completion
        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")

        # Set up history file
        histfile = os.path.join(os.path.expanduser(
            "~"), ".drone_controller_history")
        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            pass

        # Save history on exit
        import atexit
        atexit.register(lambda: readline.write_history_file(histfile))

        # Set up readline options
        readline.set_history_length(1000)

    def completer(self, text: str, state: int) -> Optional[str]:
        """Tab completion for commands"""
        options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    def signal_handler(self, signum, frame):
        print(f"\n{Colors.YELLOW}Shutting down...{Colors.END}")
        self.disconnect()
        sys.exit(0)

    def connect(self):
        """Connect to FCU command server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            self.connected = True

            # Start receiving thread
            receive_thread = threading.Thread(
                target=self.receive_messages, daemon=True)
            receive_thread.start()

            print(
                f"{Colors.GREEN}✓{Colors.END} Connected to FCU server at {Colors.CYAN}{self.host}:{self.port}{Colors.END}")
            print(f"{Colors.GREEN}✓{Colors.END} Ready for commands!")
            return True

        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from server"""
        if self.connected and self.socket:
            try:
                self.socket.send(b"quit\n")
                self.socket.close()
            except:
                pass
            self.connected = False
            print(f"{Colors.YELLOW}ℹ{Colors.END} Disconnected from server")

    def receive_messages(self):
        """Receive messages from server in background thread"""
        buffer = ""
        while self.connected and self.running:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.handle_server_message(line.strip())

            except socket.timeout:
                # Timeout is normal, just continue
                continue
            except Exception as e:
                if self.connected:
                    print(f"{Colors.RED}✗{Colors.END} Receive error: {e}")
                break

    def handle_server_message(self, message):
        """Handle incoming JSON messages from server"""
        try:
            data = json.loads(message)
            msg_type = data.get('type', 'unknown')
            msg_text = data.get('message', '')
            timestamp = data.get('timestamp', 0)
            msg_data = data.get('data', {})

            # Always show raw JSON first (like bash command output)
            print(f"{Colors.WHITE}JSON Response:{Colors.END}")
            print(f"  {json.dumps(data, indent=2, ensure_ascii=False)}")
            print()

            if msg_type == 'welcome':
                print(
                    f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}{msg_text}{Colors.END}")
                if 'data' in data:
                    self.print_commands(data['data'])

            elif msg_type == 'command':
                print(
                    f"{Colors.GREEN}✓{Colors.END} Command executed: {Colors.BOLD}{msg_text}{Colors.END}")
                if 'command_id' in msg_data:
                    print(
                        f"  Command ID: {Colors.CYAN}{msg_data['command_id']}{Colors.END}")

            elif msg_type == 'status':
                print(f"{Colors.YELLOW}ℹ{Colors.END} Status: {msg_text}")

            elif msg_type == 'debug':
                print(
                    f"{Colors.MAGENTA}ℹ{Colors.END} Debug info: {Colors.BOLD}{msg_text}{Colors.END}")
                self.print_debug_data(msg_data)

            elif msg_type == 'help':
                print(
                    f"{Colors.CYAN}ℹ{Colors.END} Help: {Colors.BOLD}{msg_text}{Colors.END}")
                if 'commands' in msg_data:
                    self.print_commands(msg_data['commands'])

            elif msg_type == 'error':
                print(f"{Colors.RED}✗{Colors.END} Error: {msg_text}")

            elif msg_type == 'goodbye':
                print(f"{Colors.YELLOW}ℹ{Colors.END} {msg_text}")

            else:
                print(f"{Colors.WHITE}ℹ{Colors.END} {msg_text}")

        except json.JSONDecodeError:
            # Fallback for non-JSON messages
            print(f"{Colors.WHITE}Raw Response:{Colors.END}")
            print(f"  {message}")
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Failed to parse message: {e}")
            print(f"Raw message: {message}")

    def print_commands(self, commands_data):
        """Print available commands in a nice format"""
        print(f"\n{Colors.BOLD}Available Commands:{Colors.END}")
        print("=" * 50)
        for cmd, desc in commands_data.items():
            if cmd in self.commands:
                cmd_info = self.commands[cmd]
                print(
                    f"  {Colors.CYAN}{cmd:<3}{Colors.END} - {Colors.GREEN}{cmd_info['name']}{Colors.END}")
                print(
                    f"      {Colors.WHITE}{cmd_info['description']}{Colors.END}")
        print("=" * 50)

    def print_debug_data(self, data):
        """Print debug data in a formatted way"""
        if 'world_position' in data:
            pos = data['world_position']
            print(f"  {Colors.BOLD}World Position:{Colors.END}")
            print(f"    X: {Colors.CYAN}{pos.get('x', 'N/A'):.3f}{Colors.END}")
            print(f"    Y: {Colors.CYAN}{pos.get('y', 'N/A'):.3f}{Colors.END}")
            print(f"    Z: {Colors.CYAN}{pos.get('z', 'N/A'):.3f}{Colors.END}")

        if 'orientation' in data:
            orient = data['orientation']
            print(f"  {Colors.BOLD}Orientation:{Colors.END}")
            print(
                f"    Roll:  {Colors.CYAN}{orient.get('roll', 'N/A'):.3f}{Colors.END} rad")
            print(
                f"    Pitch: {Colors.CYAN}{orient.get('pitch', 'N/A'):.3f}{Colors.END} rad")
            print(
                f"    Yaw:   {Colors.CYAN}{orient.get('yaw', 'N/A'):.3f}{Colors.END} rad")

        if 'velocity' in data:
            vel = data['velocity']
            if 'linear' in vel:
                lin_vel = vel['linear']
                print(f"  {Colors.BOLD}Linear Velocity:{Colors.END}")
                print(
                    f"    X: {Colors.CYAN}{lin_vel.get('x', 'N/A'):.3f}{Colors.END} m/s")
                print(
                    f"    Y: {Colors.CYAN}{lin_vel.get('y', 'N/A'):.3f}{Colors.END} m/s")
                print(
                    f"    Z: {Colors.CYAN}{lin_vel.get('z', 'N/A'):.3f}{Colors.END} m/s")

        if 'imu' in data:
            imu = data['imu']
            if 'linear_acceleration' in imu:
                acc = imu['linear_acceleration']
                print(f"  {Colors.BOLD}IMU Acceleration:{Colors.END}")
                print(
                    f"    X: {Colors.CYAN}{acc.get('x', 'N/A'):.3f}{Colors.END} m/s²")
                print(
                    f"    Y: {Colors.CYAN}{acc.get('y', 'N/A'):.3f}{Colors.END} m/s²")
                print(
                    f"    Z: {Colors.CYAN}{acc.get('z', 'N/A'):.3f}{Colors.END} m/s²")

        if 'gnss' in data:
            gnss = data['gnss']
            print(f"  {Colors.BOLD}GNSS:{Colors.END}")
            print(
                f"    Latitude:  {Colors.CYAN}{gnss.get('latitude', 'N/A'):.6f}{Colors.END}")
            print(
                f"    Longitude: {Colors.CYAN}{gnss.get('longitude', 'N/A'):.6f}{Colors.END}")
            print(
                f"    Altitude:  {Colors.CYAN}{gnss.get('altitude', 'N/A'):.3f}{Colors.END} m")

        if 'topics' in data:
            topics = data['topics']
            print(f"  {Colors.BOLD}ROS Topics ({len(topics)} total):{Colors.END}")
            for topic in topics:  # Show all topics
                name = topic.get('name', 'Unknown')
                msg_type = topic.get('type', 'Unknown')
                print(
                    f"    {Colors.CYAN}{name:<30}{Colors.END} {Colors.WHITE}{msg_type}{Colors.END}")

    def send_command(self, command):
        """Send command to server"""
        if not self.connected:
            print(f"{Colors.RED}✗{Colors.END} Not connected to server")
            return False

        try:
            # Show what we're sending (like bash echo)
            print(
                f"{Colors.CYAN}$ {Colors.END}Sending command: {Colors.BOLD}'{command}'{Colors.END}")

            self.socket.send((command + '\n').encode('utf-8'))

            # Wait a bit for response
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Failed to send command: {e}")
            return False

    def show_help(self):
        """Show available commands"""
        print(f"\n{Colors.BOLD}Available Commands:{Colors.END}")
        print("─" * 60)

        # Group commands by category
        flight_commands = ['a', 'd', 't', 'l']
        mission_commands = ['r', 's', '1', '2', '3', '4']
        info_commands = ['p', 'i']
        system_commands = ['h', 'q']

        print(f"{Colors.BOLD}Flight Control:{Colors.END}")
        for cmd in flight_commands:
            if cmd in self.commands:
                info = self.commands[cmd]
                print(
                    f"  {Colors.CYAN}{cmd}{Colors.END}  {Colors.GREEN}{info['name']:<12}{Colors.END} {Colors.WHITE}{info['description']}{Colors.END}")

        print(f"\n{Colors.BOLD}Mission Control:{Colors.END}")
        for cmd in mission_commands:
            if cmd in self.commands:
                info = self.commands[cmd]
                print(
                    f"  {Colors.CYAN}{cmd}{Colors.END}  {Colors.GREEN}{info['name']:<12}{Colors.END} {Colors.WHITE}{info['description']}{Colors.END}")

        print(f"\n{Colors.BOLD}Information:{Colors.END}")
        for cmd in info_commands:
            if cmd in self.commands:
                info = self.commands[cmd]
                print(
                    f"  {Colors.CYAN}{cmd}{Colors.END}  {Colors.GREEN}{info['name']:<12}{Colors.END} {Colors.WHITE}{info['description']}{Colors.END}")

        print(f"\n{Colors.BOLD}System:{Colors.END}")
        for cmd in system_commands:
            if cmd in self.commands:
                info = self.commands[cmd]
                print(
                    f"  {Colors.CYAN}{cmd}{Colors.END}  {Colors.GREEN}{info['name']:<12}{Colors.END} {Colors.WHITE}{info['description']}{Colors.END}")

        print("─" * 60)
        print(f"Also try: {Colors.CYAN}clear{Colors.END}, {Colors.CYAN}ls{Colors.END}, {Colors.CYAN}help{Colors.END}, {Colors.CYAN}quit{Colors.END}")

    def interactive_mode(self):
        """Run interactive command mode"""
        print(f"\n{Colors.GREEN}Interactive Mode Started!{Colors.END}")
        print(
            f"Type {Colors.CYAN}'h'{Colors.END} for help, {Colors.CYAN}'q'{Colors.END} to quit")
        print(f"Use {Colors.YELLOW}TAB{Colors.END} for command autocomplete")
        print(f"Commands: {Colors.CYAN}a{Colors.END}d{Colors.CYAN}t{Colors.END}l{Colors.CYAN}r{Colors.END}s{Colors.CYAN}1234{Colors.END}p{Colors.CYAN}i{Colors.END}h{Colors.CYAN}q{Colors.END}")
        print()

        while self.connected and self.running:
            try:
                # Bash-like prompt with current time
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                prompt = f"{Colors.BOLD}{Colors.GREEN}> {Colors.END}"
                command = input(prompt).strip()

                if not command:
                    continue

                # Handle special commands first
                if command == 'q' or command == 'quit' or command == 'exit':
                    print(f"{Colors.YELLOW}Exiting...{Colors.END}")
                    break
                elif command == 'h' or command == 'help':
                    self.show_help()
                    continue
                elif command == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif command == 'ls' or command == 'commands':
                    self.show_help()
                    continue

                # Process single character commands
                if len(command) == 1 and command in self.commands:
                    cmd_info = self.commands[command]
                    print(
                        f"{Colors.CYAN}> {Colors.END}Executing: {Colors.BOLD}{cmd_info['name']}{Colors.END} - {cmd_info['description']}")

                    if self.send_command(command):
                        # The response will be handled by handle_server_message
                        pass
                    else:
                        print(f"{Colors.RED}✗{Colors.END} Failed to send command")
                else:
                    print(
                        f"{Colors.RED}✗{Colors.END} Command not found: {Colors.BOLD}'{command}'{Colors.END}")
                    print(
                        f"  Type {Colors.CYAN}'h'{Colors.END} for available commands")

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Use 'q' to quit{Colors.END}")
                continue
            except EOFError:
                break

    def run(self):
        """Main run loop"""
        print(f"{Colors.BOLD}{Colors.BLUE}FCU Drone Controller Client{Colors.END}")
        print("=" * 40)

        if not self.connect():
            return

        try:
            self.interactive_mode()
        finally:
            self.disconnect()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='FCU Drone Controller Client')
    parser.add_argument('--host', default='localhost',
                        help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8888,
                        help='Server port (default: 8888)')

    args = parser.parse_args()

    controller = DroneController(args.host, args.port)
    controller.run()


if __name__ == '__main__':
    main()
