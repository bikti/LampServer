class SerialController {
    constructor() {
        this.port = null;
        this.reader = null;
        this.writer = null;
        this.connected = false;
        this.keepReading = true;
        
        this.terminal = document.getElementById('terminal');
        this.connectBtn = document.getElementById('connect-btn');
        this.disconnectBtn = document.getElementById('disconnect-btn');
        this.refreshBtn = document.getElementById('refresh-btn');
        this.sendBtn = document.getElementById('send-btn');
        this.inputData = document.getElementById('input-data');
        this.statusIndicator = document.getElementById('status');
        this.baudRateSelect = document.getElementById('baud-rate');
        this.portsContainer = document.getElementById('ports-container');
        
        this.setupEventListeners();
        this.checkSupportedState();
        this.refreshPorts();
    }
    
    // Проверка поддержки Web Serial API
    checkSupportedState() {
        if (!('serial' in navigator)) {
            this.logError('Web Serial API не поддерживается в вашем браузере. Пожалуйста, используйте Chrome, Edge или Opera.');
            this.connectBtn.disabled = true;
            this.refreshBtn.disabled = true;
        }
    }
    
    // Настройка обработчиков событий
    setupEventListeners() {
        this.connectBtn.addEventListener('click', () => this.connect());
        this.disconnectBtn.addEventListener('click', () => this.disconnect());
        this.refreshBtn.addEventListener('click', () => this.refreshPorts());
        this.sendBtn.addEventListener('click', () => this.sendData());
        
        this.inputData.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendData();
            }
        });
    }
    
    // Обновление списка портов
    async refreshPorts() {
        if (!('serial' in navigator)) return;
        
        try {
            // Получаем порты, к которым уже был предоставлен доступ
            const ports = await navigator.serial.getPorts();
            this.displayPorts(ports);
            
            // Также слушаем события подключения/отключения устройств
            navigator.serial.addEventListener('connect', (e) => {
                this.logInfo(`Устройство подключено: ${e.target.getInfo()}`);
                this.refreshPorts();
            });
            
            navigator.serial.addEventListener('disconnect', (e) => {
                this.logInfo(`Устройство отключено: ${e.target.getInfo()}`);
                this.refreshPorts();
            });
        } catch (error) {
            this.logError(`Ошибка при получении портов: ${error.message}`);
        }
    }
    
    // Отображение списка портов
    displayPorts(ports) {
        this.portsContainer.innerHTML = '';
        
        if (ports.length === 0) {
            this.portsContainer.innerHTML = '<p>Устройства не найдены</p>';
            return;
        }
        
        ports.forEach(port => {
            const portElement = document.createElement('div');
            portElement.className = 'port-item';
            portElement.textContent = this.getPortDisplayName(port);
            portElement.addEventListener('click', () => this.selectPort(port));
            this.portsContainer.appendChild(portElement);
        });
    }
    
    // Форматирование имени порта для отображения
    getPortDisplayName(port) {
        const info = port.getInfo();
        return info.usbProductId ? 
            `Производитель: 0x${info.usbVendorId.toString(16)}, Продукт: 0x${info.usbProductId.toString(16)}` : 
            `Порт: ${info.path}`;
    }
    
    // Выбор порта для подключения
    selectPort(selectedPort) {
        this.port = selectedPort;
        this.logInfo(`Выбран порт: ${this.getPortDisplayName(selectedPort)}`);
    }
    
    // Подключение к выбранному порту
    async connect() {
        if (!('serial' in navigator)) return;
        
        try {
            // Если порт не выбран, запросим у пользователя
            if (!this.port) {
                const filters = [
                    { usbVendorId: 0x2341 },  // Arduino
                    { usbVendorId: 0x0403 },  // FTDI
                    { usbVendorId: 0x067B }   // Prolific
                ];
                
                this.port = await navigator.serial.requestPort({ filters });
            }
            
            const baudRate = parseInt(this.baudRateSelect.value);
            
            // Открываем порт с выбранной скоростью
            await this.port.open({ baudRate });
            
            this.logInfo(`Подключено к порту на скорости ${baudRate} бод`);
            this.setConnectedState(true);
            
            // Начинаем чтение данных
            this.readData();
            
        } catch (error) {
            this.logError(`Ошибка подключения: ${error.message}`);
        }
    }
    
    // Установка состояния подключения
    setConnectedState(connected) {
        this.connected = connected;
        this.connectBtn.disabled = connected;
        this.disconnectBtn.disabled = !connected;
        this.sendBtn.disabled = !connected;
        this.inputData.disabled = !connected;
        
        if (connected) {
            this.statusIndicator.classList.add('connected');
            this.statusIndicator.querySelector('span').textContent = 'Подключено';
        } else {
            this.statusIndicator.classList.remove('connected');
            this.statusIndicator.querySelector('span').textContent = 'Не подключено';
        }
    }
    
    // Чтение данных из порта
    async readData() {
        if (!this.port || !this.port.readable) return;
        
        const decoder = new TextDecoderStream();
        const readableStreamClosed = this.port.readable.pipeTo(decoder.writable);
        const reader = decoder.readable.getReader();
        
        this.keepReading = true;
        
        try {
            while (this.keepReading) {
                const { value, done } = await reader.read();
                if (done) {
                    reader.releaseLock();
                    break;
                }
                
                // Выводим полученные данные в терминал
                this.logIncoming(value);
            }
        } catch (error) {
            this.logError(`Ошибка чтения: ${error.message}`);
        } finally {
            reader.releaseLock();
        }
    }
    
    // Отправка данных в порт
    async sendData() {
        if (!this.port || !this.port.writable || !this.inputData.value) return;
        
        try {
            const encoder = new TextEncoder();
            const data = encoder.encode(this.inputData.value + '\n');
            
            this.writer = this.port.writable.getWriter();
            await this.writer.write(data);
            await this.writer.releaseLock();
            
            this.logOutgoing(this.inputData.value);
            this.inputData.value = '';
            
        } catch (error) {
            this.logError(`Ошибка отправки: ${error.message}`);
        }
    }
    
    // Отключение от порта
    async disconnect() {
        this.keepReading = false;
        
        if (this.reader) {
            await this.reader.cancel();
        }
        
        if (this.port) {
            try {
                await this.port.close();
                this.logInfo('Отключено от порта');
            } catch (error) {
                this.logError(`Ошибка при отключении: ${error.message}`);
            }
        }
        
        this.setConnectedState(false);
        this.port = null;
        this.reader = null;
        this.writer = null;
    }
    
    // Логирование входящих данных
    logIncoming(data) {
        this.appendToTerminal(data, 'incoming');
    }
    
    // Логирование исходящих данных
    logOutgoing(data) {
        this.appendToTerminal(data, 'outgoing');
    }
    
    // Логирование информационных сообщений
    logInfo(message) {
        this.appendToTerminal(message, 'info');
    }
    
    // Логирование ошибок
    logError(message) {
        this.appendToTerminal(message, 'error');
    }
    
    // Добавление сообщения в терминал
    appendToTerminal(message, className) {
        const line = document.createElement('div');
        line.className = className;
        line.textContent = `> ${new Date().toLocaleTimeString()}: ${message}`;
        this.terminal.appendChild(line);
        
        // Автопрокрутка к последнему сообщению
        this.terminal.scrollTop = this.terminal.scrollHeight;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const serialController = new SerialController();
});