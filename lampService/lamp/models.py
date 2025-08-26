from django.db import models
from django.core.validators import MinLengthValidator
import uuid

class Device(models.Model):
    # Статусы устройства
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
    ]
    
    # Типы устройств
    TYPE_CHOICES = [
        ('lamp', 'Lamp'),
        ('sensor', 'Sensor'),
        ('switch', 'Switch'),
        ('controller', 'Controller'),
        ('other', 'Other'),
    ]
    
    # Уникальный идентификатор
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Основная информация из MQTT
    name = models.CharField(
        max_length=100,
        verbose_name='Device Name',
        help_text='Название устройства'
    )
    model = models.CharField(
        max_length=100,
        verbose_name='Device Model',
        help_text='Модель устройства'
    )
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(3)],
        verbose_name='Serial Number',
        help_text='Серийный номер устройства',
        db_index=True  # Индекс для быстрого поиска
    )
    
    # Дополнительная информация
    device_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='other',
        verbose_name='Device Type',
        help_text='Тип устройства'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline',
        verbose_name='Status',
        help_text='Текущий статус устройства'
    )
    firmware_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Firmware Version',
        help_text='Версия прошивки'
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='IP Address',
        help_text='IP адрес устройства'
    )
    
    # MQTT информация
    mqtt_topic = models.CharField(
        max_length=200,
        verbose_name='MQTT Topic',
        help_text='Топик MQTT для устройства'
    )
    last_message_received = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Last Message',
        help_text='Время получения последнего сообщения'
    )
    
    # Системные поля
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        help_text='Время создания записи'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
        help_text='Время последнего обновления'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active',
        help_text='Активно ли устройство'
    )
    
    # Связи (если нужно)
    # location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True)
    # group = models.ForeignKey('DeviceGroup', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
            models.Index(fields=['device_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.serial_number}) - {self.get_status_display()}"
    
    @property
    def is_online(self):
        return self.status == 'online'
    
    def update_status(self, new_status, save=True):
        """Обновление статуса устройства"""
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            if save:
                self.save()
    
    def mark_online(self, save=True):
        """Пометить устройство как онлайн"""
        self.update_status('online', save)
    
    def mark_offline(self, save=True):
        """Пометить устройство как оффлайн"""
        self.update_status('offline', save)