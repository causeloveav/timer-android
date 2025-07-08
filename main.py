from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from datetime import datetime
import os

class TimerApp(App):
    def build(self):
        self.title = "Таймер для Android"
        
        # Переменные
        self.time_left = 0
        self.timer_running = False
        self.start_time = None
        self.log_file = "activity_log.txt"
        
        # Основной layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Заголовок
        title = Label(text='Таймер активности', font_size=20, size_hint_y=0.1)
        main_layout.add_widget(title)
        
        # Ввод времени
        time_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        time_layout.add_widget(Label(text='Минуты:', size_hint_x=0.3))
        self.time_input = TextInput(text='25', multiline=False, size_hint_x=0.7)
        time_layout.add_widget(self.time_input)
        main_layout.add_widget(time_layout)
        
        # Отображение времени
        self.time_display = Label(text='00:00', font_size=40, size_hint_y=0.2)
        main_layout.add_widget(self.time_display)
        
        # Кнопки управления
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.start_button = Button(text='Старт')
        self.start_button.bind(on_press=self.start_timer)
        button_layout.add_widget(self.start_button)
        
        self.stop_button = Button(text='Стоп', disabled=True)
        self.stop_button.bind(on_press=self.stop_timer)
        button_layout.add_widget(self.stop_button)
        
        reset_button = Button(text='Сброс')
        reset_button.bind(on_press=self.reset_timer)
        button_layout.add_widget(reset_button)
        
        main_layout.add_widget(button_layout)
        
        # Поле активности
        activity_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        activity_layout.add_widget(Label(text='Активность:', size_hint_x=0.3))
        self.activity_input = TextInput(multiline=False, size_hint_x=0.7)
        activity_layout.add_widget(self.activity_input)
        main_layout.add_widget(activity_layout)
        
        # Кнопка сохранения
        self.save_button = Button(text='Сохранить', size_hint_y=0.1, disabled=True)
        self.save_button.bind(on_press=self.save_activity)
        main_layout.add_widget(self.save_button)
        
        # Статус
        self.status_label = Label(text='Готов к работе', size_hint_y=0.1)
        main_layout.add_widget(self.status_label)
        
        return main_layout
    
    def start_timer(self, instance):
        try:
            minutes = int(self.time_input.text)
            if minutes <= 0:
                self.status_label.text = "Ошибка: время должно быть положительным"
                return
                
            self.time_left = minutes * 60
            self.timer_running = True
            self.start_time = datetime.now()
            
            # Обновляем интерфейс
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.time_input.readonly = True
            self.status_label.text = "Таймер запущен"
            
            # Запускаем таймер
            Clock.schedule_interval(self.update_timer, 1)
            
        except ValueError:
            self.status_label.text = "Ошибка: введите корректное число"
    
    def update_timer(self, dt):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.time_display.text = f"{minutes:02d}:{seconds:02d}"
            
            if self.time_left <= 0:
                self.timer_finished()
                
        return self.timer_running
    
    def timer_finished(self):
        self.timer_running = False
        self.time_display.text = "00:00"
        self.status_label.text = "Время вышло! Укажите активность"
        
        # Активируем поле для ввода
        self.save_button.disabled = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        
        Clock.unschedule(self.update_timer)
    
    def stop_timer(self, instance):
        self.timer_running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.status_label.text = "Таймер остановлен"
        Clock.unschedule(self.update_timer)
    
    def reset_timer(self, instance):
        self.timer_running = False
        self.time_left = 0
        self.time_display.text = "00:00"
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.save_button.disabled = True
        self.activity_input.text = ""
        self.status_label.text = "Готов к работе"
        Clock.unschedule(self.update_timer)
    
    def save_activity(self, instance):
        activity = self.activity_input.text.strip()
        if not activity:
            self.status_label.text = "Введите описание активности"
            return
        
        try:
            duration_minutes = int(self.time_input.text)
            end_time = datetime.now()
            
            # Сохраняем в лог
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(
                    f"{self.start_time:%Y-%m-%d %H:%M:%S} | "
                    f"{end_time:%Y-%m-%d %H:%M:%S} | "
                    f"{duration_minutes} мин | "
                    f"{activity}\n"
                )
            
            self.status_label.text = "Активность сохранена"
            self.save_button.disabled = True
            self.activity_input.text = ""
            
        except Exception as e:
            self.status_label.text = f"Ошибка сохранения: {e}"

# Запуск приложения
if __name__ == '__main__':
    TimerApp().run()
