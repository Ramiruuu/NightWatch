import socket
import threading
import json
import time
from datetime import datetime
from queue import Queue
import logging

class RedTeamServer:
    def __init__(self):
        self.tcp_socket = None
        self.udp_socket = None
        self.tcp_running = False
        self.udp_running = False
        self.tcp_thread = None
        self.udp_thread = None
        self.clients = []
        self.message_queue = Queue()
        self.message_history = []
        self.connections = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def start_tcp_server(self, host='0.0.0.0', port=4444):
        """Start TCP server in a new thread"""
        if self.tcp_running:
            return False, "TCP server already running"
            
        self.tcp_running = True
        self.tcp_thread = threading.Thread(
            target=self._run_tcp_server,
            args=(host, port),
            daemon=True
        )
        self.tcp_thread.start()
        self._add_message(f"TCP Server started on {host}:{port}", "success")
        return True, f"TCP Server started on {host}:{port}"
        
    def _run_tcp_server(self, host, port):
        """Main TCP server loop"""
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.tcp_socket.bind((host, port))
            self.tcp_socket.listen(5)
            self.tcp_socket.settimeout(1.0)
            
            while self.tcp_running:
                try:
                    client_socket, address = self.tcp_socket.accept()
                    # Handle client in new thread
                    client_thread = threading.Thread(
                        target=self._handle_tcp_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                    connection_info = {
                        'type': 'TCP',
                        'address': f"{address[0]}:{address[1]}",
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.connections.append(connection_info)
                    self._add_message(f"TCP connection from {address[0]}:{address[1]}", "info")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.tcp_running:
                        self._add_message(f"TCP error: {str(e)}", "error")
                        
        except Exception as e:
            self._add_message(f"Failed to start TCP server: {str(e)}", "error")
        finally:
            if self.tcp_socket:
                self.tcp_socket.close()
                
    def _handle_tcp_client(self, client_socket, address):
        """Handle individual TCP client"""
        with client_socket:
            client_socket.settimeout(1.0)
            while self.tcp_running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                        
                    message = data.decode('utf-8', errors='ignore').strip()
                    self._add_message(f"[TCP:{address[0]}] {message}", "tcp-message")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    break
                    
        self._add_message(f"TCP client {address[0]} disconnected", "info")
        
    def start_udp_server(self, host='0.0.0.0', port=4445):
        """Start UDP server in a new thread"""
        if self.udp_running:
            return False, "UDP server already running"
            
        self.udp_running = True
        self.udp_thread = threading.Thread(
            target=self._run_udp_server,
            args=(host, port),
            daemon=True
        )
        self.udp_thread.start()
        self._add_message(f"UDP Server started on {host}:{port}", "success")
        return True, f"UDP Server started on {host}:{port}"
        
    def _run_udp_server(self, host, port):
        """Main UDP server loop"""
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.udp_socket.bind((host, port))
            self.udp_socket.settimeout(1.0)
            
            while self.udp_running:
                try:
                    data, address = self.udp_socket.recvfrom(1024)
                    message = data.decode('utf-8', errors='ignore').strip()
                    
                    connection_info = {
                        'type': 'UDP',
                        'address': f"{address[0]}:{address[1]}",
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.connections.append(connection_info)
                    
                    self._add_message(f"[UDP:{address[0]}] {message}", "udp-message")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.udp_running:
                        self._add_message(f"UDP error: {str(e)}", "error")
                        
        except Exception as e:
            self._add_message(f"Failed to start UDP server: {str(e)}", "error")
        finally:
            if self.udp_socket:
                self.udp_socket.close()
                
    def _add_message(self, message, msg_type="info"):
        """Add message to history and queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg_data = {
            'timestamp': timestamp,
            'message': message,
            'type': msg_type
        }
        self.message_history.append(msg_data)
        self.message_queue.put(msg_data)
        
        # Keep only last 1000 messages
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]
            
    def stop_tcp(self):
        """Stop TCP server"""
        self.tcp_running = False
        if self.tcp_socket:
            self.tcp_socket.close()
        self._add_message("TCP Server stopped", "warning")
        
    def stop_udp(self):
        """Stop UDP server"""
        self.udp_running = False
        if self.udp_socket:
            self.udp_socket.close()
        self._add_message("UDP Server stopped", "warning")
        
    def stop_all(self):
        """Stop all servers"""
        self.stop_tcp()
        self.stop_udp()
        
    def get_status(self):
        """Get current server status"""
        return {
            'tcp_running': self.tcp_running,
            'udp_running': self.udp_running,
            'connections': len(self.connections[-10:]),  # Last 10 connections
            'messages': len(self.message_history),
            'total_connections': len(self.connections)
        }
        
    def get_messages(self, limit=50):
        """Get recent messages"""
        return self.message_history[-limit:]
        
    def clear_messages(self):
        """Clear message history"""
        self.message_history = []
        self.connections = []
        self._add_message("Message history cleared", "info")

# Create global server instance
server = RedTeamServer()