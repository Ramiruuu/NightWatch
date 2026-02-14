from flask import Flask, render_template, jsonify, request
from server_core import server
import threading
import time
import json

app = Flask(__name__)

# Store connected clients for real-time updates (Server-Sent Events)
clients = []

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/logs')
def logs():
    """Logs viewer page"""
    return render_template('logs.html')

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/api/status')
def api_status():
    """API endpoint for server status"""
    return jsonify(server.get_status())

@app.route('/api/messages')
def api_messages():
    """API endpoint for recent messages"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        'messages': server.get_messages(limit)
    })

@app.route('/api/start/tcp', methods=['POST'])
def api_start_tcp():
    """Start TCP server"""
    data = request.json
    host = data.get('host', '0.0.0.0')
    try:
        port = int(data.get('port', 4444))
        success, message = server.start_tcp_server(host, port)
        return jsonify({'success': success, 'message': message})
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Invalid port number: {str(e)}'})

@app.route('/api/start/udp', methods=['POST'])
def api_start_udp():
    """Start UDP server"""
    data = request.json
    host = data.get('host', '0.0.0.0')
    try:
        port = int(data.get('port', 4445))
        success, message = server.start_udp_server(host, port)
        return jsonify({'success': success, 'message': message})
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Invalid port number: {str(e)}'})

@app.route('/api/stop/tcp', methods=['POST'])
def api_stop_tcp():
    """Stop TCP server"""
    server.stop_tcp()
    return jsonify({'success': True, 'message': 'TCP Server stopped'})

@app.route('/api/stop/udp', methods=['POST'])
def api_stop_udp():
    """Stop UDP server"""
    server.stop_udp()
    return jsonify({'success': True, 'message': 'UDP Server stopped'})

@app.route('/api/stop/all', methods=['POST'])
def api_stop_all():
    """Stop all servers"""
    server.stop_all()
    return jsonify({'success': True, 'message': 'All servers stopped'})

@app.route('/api/clear', methods=['POST'])
def api_clear():
    """Clear message history"""
    server.clear_messages()
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/stream')
def stream():
    """Server-Sent Events for real-time updates"""
    def event_stream():
        last_message_count = len(server.message_history)
        while True:
            # Check for new messages
            current_count = len(server.message_history)
            if current_count > last_message_count:
                new_messages = server.message_history[last_message_count:]
                last_message_count = current_count
                yield f"data: {json.dumps({'type': 'messages', 'data': new_messages})}\n\n"
            
            # Send heartbeat every 5 seconds
            yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            time.sleep(1)
    
    return app.response_class(
        event_stream(),
        mimetype='text/event-stream'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)