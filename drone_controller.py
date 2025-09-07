#!/usr/bin/env python3
"""
FCU Drone Controller Client
Network-based interactive control for FCU core
"""

import socket
import threading
import time
import sys
import signal

class DroneController:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = True
        
        # Command mapping
        self.commands = {
            'a': 'Unlock',
            'd': 'Lock', 
            't': 'Takeoff',
            'l': 'Land',
            'r': 'Run',
            's': 'Stop',
            '1': 'Position 1',
            '2': 'Position 2',
            '3': 'Position 3',
            '4': 'Position 4',
            'h': 'Help',
            'q': 'Quit'
        }
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        print("\nShutting down...")
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
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
            print(f"[OK] Connected to FCU server at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
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
            print("[INFO] Disconnected from server")
            
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
                    print(f"[ERROR] Receive error: {e}")
                break
                
    def handle_server_message(self, message):
        """Handle incoming messages from server"""
        if message.startswith("FCU Command Server Connected!"):
            print("[SERVER] " + message)
        elif message.startswith("Command:"):
            print("[CMD] " + message)
        elif message.startswith("STATUS:"):
            print("[STATUS] " + message[7:])
        elif message.startswith("Commands:"):
            print("[HELP] " + message)
        else:
            print("[MSG] " + message)
            
    def send_command(self, command):
        """Send command to server"""
        if not self.connected:
            print("[ERROR] Not connected to server")
            return False
            
        try:
            self.socket.send((command + '\n').encode('utf-8'))
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send command: {e}")
            return False
            
    def show_help(self):
        """Show available commands"""
        print("\nFCU Drone Controller Commands:")
        print("=" * 50)
        for cmd, desc in self.commands.items():
            if cmd not in ['h', 'q']:
                print(f"  {cmd:<3} - {desc}")
        print("  h    - Show this help")
        print("  q    - Quit")
        print("=" * 50)
        
    def interactive_mode(self):
        """Run interactive command mode"""
        print("\nInteractive Mode Started!")
        print("Type 'h' for help, 'q' to quit")
        
        while self.connected and self.running:
            try:
                command = input("\nFCU> ").strip().lower()
                
                if not command:
                    continue
                    
                if command == 'q':
                    break
                elif command == 'h':
                    self.show_help()
                elif command in self.commands:
                    if self.send_command(command):
                        print(f"[SENT] Command: {self.commands[command]}")
                else:
                    print("[ERROR] Invalid command. Type 'h' for help.")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
                
    def run(self):
        """Main run loop"""
        print("FCU Drone Controller Client")
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
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8888, help='Server port (default: 8888)')
    
    args = parser.parse_args()
    
    controller = DroneController(args.host, args.port)
    controller.run()

if __name__ == '__main__':
    main()
