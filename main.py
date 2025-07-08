from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from datetime import datetime
import os

# Импорты для уведомлений и звука
try:
    from plyer import notification
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    android_available = True
except ImportError:
    android_available = False

class TimerApp(App):
    def build(self):
        self.title = "Таймер для Android"
        
        # Переменные
        self.time_left = 0
        self.timer_running = False
        self.start_time = None
        self.log_file = "activity_log.txt"
        self.keyboard_height = 0
        
        # Запрашиваем разрешения при запуске
        if android_available:
            self.request_android_permissions()
            self.setup_background_service()
        
        # Основной ScrollView для решения проблемы с клавиатурой
        main_scroll = ScrollView()
        
        # Основной layout для вертикальной ориентации
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Заголовок
        title = Label(
            text='ТАЙМЕР АКТИВНОСТИ', 
            font_size='24sp', 
            size_hint_y=None, 
            height='60dp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Секция ввода времени - СДЕЛАНО КОРОЧЕ
        time_section = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        time_section.add_widget(Label(text='Время (мин):', font_size='16sp', size_hint_x=0.6))
        self.time_input = TextInput(
            text='25', 
            multiline=False, 
            font_size='16sp',
            size_hint_x=0.4,  # Сделано меньше (было 0.6)
            input_filter='int'
        )
        time_section.add_widget(self.time_input)
        main_layout.add_widget(time_section)
        
        # Отображение времени
        self.time_display = Label(
            text='00:00', 
            font_size='64sp', 
            size_hint_y=None, 
            height='120dp',
            bold=True,
            color=[0.2, 0.6, 1, 1]
        )
        main_layout.add_widget(self.time_display)
        
        # Кнопки управления таймером - БЕЗ ИКОНОК
        timer_buttons = GridLayout(cols=3, size_hint_y=None, height='60dp', spacing=10)
        
        self.start_button = Button(text='СТАРТ', font_size='14sp')  # Убрана иконка ▶
        self.start_button.bind(on_press=self.start_timer)
        timer_buttons.add_widget(self.start_button)
        
        self.stop_button = Button(text='СТОП', font_size='14sp', disabled=True)  # Убрана иконка ⏸
        self.stop_button.bind(on_press=self.stop_timer)
        timer_buttons.add_widget(self.stop_button)
        
        reset_button = Button(text='СБРОС', font_size='14sp')  # Убрана иконка 🔄
        reset_button.bind(on_press=self.reset_timer)
        timer_buttons.add_widget(reset_button)
        
        main_layout.add_widget(timer_buttons)
        
        # Разделитель
        main_layout.add_widget(Label(text='', size_hint_y=None, height='20dp'))
        
        # Секция активности
        activity_label = Label(
            text='Чем занимались:', 
            font_size='16sp', 
            size_hint_y=None, 
            height='30dp',
            text_size=(None, None),
            halign='left'
        )
        main_layout.add_widget(activity_label)
        
        # Поле ввода активности с обработкой клавиатуры
        self.activity_input = TextInput(
            multiline=True, 
            font_size='14sp',
            size_hint_y=None,
            height='80dp',
            hint_text='Опишите свою активность...'
        )
        # Привязываем события фокуса для обработки клавиатуры
        self.activity_input.bind(focus=self.on_activity_focus)
        main_layout.add_widget(self.activity_input)
        
        # Кнопка сохранения активности - БЕЗ ИКОНКИ
        self.save_button = Button(
            text='СОХРАНИТЬ АКТИВНОСТЬ',  # Убрана иконка 💾
            font_size='16sp',
            size_hint_y=None, 
            height='50dp', 
            disabled=True
        )
        self.save_button.bind(on_press=self.save_activity)
        main_layout.add_widget(self.save_button)
        
        # Разделитель
        main_layout.add_widget(Label(text='', size_hint_y=None, height='15dp'))
        
        # Кнопки управления логом - БЕЗ ИКОНОК
        log_buttons = GridLayout(cols=2, size_hint_y=None, height='50dp', spacing=10)
        
        view_log_button = Button(text='ПОСМОТРЕТЬ ЛОГ', font_size='14sp')  # Убрана иконка 📋
        view_log_button.bind(on_press=self.view_log)
        log_buttons.add_widget(view_log_button)
        
        clear_log_button = Button(text='ОЧИСТИТЬ ЛОГ', font_size='14sp')  # Убрана иконка 🗑️
        clear_log_button.bind(on_press=self.clear_log)
        log_buttons.add_widget(clear_log_button)
        
        main_layout.add_widget(log_buttons)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе', 
            font_size='14sp',
            size_hint_y=None, 
            height='40dp',
            color=[0, 0.7, 0, 1]
        )
        main_layout.add_widget(self.status_label)
        
        # Добавляем дополнительное пространство внизу для клавиатуры
        spacer = Label(text='', size_hint_y=None, height='100dp')
        main_layout.add_widget(spacer)
        
        main_scroll.add_widget(main_layout)
        
        # Привязываем события клавиатуры
        Window.bind(on_keyboard=self.on_keyboard)
        if hasattr(Window, 'softinput_mode'):
            Window.softinput_mode = 'below_target'
        
        return main_scroll
    
    def on_activity_focus(self, instance, value):
        """Обрабатывает фокус на поле активности для прокрутки"""
        if value:  # Поле получило фокус
            # Прокручиваем вниз, чтобы поле было видно над клавиатурой
            Clock.schedule_once(lambda dt: self.scroll_to_input(), 0.3)
    
    def scroll_to_input(self):
        """Прокручивает к полю ввода активности"""
        try:
            # Получаем главный ScrollView
            main_scroll = self.root
            if hasattr(main_scroll, 'scroll_to'):
                # Прокручиваем вниз к полю ввода
                main_scroll.scroll_y = 0  # Прокрутка к низу
        except:
            pass
    
    def on_keyboard(self, window, key, *args):
        """Обрабатывает события клавиатуры"""
        # Можно добавить дополнительную логику при необходимости
        return False
    
    def request_android_permissions(self):
        """Запрашивает необходимые разрешения Android"""
        if android_available:
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.VIBRATE,
                Permission.WAKE_LOCK,
                Permission.FOREGROUND_SERVICE
            ])
    
    def setup_background_service(self):
        """Настраивает службу для работы в фоне"""
        if android_available:
            try:
                # Настраиваем приложение для работы в фоне
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                
                # Предотвращаем убийство приложения системой
                Intent = autoclass('android.content.Intent')
                PendingIntent = autoclass('android.app.PendingIntent')
                
            except Exception as e:
                print(f"Ошибка настройки фоновой службы: {e}")
    
    def on_pause(self):
        """Вызывается при переходе приложения в фон"""
        # ВАЖНО: Возвращаем True для продолжения работы в фоне
        if self.timer_running:
            self.show_notification(
                "Таймер работает в фоне",
                f"Таймер продолжает работать. Осталось: {self.time_left // 60:02d}:{self.time_left % 60:02d}"
            )
        return True  # True означает продолжение работы в фоне
    
    def on_resume(self):
        """Вызывается при возврате из фона"""
        if self.timer_running:
            self.status_label.text = "Таймер запущен"
            self.status_label.color = [1, 0.5, 0, 1]
        return True
    
    def start_timer(self, instance):
        try:
            minutes = int(self.time_input.text)
            if minutes <= 0:
                self.status_label.text = "Ошибка: время должно быть положительным"
                self.status_label.color = [1, 0, 0, 1]
                return
                
            self.time_left = minutes * 60
            self.timer_running = True
            self.start_time = datetime.now()
            
            # Обновляем интерфейс
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.time_input.readonly = True
            self.status_label.text = "Таймер запущен"
            self.status_label.color = [1, 0.5, 0, 1]
            
            # Показываем уведомление о начале таймера
            self.show_notification(
                "Таймер запущен",
                f"Таймер на {minutes} минут активен. Приложение работает в фоне."
            )
            
            # Запускаем таймер
            Clock.schedule_interval(self.update_timer, 1)
            
        except ValueError:
            self.status_label.text = "Ошибка: введите корректное число"
            self.status_label.color = [1, 0, 0, 1]
    
    def update_timer(self, dt):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.time_display.text = f"{minutes:02d}:{seconds:02d}"
            
            # Изменяем цвет в зависимости от оставшегося времени
            if self.time_left <= 60:
                self.time_display.color = [1, 0, 0, 1]
            elif self.time_left <= 300:
                self.time_display.color = [1, 0.5, 0, 1]
            else:
                self.time_display.color = [0.2, 0.6, 1, 1]
            
            # Обновляем уведомление каждые 5 минут
            if self.time_left % 300 == 0:
                self.update_background_notification()
            
            if self.time_left <= 0:
                self.timer_finished()
                
        return self.timer_running
    
    def timer_finished(self):
        self.timer_running = False
        self.time_display.text = "00:00"
        self.time_display.color = [1, 0, 0, 1]
        self.status_label.text = "ВРЕМЯ ВЫШЛО! Укажите активность"
        self.status_label.color = [1, 0, 0, 1]
        
        # Показываем уведомление об окончании
        self.show_notification(
            "ВРЕМЯ ВЫШЛО!",
            "Таймер завершен! Откройте приложение для ввода активности.",
            urgent=True
        )
        
        # Воспроизводим звуковой сигнал
        self.play_notification_sound()
        
        # Активируем поле для ввода
        self.save_button.disabled = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.activity_input.focus = True
        
        Clock.unschedule(self.update_timer)
    
    def show_notification(self, title, message, urgent=False):
        """Показывает уведомление в панели уведомлений Android"""
        if android_available:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Таймер",
                    app_icon=None,
                    timeout=10 if not urgent else 0,
                    toast=urgent
                )
            except Exception as e:
                print(f"Ошибка уведомления: {e}")
    
    def play_notification_sound(self):
        """Воспроизводит звуковой сигнал"""
        if android_available:
            try:
                # Системный звук уведомления
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                
                # Получаем RingtoneManager для системных звуков
                RingtoneManager = autoclass('android.media.RingtoneManager')
                
                # Воспроизводим звук уведомления
                notification_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
                ringtone = RingtoneManager.getRingtone(context, notification_uri)
                
                if ringtone:
                    ringtone.play()
                    
                # Дополнительно вибрация
                self.vibrate_device()
                    
            except Exception as e:
                print(f"Ошибка воспроизведения звука: {e}")
    
    def vibrate_device(self):
        """Включает вибрацию устройства"""
        if android_available:
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                vibrator = context.getSystemService(context.VIBRATOR_SERVICE)
                
                if vibrator and vibrator.hasVibrator():
                    # Вибрация на 1 секунду
                    vibrator.vibrate(1000)
            except Exception as e:
                print(f"Ошибка вибрации: {e}")
    
    def update_background_notification(self):
        """Обновляет уведомление о работающем таймере"""
        if self.timer_running:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            
            self.show_notification(
                "Таймер активен",
                f"Осталось времени: {minutes:02d}:{seconds:02d}"
            )
    
    def stop_timer(self, instance):
        self.timer_running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.status_label.text = "Таймер остановлен"
        self.status_label.color = [1, 0, 0, 1]
        Clock.unschedule(self.update_timer)
        
        # Убираем фоновое уведомление
        if android_available:
            try:
                notification.notify(
                    title="Таймер остановлен",
                    message="Таймер был остановлен пользователем",
                    timeout=3
                )
            except:
                pass
    
    def reset_timer(self, instance):
        self.timer_running = False
        self.time_left = 0
        self.time_display.text = "00:00"
        self.time_display.color = [0.2, 0.6, 1, 1]
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.save_button.disabled = True
        self.activity_input.text = ""
        self.status_label.text = "Готов к работе"
        self.status_label.color = [0, 0.7, 0, 1]
        Clock.unschedule(self.update_timer)
    
    def save_activity(self, instance):
        activity = self.activity_input.text.strip()
        if not activity:
            self.status_label.text = "Введите описание активности"
            self.status_label.color = [1, 0, 0, 1]
            return
        
        try:
            duration_minutes = int(self.time_input.text)
            end_time = datetime.now()
            
            if not os.path.exists(self.log_file):
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("=== ЖУРНАЛ АКТИВНОСТИ ===\n\n")
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(
                    f"Дата: {self.start_time:%Y-%m-%d %H:%M:%S} -> "
                    f"{end_time:%Y-%m-%d %H:%M:%S}\n"
                    f"Длительность: {duration_minutes} мин\n"
                    f"Активность: {activity}\n"
                    f"{'-' * 40}\n\n"
                )
            
            self.status_label.text = "Активность сохранена!"
            self.status_label.color = [0, 0.7, 0, 1]
            self.save_button.disabled = True
            self.activity_input.text = ""
            
            # Уведомление о сохранении
            self.show_notification(
                "Активность сохранена",
                f"Записана активность: {activity}"
            )
            
        except Exception as e:
            self.status_label.text = f"Ошибка сохранения: {e}"
            self.status_label.color = [1, 0, 0, 1]
    
    def view_log(self, instance):
        """Показывает лог в popup окне"""
        try:
            if not os.path.exists(self.log_file):
                content_text = "Журнал пуст.\nЗапустите таймер для создания записей."
            else:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    content_text = f.read()
                    if not content_text.strip():
                        content_text = "Журнал пуст.\nЗапустите таймер для создания записей."
        except Exception as e:
            content_text = f"Ошибка чтения лога: {e}"
        
        content = BoxLayout(orientation='vertical', spacing=10)
        
        title_label = Label(
            text='ЖУРНАЛ АКТИВНОСТИ',
            font_size='18sp',
            size_hint_y=None,
            height='40dp',
            bold=True
        )
        content.add_widget(title_label)
        
        scroll = ScrollView()
        log_label = Label(
            text=content_text,
            font_size='12sp',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        scroll.add_widget(log_label)
        content.add_widget(scroll)
        
        close_button = Button(
            text='ЗАКРЫТЬ',
            font_size='16sp',
            size_hint_y=None,
            height='50dp'
        )
        content.add_widget(close_button)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        close_button.bind(on_press=popup.dismiss)
        
        def update_text_size(instance, value):
            log_label.text_size = (value[0] - 40, None)
        
        popup.bind(size=update_text_size)
        popup.open()
    
    def clear_log(self, instance):
        """Очищает журнал с подтверждением"""
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)
        
        message = Label(
            text='ВНИМАНИЕ!\n\nВы уверены, что хотите очистить журнал?\nЭто действие нельзя отменить.',
            font_size='16sp',
            text_size=(None, None),
            halign='center'
        )
        content.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='50dp')
        
        yes_button = Button(text='ДА, ОЧИСТИТЬ', font_size='14sp')
        no_button = Button(text='ОТМЕНА', font_size='14sp')
        
        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)
        content.add_widget(buttons)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        def confirm_clear(instance):
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("=== ЖУРНАЛ АКТИВНОСТИ ===\n\n")
                self.status_label.text = "Журнал очищен"
                self.status_label.color = [0, 0.7, 0, 1]
            except Exception as e:
                self.status_label.text = f"Ошибка очистки: {e}"
                self.status_label.color = [1, 0, 0, 1]
            popup.dismiss()
        
        yes_button.bind(on_press=confirm_clear)
        no_button.bind(on_press=popup.dismiss)
        
        popup.open()

if __name__ == '__main__':
    TimerApp().run()
