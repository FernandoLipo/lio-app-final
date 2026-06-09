[app]
title = LioApp
package.name = lioapplimpieza
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy==2.3.0,sqlite3,pillow

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
android.skip_update = False
log_level = 2

# Forzamos el entorno exacto que dio verde en las pruebas
android.api = 33
android.minapi = 24
android.ndk = 25.2.9519653
android.ndk_api = 24

[buildozer]
log_level = 2
warn_on_root = 1
