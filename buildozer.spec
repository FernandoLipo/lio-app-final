[app]
title = LioApp
package.name = lioapplimpieza
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Usamos sqlite3 y pillow para tu lista en formato imagen
requirements = python3,kivy,sqlite3,pillow

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
android.skip_update = False
log_level = 2

# Forzamos la versión recomendada por el sistema que sí existe para descargar
android.api = 33
android.minapi = 24
android.ndk = r28c
android.ndk_api = 24

[buildozer]
log_level = 2
warn_on_root = 1
