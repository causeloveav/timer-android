from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
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
        
        # Основной layout для вертикальной ориентации
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        title = Label(
            text='ТАЙМЕР АКТИВНОСТИ', 
            font_size='24sp', 
            size_hint_y=None, 
            height='60dp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Секция ввода времени
        time_section = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        time_section.add_widget(Label(text='Время (мин):', font_size='16sp', size_hint_x=0.4))
        self.time_input = TextInput(
            text='25', 
            multiline=False, 
            font_size='16sp',
            size_hint_x=0.6,
            input_filter='int'
        )
        time_section.add_widget(self.time_input)
        main_layout.add_widget(time_section)
        
        # Отображение времени - большой дисплей
        self.time_display = Label(
            text='00:00', 
            font_size='64sp', 
            size_hint_y=None, 
            height='120dp',
            bold=True,
            color=[0.2, 0.6, 1, 1]  # Синий цвет
        )
        main_layout.add_widget(self.time_display)
        
        # Кнопки управления таймером
        timer_buttons = GridLayout(cols=3, size_hint_y=None, height='60dp', spacing=10)
        
        self.start_button = Button(text='▶ СТАРТ', font_size='14sp')
        self.start_button.bind(on_press=self.start_timer)
        timer_buttons.add_widget(self.start_button)
        
        self.stop_button = Button(text='⏸ СТОП', font_size='14sp', disabled=True)
        self.stop_button.bind(on_press=self.stop_timer)
        timer_buttons.add_widget(self.stop_button)
        
        reset_button = Button(text='🔄 СБРОС', font_size='14sp')
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
        
        self.activity_input = TextInput(
            multiline=True, 
            font_size='14sp',
            size_hint_y=None,
            height='80dp',
            hint_text='Опишите свою активность...'
        )
        main_layout.add_widget(self.activity_input)
        
        # Кнопка сохранения активности
        self.save_button = Button(
            text='💾 СОХРАНИТЬ АКТИВНОСТЬ', 
            font_size='16sp',
            size_hint_y=None, 
            height='50dp', 
            disabled=True
        )
        self.save_button.bind(on_press=self.save_activity)
        main_layout.add_widget(self.save_button)
        
        # Разделитель
        main_layout.add_widget(Label(text='', size_hint_y=None, height='15dp'))
        
        # Кнопки управления логом
        log_buttons = GridLayout(cols=2, size_hint_y=None, height='50dp', spacing=10)
        
        view_log_button = Button(text='📋 ПОСМОТРЕТЬ ЛОГ', font_size='14sp')
        view_log_button.bind(on_press=self.view_log)
        log_buttons.add_widget(view_log_button)
        
        clear_log_button = Button(text='🗑️ ОЧИСТИТЬ ЛОГ', font_size='14sp')
        clear_log_button.bind(on_press=self.clear_log)
        log_buttons.add_widget(clear_log_button)
        
        main_layout.add_widget(log_buttons)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе', 
            font_size='14sp',
            size_hint_y=None, 
            height='40dp',
            color=[0, 0.7, 0, 1]  # Зеленый цвет
        )
        main_layout.add_widget(self.status_label)
        
        return main_layout
    
    def start_timer(self, instance):
        try:
            minutes = int(self.time_input.text)
            if minutes <= 0:
                self.status_label.text = "Ошибка: время должно быть положительным"
                self.status_label.color = [1, 0, 0, 1]  # Красный
                return
                
            self.time_left = minutes * 60
            self.timer_running = True
            self.start_time = datetime.now()
            
            # Обновляем интерфейс
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.time_input.readonly = True
            self.status_label.text = "⏰ Таймер запущен"
            self.status_label.color = [1, 0.5, 0, 1]  # Оранжевый
            
            # Запускаем таймер
            Clock.schedule_interval(self.update_timer, 1)
            
        except ValueError:
            self.status_label.text = "Ошибка: введите корректное число"
            self.status_label.color = [1, 0, 0, 1]  # Красный
    
    def update_timer(self, dt):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.time_display.text = f"{minutes:02d}:{seconds:02d}"
            
            # Изменяем цвет в зависимости от оставшегося времени
            if self.time_left <= 60:  # Последняя минута
                self.time_display.color = [1, 0, 0, 1]  # Красный
            elif self.time_left <= 300:  # Последние 5 минут
                self.time_display.color = [1, 0.5, 0, 1]  # Оранжевый
            else:
                self.time_display.color = [0.2, 0.6, 1, 1]  # Синий
            
            if self.time_left <= 0:
                self.timer_finished()
                
        return self.timer_running
    
    def timer_finished(self):
        self.timer_running = False
        self.time_display.text = "00:00"
        self.time_display.color = [1, 0, 0, 1]  # Красный
        self.status_label.text = "⏰ ВРЕМЯ ВЫШЛО! Укажите активность"
        self.status_label.color = [1, 0, 0, 1]  # Красный
        
        # Активируем поле для ввода
        self.save_button.disabled = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.activity_input.focus = True
        
        Clock.unschedule(self.update_timer)
    
    def stop_timer(self, instance):
        self.timer_running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.status_label.text = "⏸ Таймер остановлен"
        self.status_label.color = [1, 0, 0, 1]  # Красный
        Clock.unschedule(self.update_timer)
    
    def reset_timer(self, instance):
        self.timer_running = False
        self.time_left = 0
        self.time_display.text = "00:00"
        self.time_display.color = [0.2, 0.6, 1, 1]  # Синий
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.time_input.readonly = False
        self.save_button.disabled = True
        self.activity_input.text = ""
        self.status_label.text = "✅ Готов к работе"
        self.status_label.color = [0, 0.7, 0, 1]  # Зеленый
        Clock.unschedule(self.update_timer)
    
    def save_activity(self, instance):
        activity = self.activity_input.text.strip()
        if not activity:
            self.status_label.text = "Введите описание активности"
            self.status_label.color = [1, 0, 0, 1]  # Красный
            return
        
        try:
            duration_minutes = int(self.time_input.text)
            end_time = datetime.now()
            
            # Создаем файл лога если не существует
            if not os.path.exists(self.log_file):
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("=== ЖУРНАЛ АКТИВНОСТИ ===\n\n")
            
            # Сохраняем в лог
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(
                    f"📅 {self.start_time:%Y-%m-%d %H:%M:%S} → "
                    f"{end_time:%Y-%m-%d %H:%M:%S}\n"
                    f"⏱️ Длительность: {duration_minutes} мин\n"
                    f"📝 Активность: {activity}\n"
                    f"{'-' * 40}\n\n"
                )
            
            self.status_label.text = "💾 Активность сохранена!"
            self.status_label.color = [0, 0.7, 0, 1]  # Зеленый
            self.save_button.disabled = True
            self.activity_input.text = ""
            
        except Exception as e:
            self.status_label.text = f"Ошибка сохранения: {e}"
            self.status_label.color = [1, 0, 0, 1]  # Красный
    
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
        
        # Создаем popup с логом
        content = BoxLayout(orientation='vertical', spacing=10)
        
        # Заголовок
        title_label = Label(
            text='📋 ЖУРНАЛ АКТИВНОСТИ',
            font_size='18sp',
            size_hint_y=None,
            height='40dp',
            bold=True
        )
        content.add_widget(title_label)
        
        # Текст лога в скроллируемом виде
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
        
        # Кнопка закрытия
        close_button = Button(
            text='❌ ЗАКРЫТЬ',
            font_size='16sp',
            size_hint_y=None,
            height='50dp'
        )
        content.add_widget(close_button)
        
        # Создаем и показываем popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        close_button.bind(on_press=popup.dismiss)
        
        # Адаптируем размер текста под popup
        def update_text_size(instance, value):
            log_label.text_size = (value[0] - 40, None)
        
        popup.bind(size=update_text_size)
        popup.open()
    
    def clear_log(self, instance):
        """Очищает журнал с подтверждением"""
        # Создаем popup подтверждения
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)
        
        message = Label(
            text='⚠️ ВНИМАНИЕ!\n\nВы уверены, что хотите очистить журнал?\nЭто действие нельзя отменить.',
            font_size='16sp',
            text_size=(None, None),
            halign='center'
        )
        content.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='50dp')
        
        yes_button = Button(text='✅ ДА, ОЧИСТИТЬ', font_size='14sp')
        no_button = Button(text='❌ ОТМЕНА', font_size='14sp')
        
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
                self.status_label.text = "🗑️ Журнал очищен"
                self.status_label.color = [0, 0.7, 0, 1]  # Зеленый
            except Exception as e:
                self.status_label.text = f"Ошибка очистки: {e}"
                self.status_label.color = [1, 0, 0, 1]  # Красный
            popup.dismiss()
        
        yes_button.bind(on_press=confirm_clear)
        no_button.bind(on_press=popup.dismiss)
        
        popup.open()

if __name__ == '__main__':
    TimerApp().run()
