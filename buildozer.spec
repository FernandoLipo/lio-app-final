[app]
title = LioApp
package.name = lioapplimpieza
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Requerimientos para tu interfaz de ingreso, base de datos sqlite y manejo de imagen para exportar
requirements = python3,kivy,sqlite3,pillow

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
android.skip_update = False
log_level = 2

# Agregamos los permisos para que la app pueda guardar la lista en tu galería de fotos
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MOUNT_UNMOUNT_FILESYSTEMS

# Dejamos que el sistema moderno elija las versiones por defecto compatibles
android.api = 33
android.minapi = 24

[buildozer]
log_level = 2
warn_on_root = 1
