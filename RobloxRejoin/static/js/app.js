// Roblox Rejoiner Bot Web Interface
const App = {
    // Application state
    state: {
        botRunning: false,
        autoRefresh: true,
        refreshInterval: null
    },

    // Initialize the application
    init() {
        this.bindEvents();
        this.bindScreenDetectionEvents();
        this.updateStatus();
        this.startAutoRefresh();
        this.setupVipServerToggle();
    },

    // Bind event listeners
    bindEvents() {
        // Bot control buttons
        document.getElementById('start-bot-btn').addEventListener('click', () => this.startBot());
        document.getElementById('stop-bot-btn').addEventListener('click', () => this.stopBot());
        
        // Test connection buttons
        document.getElementById('test-mumu-btn').addEventListener('click', () => this.testMumu());
        document.getElementById('test-adb-btn').addEventListener('click', () => this.testAdb());
        
        // Configuration form
        document.getElementById('config-form').addEventListener('submit', (e) => this.saveConfig(e));
        
        // Clear logs button
        document.getElementById('clear-logs-btn').addEventListener('click', () => this.clearLogs());
        
        // VIP server checkbox
        document.getElementById('use_vip_server').addEventListener('change', () => this.toggleVipServer());
        
        // Screen detection controls
        this.bindScreenDetectionEvents();
    },

    // Setup VIP server section toggle
    setupVipServerToggle() {
        this.toggleVipServer();
    },

    // Toggle VIP server section visibility
    toggleVipServer() {
        const checkbox = document.getElementById('use_vip_server');
        const section = document.getElementById('vip-server-section');
        section.style.display = checkbox.checked ? 'block' : 'none';
    },

    // Start the bot
    async startBot() {
        this.setButtonLoading('start-bot-btn', true);
        
        try {
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', 'Bot started successfully');
                this.state.botRunning = true;
                this.updateButtonStates();
            } else {
                this.showNotification('error', result.message || 'Failed to start bot');
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('start-bot-btn', false);
        }
    },

    // Stop the bot
    async stopBot() {
        this.setButtonLoading('stop-bot-btn', true);
        
        try {
            const response = await fetch('/api/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', 'Bot stopped successfully');
                this.state.botRunning = false;
                this.updateButtonStates();
            } else {
                this.showNotification('error', result.message || 'Failed to stop bot');
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('stop-bot-btn', false);
        }
    },

    // Test MuMu connection
    async testMumu() {
        this.setButtonLoading('test-mumu-btn', true);
        
        try {
            const response = await fetch('/api/test-mumu');
            const result = await response.json();
            
            if (result.success) {
                const type = result.running ? 'success' : 'warning';
                this.showNotification(type, result.message);
            } else {
                this.showNotification('error', result.message);
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('test-mumu-btn', false);
        }
    },

    // Test ADB connection
    async testAdb() {
        this.setButtonLoading('test-adb-btn', true);
        
        try {
            const response = await fetch('/api/test-adb');
            const result = await response.json();
            
            if (result.success) {
                const type = result.connected ? 'success' : 'warning';
                this.showNotification(type, result.message);
            } else {
                this.showNotification('error', result.message);
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('test-adb-btn', false);
        }
    },

    // Save configuration
    async saveConfig(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const config = {};
        
        // Convert form data to object
        for (let [key, value] of formData.entries()) {
            if (key === 'use_vip_server') {
                config[key] = true; // Checkbox is checked if present
            } else {
                config[key] = value;
            }
        }
        
        // Ensure use_vip_server is set to false if not checked
        if (!config.use_vip_server) {
            config.use_vip_server = false;
        }
        
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', 'Configuration saved successfully');
            } else {
                this.showNotification('error', result.message || 'Failed to save configuration');
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        }
    },

    // Update system status
    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const status = await response.json();
            
            // Update bot running state
            this.state.botRunning = status.bot_running;
            this.updateButtonStates();
            
            // Update status indicators
            this.updateStatusIndicator('bot-status', status.bot_running, 'Running', 'Stopped');
            this.updateStatusIndicator('mumu-status', status.mumu_running, 'Running', 'Stopped');
            this.updateStatusIndicator('roblox-status', status.roblox_running, 'Running', 'Stopped');
            this.updateStatusIndicator('adb-status', status.adb_connected, 'Connected', 'Disconnected');
            
            // Update navbar status
            const navbarIndicator = document.getElementById('status-indicator');
            const navbarText = document.getElementById('status-text');
            
            if (navbarIndicator && navbarText) {
                if (status.bot_running) {
                    navbarIndicator.className = 'fas fa-circle text-success';
                    navbarText.textContent = 'Bot Running';
                } else {
                    navbarIndicator.className = 'fas fa-circle text-secondary';
                    navbarText.textContent = 'Bot Stopped';
                }
            }
            
        } catch (error) {
            console.error('Error updating status:', error);
            // Don't show error to user in demo mode
        }
    },

    // Update individual status indicator
    updateStatusIndicator(prefix, isActive, activeText, inactiveText) {
        const icon = document.getElementById(prefix + '-icon');
        const text = document.getElementById(prefix + '-text');
        
        if (isActive) {
            icon.className = icon.className.replace(/text-\w+/, 'text-success');
            text.textContent = activeText;
            text.className = 'fw-bold text-success';
        } else {
            icon.className = icon.className.replace(/text-\w+/, 'text-secondary');
            text.textContent = inactiveText;
            text.className = 'fw-bold text-secondary';
        }
    },

    // Update button states based on bot status
    updateButtonStates() {
        const startBtn = document.getElementById('start-bot-btn');
        const stopBtn = document.getElementById('stop-bot-btn');
        
        if (this.state.botRunning) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    },

    // Set button loading state
    setButtonLoading(buttonId, isLoading) {
        const button = document.getElementById(buttonId);
        const originalText = button.innerHTML;
        
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
            button.dataset.originalText = originalText;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || originalText;
        }
    },

    // Load and display logs
    async loadLogs() {
        try {
            const response = await fetch('/api/logs');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            
            const logContainer = document.getElementById('log-container');
            if (!logContainer) return;
            
            if (result.logs && result.logs.length > 0) {
                logContainer.innerHTML = result.logs.map(log => 
                    `<div class="log-entry">${this.escapeHtml(log)}</div>`
                ).join('');
            } else {
                logContainer.innerHTML = '<div class="text-muted">No logs available.</div>';
            }
            
            // Auto-scroll to bottom
            logContainer.scrollTop = logContainer.scrollHeight;
            
        } catch (error) {
            console.error('Error loading logs:', error);
            // Don't show error to user in demo mode
        }
    },

    // Clear logs
    clearLogs() {
        const logContainer = document.getElementById('log-container');
        logContainer.innerHTML = '<div class="text-muted">Logs cleared.</div>';
    },

    // Start auto-refresh
    startAutoRefresh() {
        if (this.state.refreshInterval) {
            clearInterval(this.state.refreshInterval);
        }
        
        this.state.refreshInterval = setInterval(() => {
            if (this.state.autoRefresh) {
                this.updateStatus();
                this.loadLogs();
            }
        }, 2000); // Refresh every 2 seconds
    },

    // Show notification toast
    showNotification(type, message) {
        const toast = document.getElementById('notification-toast');
        const toastMessage = document.getElementById('toast-message');
        const toastHeader = toast.querySelector('.toast-header');
        
        // Set message
        toastMessage.textContent = message;
        
        // Set toast style based on type
        toast.className = 'toast';
        toastHeader.className = 'toast-header';
        
        if (type === 'success') {
            toast.classList.add('bg-success', 'text-white');
            toastHeader.querySelector('i').className = 'fas fa-check-circle me-2';
        } else if (type === 'error') {
            toast.classList.add('bg-danger', 'text-white');
            toastHeader.querySelector('i').className = 'fas fa-exclamation-triangle me-2';
        } else if (type === 'warning') {
            toast.classList.add('bg-warning', 'text-dark');
            toastHeader.querySelector('i').className = 'fas fa-exclamation-triangle me-2';
        } else {
            toast.classList.add('bg-info', 'text-white');
            toastHeader.querySelector('i').className = 'fas fa-info-circle me-2';
        }
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    },

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    },

    // Screen Detection Functions
    bindScreenDetectionEvents() {
        // Screenshot controls
        const takeScreenshotBtn = document.getElementById('take-screenshot-btn');
        const detectElementsBtn = document.getElementById('detect-elements-btn');
        const saveClickBtn = document.getElementById('save-click-btn');
        const clearSelectionBtn = document.getElementById('clear-selection-btn');
        
        // Manual tap controls
        const manualTapBtn = document.getElementById('manual-tap-btn');
        
        // Template controls
        const createTemplateBtn = document.getElementById('create-template-btn');
        const findAndTapBtn = document.getElementById('find-and-tap-btn');
        
        if (takeScreenshotBtn) {
            takeScreenshotBtn.addEventListener('click', () => this.takeScreenshot());
        }
        if (detectElementsBtn) {
            detectElementsBtn.addEventListener('click', () => this.detectAndEnlarge());
        }
        if (saveClickBtn) {
            saveClickBtn.addEventListener('click', () => this.saveAndTap());
        }
        if (clearSelectionBtn) {
            clearSelectionBtn.addEventListener('click', () => this.clearSelection());
        }
        if (manualTapBtn) {
            manualTapBtn.addEventListener('click', () => this.manualTap());
        }
        if (createTemplateBtn) {
            createTemplateBtn.addEventListener('click', () => this.createTemplate());
        }
        if (findAndTapBtn) {
            findAndTapBtn.addEventListener('click', () => this.findAndTap());
        }
        
        // Initialize click selection state
        this.screenClickState = {
            selectedX: null,
            selectedY: null,
            imageElement: null,
            isEnlarged: false
        };
    },

    // Take screenshot from device
    async takeScreenshot() {
        this.setButtonLoading('take-screenshot-btn', true);
        
        try {
            const response = await fetch('/api/screenshot');
            const result = await response.json();
            
            if (result.success && result.screenshot) {
                const screenshotDisplay = document.getElementById('screenshot-display');
                screenshotDisplay.innerHTML = `
                    <img src="${result.screenshot}" class="img-fluid screenshot-image" style="max-width: 100%; height: auto; cursor: crosshair;" alt="Device Screenshot">
                `;
                
                // Enable detect button
                document.getElementById('detect-elements-btn').disabled = false;
                
                // Reset state
                this.clearSelection();
                this.screenClickState.isEnlarged = false;
                
                this.showNotification('success', 'Screenshot captured! Click "Detect & Enlarge" to continue');
            } else {
                this.showNotification('error', result.message || 'Failed to capture screenshot');
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('take-screenshot-btn', false);
        }
    },

    // Detect and enlarge image for clicking
    async detectAndEnlarge() {
        this.setButtonLoading('detect-elements-btn', true);
        
        try {
            // First detect elements
            const response = await fetch('/api/detect-elements');
            const result = await response.json();
            
            if (result.success) {
                const detections = result.detections;
                const detectionResults = document.getElementById('detection-results');
                const detectionInfo = document.getElementById('detection-info');
                
                // Show detection results
                if (detections.total_buttons > 0) {
                    let html = `<strong>พบปุ่มในหน้าจอ: ${detections.total_buttons} ปุ่ม</strong><br>`;
                    html += '<div class="mt-2"><small>คลิกบนรูปเพื่อเลือกจุดที่ต้องการกด:</small></div>';
                    
                    detections.buttons.slice(0, 5).forEach((button, index) => {
                        html += `<div class="badge bg-secondary me-1 mb-1">
                            ${index + 1}: (${button.x}, ${button.y})
                        </div>`;
                    });
                    
                    detectionInfo.innerHTML = html;
                } else {
                    detectionInfo.innerHTML = '<strong>Ready to click!</strong><br><small>คลิกบนรูปเพื่อเลือกจุดที่ต้องการกด</small>';
                }
                
                detectionResults.style.display = 'block';
                
                // Enlarge image and enable clicking
                this.enlargeImageForClicking();
                
                this.showNotification('success', 'Image enlarged! Click on the image to select tap position');
            } else {
                this.showNotification('error', result.message || 'Failed to detect elements');
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('detect-elements-btn', false);
        }
    },
    
    // Enlarge image for clicking
    enlargeImageForClicking() {
        const screenshotDisplay = document.getElementById('screenshot-display');
        const imageElement = screenshotDisplay.querySelector('img');
        
        if (!imageElement) {
            this.showNotification('error', 'No screenshot found');
            return;
        }
        
        // Store reference and mark as enlarged
        this.screenClickState.imageElement = imageElement;
        this.screenClickState.isEnlarged = true;
        
        // Make image larger and enable clicking
        imageElement.style.maxWidth = '90%';
        imageElement.style.height = 'auto';
        imageElement.classList.add('enlarged', 'clickable');
        
        // Add click event listener
        imageElement.addEventListener('click', (e) => this.handleImageClick(e));
        
        // Show coordinates display
        document.getElementById('coordinates-display').style.display = 'block';
        
        // Enable clear button
        document.getElementById('clear-selection-btn').disabled = false;
    },
    
    // Handle image click to select position
    handleImageClick(event) {
        const imageElement = event.target;
        const rect = imageElement.getBoundingClientRect();
        
        // Calculate click position relative to image
        const scaleX = imageElement.naturalWidth / imageElement.clientWidth;
        const scaleY = imageElement.naturalHeight / imageElement.clientHeight;
        
        const x = Math.round((event.clientX - rect.left) * scaleX);
        const y = Math.round((event.clientY - rect.top) * scaleY);
        
        // Store selected coordinates
        this.screenClickState.selectedX = x;
        this.screenClickState.selectedY = y;
        
        // Update display
        this.updateClickSelection(x, y, event.clientX - rect.left, event.clientY - rect.top);
        
        // Enable save button
        document.getElementById('save-click-btn').disabled = false;
        
        this.showNotification('info', `Selected position: (${x}, ${y})`);
    },
    
    // Update click selection visual indicator
    updateClickSelection(realX, realY, displayX, displayY) {
        const overlay = document.getElementById('click-overlay');
        const marker = document.getElementById('click-marker');
        const coordinates = document.getElementById('click-coordinates');
        const selectedCoordinates = document.getElementById('selected-coordinates');
        
        // Show overlay and marker
        overlay.style.display = 'block';
        marker.style.display = 'block';
        marker.style.left = displayX + 'px';
        marker.style.top = displayY + 'px';
        
        // Update coordinate display
        coordinates.textContent = `(${realX}, ${realY})`;
        selectedCoordinates.innerHTML = `<strong>X: ${realX}, Y: ${realY}</strong>`;
    },
    
    // Save and tap selected position
    async saveAndTap() {
        if (this.screenClickState.selectedX === null || this.screenClickState.selectedY === null) {
            this.showNotification('error', 'Please select a position on the image first');
            return;
        }
        
        this.setButtonLoading('save-click-btn', true);
        
        try {
            const response = await fetch('/api/tap-screen', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    x: this.screenClickState.selectedX, 
                    y: this.screenClickState.selectedY 
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', `Tapped at (${this.screenClickState.selectedX}, ${this.screenClickState.selectedY})`);
                
                // Add success effect to image
                if (this.screenClickState.imageElement) {
                    this.screenClickState.imageElement.classList.add('tap-success');
                    setTimeout(() => {
                        if (this.screenClickState.imageElement) {
                            this.screenClickState.imageElement.classList.remove('tap-success');
                        }
                    }, 1000);
                }
                
                // Reset for next action
                this.clearSelection();
                
                // Take new screenshot after a short delay
                setTimeout(() => {
                    this.takeScreenshot();
                }, 2000);
            } else {
                this.showNotification('error', result.message || 'Failed to tap screen');
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('save-click-btn', false);
        }
    },
    
    // Clear selection
    clearSelection() {
        // Reset state
        this.screenClickState.selectedX = null;
        this.screenClickState.selectedY = null;
        
        // Hide visual indicators
        const overlay = document.getElementById('click-overlay');
        const marker = document.getElementById('click-marker');
        const coordinatesDisplay = document.getElementById('coordinates-display');
        const selectedCoordinates = document.getElementById('selected-coordinates');
        
        overlay.style.display = 'none';
        marker.style.display = 'none';
        coordinatesDisplay.style.display = 'none';
        selectedCoordinates.textContent = 'Click on the image to select a position';
        
        // Disable buttons
        document.getElementById('save-click-btn').disabled = true;
        document.getElementById('clear-selection-btn').disabled = true;
        
        // Remove CSS classes from image if enlarged
        if (this.screenClickState.imageElement && this.screenClickState.isEnlarged) {
            this.screenClickState.imageElement.classList.remove('enlarged', 'clickable');
            this.screenClickState.isEnlarged = false;
        }
    },

    // Manual tap screen
    async manualTap() {
        const x = parseInt(document.getElementById('tap-x').value) || 0;
        const y = parseInt(document.getElementById('tap-y').value) || 0;
        
        this.setButtonLoading('manual-tap-btn', true);
        
        try {
            const response = await fetch('/api/tap-screen', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ x, y })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', `Tapped at (${x}, ${y})`);
            } else {
                this.showNotification('error', result.message || 'Failed to tap screen');
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('manual-tap-btn', false);
        }
    },

    // Create template from screenshot
    async createTemplate() {
        const name = document.getElementById('template-name').value.trim();
        const x = parseInt(document.getElementById('template-x').value) || 0;
        const y = parseInt(document.getElementById('template-y').value) || 0;
        const width = parseInt(document.getElementById('template-width').value) || 50;
        const height = parseInt(document.getElementById('template-height').value) || 50;
        
        if (!name) {
            this.showNotification('error', 'Please enter a template name');
            return;
        }
        
        this.setButtonLoading('create-template-btn', true);
        
        try {
            const response = await fetch('/api/create-template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, x, y, width, height })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', `Template "${name}" created successfully`);
                // Clear the form
                document.getElementById('template-name').value = '';
            } else {
                this.showNotification('error', result.message || 'Failed to create template');
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('create-template-btn', false);
        }
    },

    // Find template and tap
    async findAndTap() {
        const templateName = document.getElementById('find-template-name').value.trim();
        const threshold = parseFloat(document.getElementById('template-threshold').value) || 0.8;
        
        if (!templateName) {
            this.showNotification('error', 'Please enter a template name');
            return;
        }
        
        this.setButtonLoading('find-and-tap-btn', true);
        
        try {
            const response = await fetch('/api/find-and-tap', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ template_name: templateName, threshold })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', `Found and tapped "${templateName}"`);
            } else {
                this.showNotification('warning', result.message || `Template "${templateName}" not found`);
            }
        } catch (error) {
            this.showNotification('error', 'Network error: ' + error.message);
        } finally {
            this.setButtonLoading('find-and-tap-btn', false);
        }
    }
};

// Initialize app when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}
