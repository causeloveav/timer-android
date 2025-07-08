[app]
title = Timer Android
package.name = timer_android
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.2
requirements = python3,kivy

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.private_storage = True

# ВАЖНО: Принудительная вертикальная ориентация
orientation = portrait
android.orientation = portrait

fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 0
