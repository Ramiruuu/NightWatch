# quick_test.py - Run this to test your servers
import socket

def test_tcp():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 4444))
        sock.send(b'Hello from Python test!\n')
        print("✅ TCP test successful - message sent!")
        sock.close()
    except Exception as e:
        print(f"❌ TCP test failed: {e}")

def test_udp():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'Hello UDP test!', ('localhost', 4445))
        print("✅ UDP test successful - message sent!")
        sock.close()
    except Exception as e:
        print(f"❌ UDP test failed: {e}")

if __name__ == "__main__":
    print("Testing NightWatch Servers...")
    test_tcp()
    test_udp()