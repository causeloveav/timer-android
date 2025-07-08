from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from datetime import datetime
import os
import random

# Импорты для уведомлений и звука
try:
    from plyer import notification
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    android_available = True
except ImportError:
    android_available = False

class Card(FloatLayout):
    """Карточка с современным дизайном"""
    def __init__(self, bg_color=(0.98, 0.98, 0.98, 1), dark_bg_color=(0.15, 0.15, 0.15, 1), 
                 elevation=2, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.dark_bg_color = dark_bg_color
        self.elevation = elevation
        self.is_dark_theme = False
        
        with self.canvas.before:
            self.color = Color(*bg_color)
            self.rect = RoundedRectangle(radius=[dp(12)] * 4)
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.rect.pos = (self.pos[0] + dp(2), self.pos[1] - dp(2))
        self.rect.size = self.size
    
    def set_theme(self, is_dark):
        self.is_dark_theme = is_dark
        color = self.dark_bg_color if is_dark else self.bg_color
        self.color.rgba = color

class ModernButton(Button):
    """Современная кнопка с анимацией"""
    def __init__(self, button_type='primary', **kwargs):
        super().__init__(**kwargs)
        self.button_type = button_type
        self.is_dark_theme = False
        self.original_size = None
        
        # Настройка стилей по типу кнопки
        if button_type == 'primary':
            self.bg_color = (0.2, 0.6, 1, 1)  # Синий
            self.text_color = (1, 1, 1, 1)
        elif button_type == 'success':
            self.bg_color = (0.2, 0.8, 0.4, 1)  # Зеленый
            self.text_color = (1, 1, 1, 1)
        elif button_type == 'danger':
            self.bg_color = (0.9, 0.3, 0.3, 1)  # Красный
            self.text_color = (1, 1, 1, 1)
        else:  # secondary
            self.bg_color = (0.9, 0.9, 0.9, 1)  # Серый
            self.text_color = (0.2, 0.2, 0.2, 1)
        
        self.background_color = self.bg_color
        self.color = self.text_color
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)
    
    def on_button_press(self, instance):
        """Анимация нажатия"""
        if not self.original_size:
            self.original_size = self.size[:]
        
        anim = Animation(size=(self.size[0] * 0.95, self.size[1] * 0.95), 
                        duration=0.1, t='out_quad')
        anim.start(self)
    
    def on_button_release(self, instance):
        """Анимация отпускания"""
        if self.original_size:
            anim = Animation(size=self.original_size, duration=0.1, t='out_quad')
            anim.start(self)

class TimerDisplay(Label):
    """Современный дисплей таймера с анимацией"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pulse_animation = None
    
    def start_pulse(self):
        """Запускает пульсирующую анимацию"""
        if self.pulse_animation:
            self.pulse_animation.cancel(self)
        
        self.pulse_animation = Animation(font_size='72sp', duration=0.5) + \
                              Animation(font_size='64sp', duration=0.5)
        self.pulse_animation.repeat = True
        self.pulse_animation.start(self)
    
    def stop_pulse(self):
        """Останавливает анимацию"""
        if self.pulse_animation:
            self.pulse_animation.cancel(self)
            self.font_size = '64sp'

class TimerApp(App):
    def build(self):
        self.title = "Focus Timer 2025"
        
        # Переменные
        self.time_left = 0
        self.timer_running = False
        self.start_time = None
        self.log_file = "activity_log.txt"
        self.is_dark_theme = True  # По умолчанию тёмная тема
        self.user_name = "Пользователь"  # Персонализация
        
        # Мотивационные сообщения
        self.motivational_messages = [
            "Отличная работа! Продолжайте в том же духе! 🌟",
            "Вы на правильном пути к достижению целей! 💪",
            "Каждая минута приближает вас к успеху! 🚀",
            "Ваш прогресс впечатляет! 🎯",
            "Сосредоточенность - ключ к продуктивности! ⚡",
            "Вы создаете отличные привычки! 🌱"
        ]
        
        # Запрашиваем разрешения
        if android_available:
            self.request_android_permissions()
        
        # Основной контейнер
        main_container = ScrollView()
        
        # Главный layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), 
                               spacing=dp(16), size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Шапка с приветствием и переключателем темы
        header_card = Card(size_hint=(1, None), height=dp(80))
        header_layout = BoxLayout(orientation='horizontal', padding=dp(16))
        
        # Приветствие
        self.greeting_label = Label(
            text=f"Привет, {self.user_name}! Готовы к фокусировке?",
            font_size='16sp',
            color=(1, 1, 1, 1) if self.is_dark_theme else (0.2, 0.2, 0.2, 1),
            text_size=(None, None),
            halign='left',
            size_hint_x=0.8
        )
        header_layout.add_widget(self.greeting_label)
        
        # Переключатель темы
        self.theme_button = ModernButton(
            text='☀️' if self.is_dark_theme else '🌙',
            size_hint=(None, None),
            size=(dp(60), dp(48)),
            font_size='20sp'
        )
        self.theme_button.bind(on_press=self.toggle_theme)
        header_layout.add_widget(self.theme_button)
        
        header_card.add_widget(header_layout)
        main_layout.add_widget(header_card)
        
        # Карточка таймера
        timer_card = Card(size_hint=(1, None), height=dp(280))
        timer_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        
        # Заголовок таймера
        timer_title = Label(
            text='ФОКУС-ТАЙМЕР',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1) if self.is_dark_theme else (0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(30)
        )
        timer_layout.add_widget(timer_title)
        
        # Ввод времени с лейблом
        time_input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        time_label = Label(
            text='Минуты:',
            font_size='16sp',
            size_hint_x=0.4,
            color=(1, 1, 1, 1) if self.is_dark_theme else (0.2, 0.2, 0.2, 1)
        )
        time_input_layout.add_widget(time_label)
        
        self.time_input = TextInput(
            text='25',
            multiline=False,
            font_size='18sp',
            size_hint_x=0.6,
            size_hint_y=None,
            height=dp(50),
            input_filter='int',
            background_color=(0.2, 0.2, 0.2, 1) if self.is_dark_theme else (0.95, 0.95, 0.95, 1)
        )
        time_input_layout.add_widget(self.time_input)
        timer_layout.add_widget(time_input_layout)
        
        # Дисплей времени
        self.time_display = TimerDisplay(
            text='00:00',
            font_size='64sp',
            bold=True,
            color=(0.3, 0.7, 1, 1),  # Яркий синий
            size_hint_y=None,
            height=dp(100)
        )
        timer_layout.add_widget(self.time_display)
        
        # Кнопки управления таймером
        timer_buttons = GridLayout(cols=3, size_hint_y=None, height=dp(60), spacing=dp(12))
        
        self.start_button = ModernButton(
            text='СТАРТ',
            font_size='16sp',
            button_type='success',
            bold=True
        )
        self.start_button.bind(on_press=self.start_timer)
        timer_buttons.add_widget(self.start_button)
        
        self.stop_button = ModernButton(
            text='СТОП',
            font_size='16sp',
            button_type='danger',
            disabled=True,
            bold=True
        )
        self.stop_button.bind(on_press=self.stop_timer)
        timer_buttons.add_widget(self.stop_button)
        
        reset_button = ModernButton(
            text='СБРОС',
            font_size='16sp',
            button_type='secondary',
            bold=True
        )
        reset_button.bind(on_press=self.reset_timer)
        timer_buttons.add_widget(reset_button)
        
        timer_layout.add_widget(timer_buttons)
        timer_card.add_widget(timer_layout)
        main_layout.add_widget(timer_card)
        
        # Карточка активности
        activity_card = Card(size_hint=(1, None), height=dp(200))
        activity_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        activity_title = Label(
            text='ВАША АКТИВНОСТЬ',
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1) if self.is_dark_theme else (0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(30)
        )
        activity_layout.add_widget(activity_title)
        
        self.activity_input = TextInput(
            multiline=True,
            font_size='14sp',
            size_hint_y=None,
            height=dp(80),
            hint_text='Опишите, чем занимались во время фокус-сессии...',
            background_color=(0.2, 0.2, 0.2, 1) if self.is_dark_theme else (0.95, 0.95, 0.95, 1)
        )
        self.activity_input.bind(focus=self.on_activity_focus)
        activity_layout.add_widget(self.activity_input)
        
        self.save_button = ModernButton(
            text='СОХРАНИТЬ ПРОГРЕСС',
            font_size='16sp',
            button_type='primary',
            size_hint_y=None,
            height=dp(50),
            disabled=True,
            bold=True
        )
        self.save_button.bind(on_press=self.save_activity)
        activity_layout.add_widget(self.save_button)
        
        activity_card.add_widget(activity_layout)
        main_layout.add_widget(activity_card)
        
        # Карточка управления логом
        log_card = Card(size_hint=(1, None), height=dp(120))
        log_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        log_title = Label(
            text='ИСТОРИЯ ДОСТИЖЕНИЙ',
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1) if self.is_dark_theme else (0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(30)
        )
        log_layout.add_widget(log_title)
        
        log_buttons = GridLayout(cols=2, size_hint_y=None, height=dp(50), spacing=dp(12))
        
        view_log_button = ModernButton(
            text='ПОСМОТРЕТЬ',
            font_size='14sp',
            button_type='primary'
        )
        view_log_button.bind(on_press=self.view_log)
        log_buttons.add_widget(view_log_button)
        
        clear_log_button = ModernButton(
            text='ОЧИСТИТЬ',
            font_size='14sp',
            button_type='secondary'
        )
        clear_log_button.bind(on_press=self.clear_log)
        log_buttons.add_widget(clear_log_button)
        
        log_layout.add_widget(log_buttons)
        log_card.add_widget(log_layout)
        main_layout.add_widget(log_card)
        
        # Статус с эмоциональными сообщениями
        self.status_label = Label(
            text='✨ Готовы начать продуктивную сессию?',
            font_size='14sp',
            color=(0.3, 0.7, 1, 1),
            size_hint_y=None,
            height=dp(40),
            text_size=(None, None),
            halign='center'
        )
        main_layout.add_widget(self.status_label)
        
        # Пространство для клавиатуры
        spacer = Widget(size_hint_y=None, height=dp(100))
        main_layout.add_widget(spacer)
        
        main_container.add_widget(main_layout)
        
        # Настраиваем тему
        self.apply_theme()
        
        # Сохраняем ссылки на карточки для смены темы
        self.cards = [header_card, timer_card, activity_card, log_card]
        
        return main_container
    
    def toggle_theme(self, instance):
        """Переключение темы"""
        self.is_dark_theme = not self.is_dark_theme
        self.theme_button.text = '☀️' if self.is_dark_theme else '🌙'
        self.apply_theme()
        
        # Анимация смены темы
        for card in self.cards:
            card.set_theme(self.is_dark_theme)
    
    def apply_theme(self):
        """Применяет текущую тему"""
        if self.is_dark_theme:
            Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Тёмный фон
            text_color = (1, 1, 1, 1)
        else:
            Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Светлый фон
            text_color = (0.2, 0.2, 0.2, 1)
        
        # Обновляем цвета текста
        if hasattr(self, 'greeting_label'):
            self.greeting_label.color = text_color
    
    def on_activity_focus(self, instance, value):
        """Прокрутка при фокусе на поле активности"""
        if value:
            Clock.schedule_once(lambda dt: self.scroll_to_input(), 0.3)
    
    def scroll_to_input(self):
        """Прокрутка к полю ввода"""
        try:
            main_scroll = self.root
            main_scroll.scroll_y = 0
        except:
            pass
    
    def request_android_permissions(self):
        """Запрос разрешений Android"""
        if android_available:
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.VIBRATE,
                Permission.WAKE_LOCK,
                Permission.FOREGROUND_SERVICE
            ])
    
    def on_pause(self):
        """Работа в фоне"""
        if self.timer_running:
            self.show_notification(
                "🔥 Фокус-сессия активна",
                f"Продолжаем концентрацию! Осталось: {self.time_left // 60:02d}:{self.time_left % 60:02d}"
            )
        return True
    
    def start_timer(self, instance):
        try:
            minutes = int(self.time_input.text)
            if minutes <= 0:
                self.show_status_message("⚠️ Время должно быть положительным", error=True)
                return
                
            self.time_left = minutes * 60
            self.timer_running = True
            self.start_time = datetime.now()
            
            # Анимация запуска
            self.time_display.start_pulse()
            
            # Обновляем интерфейс
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.time_input.readonly = True
            
            # Мотивационное сообщение
            self.show_status_message("🚀 Фокус-сессия началась! Время продуктивности!")
            
            # Уведомление
            self.show_notification(
                "🎯 Фокус-режим активирован",
                f"Сессия на {minutes} минут началась. Удачной концентрации!"
            )
            
            # Запускаем таймер
            Clock.schedule_interval(self.update_timer, 1)
            
        except ValueError:
            self.show_status_message("❌ Введите корректное число", error=True)
    
    def update_timer(self, dt):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.time_display.text = f"{minutes:02d}:{seconds:02d}"
            
            # Изменяем цвет по времени
            if self.time_left <= 60:
                self.time_display.color = (1, 0.3, 0.3, 1)  # Красный
            elif self.time_left <= 300:
                self.time_display.color = (1, 0.6, 0.2, 1)  # Оранжевый
            else:
                self.time_display.color = (0.3, 0.7, 1, 1)  # Синий
            
            if self.time_left <= 0:
                self.timer_finished()
                
        return self.timer_running
    
    def timer_finished(self):
        self.timer_running = False
        self.time_display.text = "00:00"
        self.time_display.color = (0.2, 0.8, 0.4, 1)  # Зеленый - успех
        self.time_display.stop_pulse()
        
        # Эмоциональное сообщение
        self.show_status_message("🎉 Поздравляем! Сессия завершена успешно!")
        
        # Уведомление с мотивацией
        motivational_msg = random.choice(self.motivational_messages)
        self.show_notification(
            "✅ Фокус-сессия завершена!",
            motivational_msg,
            urgent=True
        )
        
        # Звук и вибрация
        self.play_notification_sound()
        
        # Интерфейс
        self.save_button.disabled = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.activity_input.focus = True
        
        Clock.unschedule(self.update_timer)
    
    def show_status_message(self, message, error=False):
        """Показывает статусное сообщение с анимацией"""
        if error:
            self.status_label.color = (1, 0.3, 0.3, 1)
        else:
            self.status_label.color = (0.3, 0.7, 1, 1)
        
        self.status_label.text = message
        
        # Анимация появления
        anim = Animation(opacity=0, duration=0.1) + Animation(opacity=1, duration=0.3)
        anim.start(self.status_label)
    
    def show_notification(self, title, message, urgent=False):
        """Уведомления Android"""
        if android_available:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Focus Timer",
                    timeout=10 if not urgent else 0,
                    toast=urgent
                )
            except Exception as e:
                print(f"Ошибка уведомления: {e}")
    
    def play_notification_sound(self):
        """Звук и вибрация"""
        if android_available:
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                
                RingtoneManager = autoclass('android.media.RingtoneManager')
                notification_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
                ringtone = RingtoneManager.getRingtone(context, notification_uri)
                
                if ringtone:
                    ringtone.play()
                
                # Вибрация
                vibrator = context.getSystemService(context.VIBRATOR_SERVICE)
                if vibrator and vibrator.hasVibrator():
                    vibrator.vibrate(1000)
                    
            except Exception as e:
                print(f"Ошибка звука: {e}")
    
    def stop_timer(self, instance):
        self.timer_running = False
        self.time_display.stop_pulse()
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.show_status_message("⏸️ Сессия приостановлена. Готовы продолжить?")
        Clock.unschedule(self.update_timer)
    
    def reset_timer(self, instance):
        self.timer_running = False
        self.time_left = 0
        self.time_display.text = "00:00"
        self.time_display.color = (0.3, 0.7, 1, 1)
        self.time_display.stop_pulse()
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.save_button.disabled = True
        self.activity_input.text = ""
        self.show_status_message("🔄 Готовы к новой продуктивной сессии?")
        Clock.unschedule(self.update_timer)
    
    def save_activity(self, instance):
        activity = self.activity_input.text.strip()
        if not activity:
            self.show_status_message("💭 Поделитесь своими достижениями!", error=True)
            return
        
        try:
            duration_minutes = int(self.time_input.text)
            end_time = datetime.now()
            
            if not os.path.exists(self.log_file):
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("🏆 ЖУРНАЛ ДОСТИЖЕНИЙ И ПРОДУКТИВНОСТИ 🏆\n\n")
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(
                    f"📅 {self.start_time:%Y-%m-%d %H:%M:%S} → "
                    f"{end_time:%Y-%m-%d %H:%M:%S}\n"
                    f"⏱️ Фокус-время: {duration_minutes} минут\n"
                    f"🎯 Достижение: {activity}\n"
                    f"{'=' * 50}\n\n"
                )
            
            # Мотивационное сообщение
            success_msg = random.choice(self.motivational_messages)
            self.show_status_message(f"💾 {success_msg}")
            
            self.save_button.disabled = True
            self.activity_input.text = ""
            
            # Анимация успеха
            anim = Animation(size=(self.save_button.size[0] * 1.1, self.save_button.size[1] * 1.1), 
                           duration=0.2) + \
                   Animation(size=self.save_button.size, duration=0.2)
            anim.start(self.save_button)
            
            self.show_notification(
                "🎉 Прогресс сохранён!",
                f"Отличная работа! Записано: {activity}"
            )
            
        except Exception as e:
            self.show_status_message(f"❌ Ошибка сохранения: {e}", error=True)
    
    def view_log(self, instance):
        """Современный просмотр лога"""
        try:
            if not os.path.exists(self.log_file):
                content_text = "📝 Ваш журнал достижений пока пуст.\n\n🚀 Начните фокус-сессию, чтобы записать свой первый успех!"
            else:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    content_text = f.read()
                    if not content_text.strip():
                        content_text = "📝 Ваш журнал достижений пока пуст.\n\n🚀 Начните фокус-сессию, чтобы записать свой первый успех!"
        except Exception as e:
            content_text = f"❌ Ошибка чтения журнала: {e}"
        
        # Современный popup
        content = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(20))
        
        title_label = Label(
            text='🏆 ЖУРНАЛ ДОСТИЖЕНИЙ',
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=dp(50),
            color=(0.3, 0.7, 1, 1)
        )
        content.add_widget(title_label)
        
        scroll = ScrollView()
        log_label = Label(
            text=content_text,
            font_size='14sp',
            text_size=(None, None),
            halign='left',
            valign='top',
            color=(1, 1, 1, 1) if self.is_dark_theme else (0.2, 0.2, 0.2, 1)
        )
        scroll.add_widget(log_label)
        content.add_widget(scroll)
        
        close_button = ModernButton(
            text='ЗАКРЫТЬ',
            font_size='16sp',
            button_type='primary',
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(close_button)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False,
            background_color=(0.15, 0.15, 0.15, 0.9) if self.is_dark_theme else (0.95, 0.95, 0.95, 0.9)
        )
        
        close_button.bind(on_press=popup.dismiss)
        
        def update_text_size(instance, value):
            log_label.text_size = (value[0] - dp(40), None)
        
        popup.bind(size=update_text_size)
        popup.open()
    
    def clear_log(self, instance):
        """Современное подтверждение очистки"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        message = Label(
            text='🗑️ ОЧИСТКА ЖУРНАЛА\n\nВы уверены, что хотите удалить все записи достижений?\n\n⚠️ Это действие нельзя отменить.',
            font_size='16sp',
            text_size=(None, None),
            halign='center',
            color=(1, 1, 1, 1) if self.is_dark_theme else (0.2, 0.2, 0.2, 1)
        )
        content.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=dp(50))
        
        yes_button = ModernButton(text='УДАЛИТЬ', font_size='14sp', button_type='danger')
        no_button = ModernButton(text='ОТМЕНА', font_size='14sp', button_type='secondary')
        
        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)
        content.add_widget(buttons)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False,
            background_color=(0.15, 0.15, 0.15, 0.9) if self.is_dark_theme else (0.95, 0.95, 0.95, 0.9)
        )
        
        def confirm_clear(instance):
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("🏆 ЖУРНАЛ ДОСТИЖЕНИЙ И ПРОДУКТИВНОСТИ 🏆\n\n")
                self.show_status_message("🗑️ Журнал очищен. Готовы к новым достижениям!")
            except Exception as e:
                self.show_status_message(f"❌ Ошибка очистки: {e}", error=True)
            popup.dismiss()
        
        yes_button.bind(on_press=confirm_clear)
        no_button.bind(on_press=popup.dismiss)
        
        popup.open()

if __name__ == '__main__':
    TimerApp().run()
