[app]
title = Timer Android
package.name = timer_android
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.3
requirements = python3,kivy,plyer,pyjnius,android

# Разрешения для фоновой работы и уведомлений
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE,WAKE_LOCK,FOREGROUND_SERVICE,POST_NOTIFICATIONS,MODIFY_AUDIO_SETTINGS,ACCESS_NOTIFICATION_POLICY

android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.private_storage = True

# Принудительная вертикальная ориентация
orientation = portrait
android.orientation = portrait

# Настройки для фоновой службы
android.service = 1
android.wakelock = 1

fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 0
