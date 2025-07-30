import subprocess
import time
import os
from PIL import Image
import io
import base64
import numpy as np

# Try to import OpenCV with fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV not available, using PIL-based fallback")

class ScreenDetector:
    def __init__(self, adb_path, log_callback=None):
        """Initialize screen detector with ADB path"""
        self.adb_path = adb_path
        self.log_callback = log_callback or print
        self.templates = {}
        self.last_screenshot = None
        
    def log(self, message):
        """Log a message using the callback function"""
        if self.log_callback:
            self.log_callback(message)
    
    def take_screenshot(self):
        """Take screenshot from Android device via ADB"""
        try:
            # Check if ADB is available first
            subprocess.run([self.adb_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            
            # Take screenshot using ADB
            result = subprocess.run([
                self.adb_path, 'shell', 'screencap', '-p'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            
            if result.returncode != 0:
                self.log(f"Failed to take screenshot: {result.stderr.decode()}")
                return None
            
            # Convert screenshot data to PIL Image
            screenshot_data = result.stdout.replace(b'\r\n', b'\n')
            
            if CV2_AVAILABLE:
                # Use OpenCV if available
                image = cv2.imdecode(np.frombuffer(screenshot_data, np.uint8), cv2.IMREAD_COLOR)
                if image is None:
                    self.log("Failed to decode screenshot with OpenCV")
                    return None
                self.last_screenshot = image
                return image
            else:
                # Use PIL as fallback
                try:
                    pil_image = Image.open(io.BytesIO(screenshot_data))
                    # Convert PIL to numpy array for consistency
                    image_array = np.array(pil_image)
                    self.last_screenshot = image_array
                    return image_array
                except Exception as e:
                    self.log(f"Failed to decode screenshot with PIL: {e}")
                    return None
            
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self.log(f"ADB not available: {e}")
            return None
        except Exception as e:
            self.log(f"Error taking screenshot: {e}")
            return None
    
    def load_template(self, name, template_path):
        """Load a template image for matching"""
        try:
            if os.path.exists(template_path):
                if CV2_AVAILABLE:
                    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                    if template is not None:
                        self.templates[name] = template
                        self.log(f"Loaded template: {name}")
                        return True
                else:
                    # Use PIL as fallback
                    pil_image = Image.open(template_path)
                    template = np.array(pil_image)
                    self.templates[name] = template
                    self.log(f"Loaded template: {name}")
                    return True
            self.log(f"Template not found: {template_path}")
            return False
        except Exception as e:
            self.log(f"Error loading template {name}: {e}")
            return False
    
    def create_template_from_screenshot(self, name, x, y, width, height):
        """Create template from current screenshot coordinates"""
        if self.last_screenshot is None:
            self.log("No screenshot available for template creation")
            return False
        
        try:
            template = self.last_screenshot[y:y+height, x:x+width]
            self.templates[name] = template
            
            # Save template for future use
            template_path = f"templates/{name}.png"
            os.makedirs("templates", exist_ok=True)
            
            if CV2_AVAILABLE:
                cv2.imwrite(template_path, template)
            else:
                # Use PIL to save
                pil_image = Image.fromarray(template)
                pil_image.save(template_path)
            
            self.log(f"Created template '{name}' from screenshot")
            return True
        except Exception as e:
            self.log(f"Error creating template: {e}")
            return False
    
    def find_template(self, template_name, threshold=0.8):
        """Find template in current screenshot"""
        if template_name not in self.templates:
            self.log(f"Template '{template_name}' not loaded")
            return None
        
        if self.last_screenshot is None:
            screenshot = self.take_screenshot()
            if screenshot is None:
                return None
        else:
            screenshot = self.last_screenshot
        
        try:
            template = self.templates[template_name]
            
            if CV2_AVAILABLE:
                # Use OpenCV template matching
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= threshold:
                    # Calculate center point
                    h, w = template.shape[:2]
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    
                    self.log(f"Found '{template_name}' at ({center_x}, {center_y}) with confidence {max_val:.2f}")
                    return {
                        'found': True,
                        'confidence': max_val,
                        'position': (center_x, center_y),
                        'top_left': max_loc,
                        'bottom_right': (max_loc[0] + w, max_loc[1] + h)
                    }
                else:
                    self.log(f"Template '{template_name}' not found (confidence: {max_val:.2f})")
                    return {'found': False, 'confidence': max_val}
            else:
                # Simplified matching without OpenCV (basic color matching)
                self.log("OpenCV not available, using basic matching")
                h, w = template.shape[:2]
                # Simple search for template in screenshot
                # This is a basic implementation - in real use, you'd want more sophisticated matching
                return {'found': False, 'confidence': 0.0, 'message': 'OpenCV required for template matching'}
                
        except Exception as e:
            self.log(f"Error finding template: {e}")
            return None
    
    def tap_screen(self, x, y):
        """Tap screen at specified coordinates"""
        try:
            result = subprocess.run([
                self.adb_path, 'shell', 'input', 'tap', str(x), str(y)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            
            if result.returncode == 0:
                self.log(f"Tapped at ({x}, {y})")
                return True
            else:
                self.log(f"Failed to tap: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            self.log(f"Error tapping screen: {e}")
            return False
    
    def swipe_screen(self, x1, y1, x2, y2, duration=500):
        """Swipe from one point to another"""
        try:
            result = subprocess.run([
                self.adb_path, 'shell', 'input', 'swipe', 
                str(x1), str(y1), str(x2), str(y2), str(duration)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            
            if result.returncode == 0:
                self.log(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
                return True
            else:
                self.log(f"Failed to swipe: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            self.log(f"Error swiping screen: {e}")
            return False
    
    def find_and_tap(self, template_name, threshold=0.8):
        """Find template and tap on it"""
        result = self.find_template(template_name, threshold)
        if result and result['found']:
            x, y = result['position']
            return self.tap_screen(x, y)
        return False
    
    def get_screenshot_base64(self):
        """Get current screenshot as base64 string for web display"""
        if self.last_screenshot is None:
            screenshot = self.take_screenshot()
        else:
            screenshot = self.last_screenshot
            
        if screenshot is None:
            return None
        
        try:
            if CV2_AVAILABLE:
                # Convert BGR to RGB for OpenCV
                screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(screenshot_rgb)
            else:
                # Already in RGB format from PIL
                pil_image = Image.fromarray(screenshot)
            
            # Convert to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            self.log(f"Error converting screenshot to base64: {e}")
            return None
    
    def detect_game_elements(self):
        """Detect common Roblox game elements"""
        screenshot = self.take_screenshot()
        if screenshot is None:
            return {}
        
        # Common Roblox UI elements detection
        detections = {}
        
        if CV2_AVAILABLE:
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Detect buttons using edge detection
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 50000:  # Filter by size
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 3:  # Filter by aspect ratio
                        buttons.append({
                            'x': x + w//2,
                            'y': y + h//2,
                            'width': w,
                            'height': h,
                            'area': area
                        })
            
            detections['buttons'] = buttons[:10]  # Limit to top 10
            detections['total_buttons'] = len(buttons)
        else:
            # Basic detection without OpenCV
            detections['buttons'] = []
            detections['total_buttons'] = 0
            detections['message'] = 'OpenCV required for advanced detection'
        
        return detections