[app]
title = Focus Timer 2025
package.name = focus_timer_2025
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0
requirements = python3,kivy,plyer,pyjnius,android

# Разрешения для современного приложения
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE,WAKE_LOCK,FOREGROUND_SERVICE,POST_NOTIFICATIONS,MODIFY_AUDIO_SETTINGS,ACCESS_NOTIFICATION_POLICY,SYSTEM_ALERT_WINDOW

android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b
android.private_storage = True

# Вертикальная ориентация
orientation = portrait
android.orientation = portrait

# Настройки для фоновой работы
android.service = 1
android.wakelock = 1

# Современный адаптивный дизайн
android.gradle_dependencies = androidx.core:core:1.8.0, androidx.appcompat:appcompat:1.4.2

fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 0
