[app]
title = Timer Android
package.name = timer_android
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.1
requirements = python3,kivy

# Важные настройки для GitHub Actions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 0
