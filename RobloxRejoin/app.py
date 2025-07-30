import os
import json
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from bot_controller import RobloxRejoinerBot
import threading
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "roblox_rejoiner_secret_key_2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Global bot instance
bot_instance = None
bot_thread = None
bot_running = False
log_messages = []

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default config if not exists
        default_config = {
            "place_id": "72829404259339",
            "mumu_path": "C:\\Program Files\\Netease\\MuMuPlayerGlobal-12.0\\shell\\MuMuPlayer.exe",
            "check_interval": 5,
            "cookie": "",
            "vip_server_code": "",
            "use_vip_server": False
        }
        save_config(default_config)
        return default_config

def save_config(config):
    """Save configuration to config.json"""
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def add_log_message(message):
    """Add a log message to the global log list"""
    global log_messages
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_messages.append(f"[{timestamp}] {message}")
    # Keep only last 100 messages
    if len(log_messages) > 100:
        log_messages = log_messages[-100:]
    logging.info(message)

@app.route('/')
def index():
    """Main dashboard page"""
    config = load_config()
    global bot_running
    return render_template('index.html', 
                         config=config, 
                         bot_running=bot_running,
                         log_messages=log_messages)

@app.route('/api/status')
def get_status():
    """Get current bot status"""
    global bot_instance, bot_running
    status = {
        'bot_running': bot_running,
        'mumu_running': False,
        'roblox_running': False,
        'adb_connected': False
    }
    
    if bot_instance:
        status['mumu_running'] = bot_instance.is_process_running("MuMuPlayer")
        status['roblox_running'] = bot_instance.is_package_running("com.roblox.client")
        status['adb_connected'] = bot_instance.check_adb_connection()
    
    return jsonify(status)

@app.route('/api/logs')
def get_logs():
    """Get recent log messages"""
    global log_messages
    return jsonify({'logs': log_messages})

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the Roblox Rejoiner Bot"""
    global bot_instance, bot_thread, bot_running
    
    if bot_running:
        return jsonify({'success': False, 'message': 'Bot is already running'})
    
    try:
        config = load_config()
        bot_instance = RobloxRejoinerBot(config, add_log_message)
        
        def run_bot():
            global bot_running
            bot_running = True
            try:
                if bot_instance:
                    bot_instance.run()
            except Exception as e:
                add_log_message(f"Bot error: {str(e)}")
            finally:
                bot_running = False
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        add_log_message("Bot started successfully")
        return jsonify({'success': True, 'message': 'Bot started successfully'})
    
    except Exception as e:
        add_log_message(f"Failed to start bot: {str(e)}")
        return jsonify({'success': False, 'message': f'Failed to start bot: {str(e)}'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the Roblox Rejoiner Bot"""
    global bot_instance, bot_running
    
    if not bot_running:
        return jsonify({'success': False, 'message': 'Bot is not running'})
    
    try:
        if bot_instance:
            bot_instance.stop()
        bot_running = False
        add_log_message("Bot stopped successfully")
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
    
    except Exception as e:
        add_log_message(f"Error stopping bot: {str(e)}")
        return jsonify({'success': False, 'message': f'Error stopping bot: {str(e)}'})

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        config = load_config()
        return jsonify(config)
    
    if request.method == 'POST':
        try:
            new_config = request.get_json()
            
            # Validate required fields
            required_fields = ['place_id', 'mumu_path', 'check_interval']
            for field in required_fields:
                if field not in new_config:
                    return jsonify({'success': False, 'message': f'Missing required field: {field}'})
            
            # Validate data types
            try:
                new_config['check_interval'] = int(new_config['check_interval'])
                new_config['use_vip_server'] = bool(new_config.get('use_vip_server', False))
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid data types in configuration'})
            
            save_config(new_config)
            add_log_message("Configuration updated successfully")
            return jsonify({'success': True, 'message': 'Configuration updated successfully'})
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error updating configuration: {str(e)}'})
    
    # Default return for unsupported methods
    return jsonify({'success': False, 'message': 'Method not allowed'})

@app.route('/api/test-mumu')
def test_mumu():
    """Test MuMu Player connection"""
    try:
        config = load_config()
        if bot_instance:
            result = bot_instance.is_process_running("MuMuPlayer")
        else:
            temp_bot = RobloxRejoinerBot(config, add_log_message)
            result = temp_bot.is_process_running("MuMuPlayer")
        
        message = "MuMu Player is running" if result else "MuMu Player is not running"
        return jsonify({'success': True, 'running': result, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error testing MuMu: {str(e)}'})

@app.route('/api/test-adb')
def test_adb():
    """Test ADB connection"""
    try:
        config = load_config()
        if bot_instance:
            result = bot_instance.check_adb_connection()
        else:
            temp_bot = RobloxRejoinerBot(config, add_log_message)
            result = temp_bot.check_adb_connection()
        
        message = "ADB connected successfully" if result else "ADB connection failed"
        return jsonify({'success': True, 'connected': result, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error testing ADB: {str(e)}'})

@app.route('/api/screenshot')
def take_screenshot():
    """Take screenshot from device"""
    try:
        config = load_config()
        if bot_instance and hasattr(bot_instance, 'screen_detector'):
            detector = bot_instance.screen_detector
        else:
            from screen_detector import ScreenDetector
            detector = ScreenDetector(config.get('adb_path', 'adb'), add_log_message)
        
        screenshot_base64 = detector.get_screenshot_base64()
        if screenshot_base64:
            add_log_message("Screenshot captured successfully")
            return jsonify({'success': True, 'screenshot': screenshot_base64})
        else:
            return jsonify({'success': False, 'message': 'Failed to capture screenshot'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error taking screenshot: {str(e)}'})

@app.route('/api/tap-screen', methods=['POST'])
def tap_screen():
    """Tap screen at specified coordinates"""
    try:
        data = request.get_json()
        x = int(data.get('x', 0))
        y = int(data.get('y', 0))
        
        config = load_config()
        if bot_instance and hasattr(bot_instance, 'screen_detector'):
            detector = bot_instance.screen_detector
        else:
            from screen_detector import ScreenDetector
            detector = ScreenDetector(config.get('adb_path', 'adb'), add_log_message)
        
        result = detector.tap_screen(x, y)
        if result:
            add_log_message(f"Tapped screen at ({x}, {y})")
            return jsonify({'success': True, 'message': f'Tapped at ({x}, {y})'})
        else:
            return jsonify({'success': False, 'message': 'Failed to tap screen'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error tapping screen: {str(e)}'})

@app.route('/api/detect-elements')
def detect_elements():
    """Detect game elements on screen"""
    try:
        config = load_config()
        if bot_instance and hasattr(bot_instance, 'screen_detector'):
            detector = bot_instance.screen_detector
        else:
            from screen_detector import ScreenDetector
            detector = ScreenDetector(config.get('adb_path', 'adb'), add_log_message)
        
        detections = detector.detect_game_elements()
        add_log_message(f"Detected {detections.get('total_buttons', 0)} UI elements")
        return jsonify({'success': True, 'detections': detections})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error detecting elements: {str(e)}'})

@app.route('/api/create-template', methods=['POST'])
def create_template():
    """Create template from screenshot coordinates"""
    try:
        data = request.get_json()
        name = data.get('name', '')
        x = int(data.get('x', 0))
        y = int(data.get('y', 0))
        width = int(data.get('width', 50))
        height = int(data.get('height', 50))
        
        if not name:
            return jsonify({'success': False, 'message': 'Template name is required'})
        
        config = load_config()
        if bot_instance and hasattr(bot_instance, 'screen_detector'):
            detector = bot_instance.screen_detector
        else:
            from screen_detector import ScreenDetector
            detector = ScreenDetector(config.get('adb_path', 'adb'), add_log_message)
        
        result = detector.create_template_from_screenshot(name, x, y, width, height)
        if result:
            add_log_message(f"Created template '{name}'")
            return jsonify({'success': True, 'message': f'Template "{name}" created'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create template'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating template: {str(e)}'})

@app.route('/api/find-and-tap', methods=['POST'])
def find_and_tap():
    """Find template and tap on it"""
    try:
        data = request.get_json()
        template_name = data.get('template_name', '')
        threshold = float(data.get('threshold', 0.8))
        
        if not template_name:
            return jsonify({'success': False, 'message': 'Template name is required'})
        
        config = load_config()
        if bot_instance and hasattr(bot_instance, 'screen_detector'):
            detector = bot_instance.screen_detector
        else:
            from screen_detector import ScreenDetector
            detector = ScreenDetector(config.get('adb_path', 'adb'), add_log_message)
        
        result = detector.find_and_tap(template_name, threshold)
        if result:
            add_log_message(f"Found and tapped template '{template_name}'")
            return jsonify({'success': True, 'message': f'Found and tapped "{template_name}"'})
        else:
            return jsonify({'success': False, 'message': f'Template "{template_name}" not found or failed to tap'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error finding and tapping: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
