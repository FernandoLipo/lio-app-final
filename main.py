from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.metrics import dp
import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont

class PantallaPrincipal(Screen):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        
        ruta_app = App.get_running_app().user_data_dir
        self.base_datos = os.path.join(ruta_app, "lio_limpieza.db")
        self.crear_base_datos()

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        layout.add_widget(Label(text="LIO LIMPIEZA APP", font_size='24sp', bold=True, size_hint_y=None, height=dp(40)))
        layout.add_widget(Label(text="INGRESAR PRODUCTO (Código)", font_size='16sp', size_hint_y=None, height=dp(25)))
        
        self.input_codigo = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=dp(45), input_type='number')
        layout.add_widget(self.input_codigo)

        btn_buscar = Button(text="BUSCAR", font_size='18sp', bold=True, size_hint_y=None, height=dp(45), background_color=(0.2, 0.6, 0.2, 1))
        btn_buscar.bind(on_release=self.buscar_producto)
        layout.add_widget(btn_buscar)

        layout.add_widget(Label(text="DESCRIPCIÓN:", font_size='16sp', size_hint_y=None, height=dp(25)))
        self.input_nombre = TextInput(multiline=False, font_size='16sp', size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_nombre)

        layout.add_widget(Label(text="PRECIO ($):", font_size='16sp', size_hint_y=None, height=dp(25)))
        self.input_precio = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=dp(45), input_type='number')
        layout.add_widget(self.input_precio)

        self.lbl_estado = Label(text="Listo.", font_size='14sp', color=(1, 1, 0, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_estado)

        layout.add_widget(Widget())

        self.btn_guardar = Button(text="GUARDAR NUEVO", font_size='18sp', bold=True, size_hint_y=None, height=dp(45), background_color=(0.1, 0.5, 0.8, 1))
        self.btn_guardar.bind(on_release=self.guardar_producto)
        layout.add_widget(self.btn_guardar)

        layout_edicion = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(45))
        
        self.btn_editar = Button(text="EDITAR", font_size='16sp', bold=True, background_color=(0.9, 0.6, 0.1, 1), disabled=True)
        self.btn_editar.bind(on_release=self.editar_producto)
        layout_edicion.add_widget(self.btn_editar)
        
        self.btn_borrar = Button(text="BORRAR", font_size='16sp', bold=True, background_color=(0.8, 0.2, 0.2, 1), disabled=True)
        self.btn_borrar.bind(on_release=self.borrar_producto)
        layout_edicion.add_widget(self.btn_borrar)
        layout.add_widget(layout_edicion)

        btn_exportar = Button(text="EXPORTAR LISTA DE PRECIOS", font_size='16sp', bold=True, size_hint_y=None, height=dp(50))
        btn_exportar.bind(on_release=self.ir_a_lista)
        layout.add_widget(btn_exportar)

        self.add_widget(layout)

    def crear_base_datos(self):
        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS productos (codigo TEXT PRIMARY KEY, nombre TEXT, precio REAL)")
        conn.commit()
        conn.close()

    def buscar_producto(self, instance):
        codigo = self.input_codigo.text.strip()
        if not codigo:
            self.lbl_estado.text = "Ingresa un código para buscar."
            return

        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, precio FROM productos WHERE codigo=?", (codigo,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.input_nombre.text = resultado[0]
            self.input_precio.text = str(resultado[1])
            self.lbl_estado.text = "Producto encontrado."
            self.btn_guardar.disabled = True
            self.btn_editar.disabled = False
            self.btn_borrar.disabled = False
        else:
            self.input_nombre.text = ""
            self.input_precio.text = ""
            self.lbl_estado.text = "No existe. Completá los campos para crearlo."
            self.btn_guardar.disabled = False
            self.btn_editar.disabled = True
            self.btn_borrar.disabled = True

    def guardar_producto(self, instance):
        codigo = self.input_codigo.text.strip()
        nombre = self.input_nombre.text.strip()
        precio_txt = self.input_precio.text.strip()

        if not codigo or not nombre or not precio_txt:
            self.lbl_estado.text = "Error: Faltan completar datos."
            return
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos VALUES (?, ?, ?)", (codigo, nombre, float(precio_txt)))
            conn.commit()
            conn.close()
            self.lbl_estado.text = "Producto guardado con éxito."
            self.buscar_producto(None)
        except Exception as e:
            self.lbl_estado.text = "Error al guardar: Código ya existe."

    def editar_producto(self, instance):
        codigo = self.input_codigo.text.strip()
        nombre = self.input_nombre.text.strip()
        precio_txt = self.input_precio.text.strip()

        if not codigo or not nombre or not precio_txt:
            self.lbl_estado.text = "Error: Campos vacíos."
            return

        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET nombre=?, precio=? WHERE codigo=?", (nombre, float(precio_txt), codigo))
        conn.commit()
        conn.close()
        self.lbl_estado.text = "Producto modificado correctamente."

    def borrar_producto(self, instance):
        codigo = self.input_codigo.text.strip()
        if not codigo: return

        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE codigo=?", (codigo,))
        conn.commit()
        conn.close()
        
        self.input_codigo.text = ""
        self.input_nombre.text = ""
        self.input_precio.text = ""
        self.lbl_estado.text = "Producto eliminado."
        self.btn_guardar.disabled = False
        self.btn_editar.disabled = True
        self.btn_borrar.disabled = True

    def ir_a_lista(self, instance):
        self.manager.current = 'lista'

class PantallaLista(Screen):
    def on_enter(self):
        self.generar_foto_lista()

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        layout.add_widget(Label(text="VISTA PREVIA DE TU LISTA", font_size='22sp', bold=True, size_hint_y=None, height=dp(40)))
        
        self.lbl_info = Label(
            text="Lista de Precios\nPedidos WhatsApp: 1123017122\n\n(Generando foto...)", 
            font_size='16sp',
            halign='center'
        )
        layout.add_widget(self.lbl_info)

        layout.add_widget(Widget())

        layout_acciones = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        
        btn_volver = Button(text="VOLVER ATRÁS", font_size='16sp', bold=True)
        btn_volver.bind(on_release=self.volver)
        layout_acciones.add_widget(btn_volver)

        btn_compartir = Button(text="COMPARTIR", font_size='16sp', bold=True, background_color=(0.1, 0.6, 0.2, 1))
        btn_compartir.bind(on_release=self.compartir_lista)
        layout_acciones.add_widget(btn_compartir)
        
        layout.add_widget(layout_acciones)
        self.add_widget(layout)

    def generar_foto_lista(self):
        try:
            ruta_app = App.get_running_app().user_data_dir
            base_datos = os.path.join(ruta_app, "lio_limpieza.db")
            
            conn = sqlite3.connect(base_datos)
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, precio FROM productos ORDER BY nombre ASC")
            items = cursor.fetchall()
            conn.close()

            ancho = 720
            alto = 200 + (len(items) * 45) if items else 400
            
            imagen = Image.new("RGB", (ancho, alto), "white")
            lienzo = ImageDraw.Draw(imagen)

            lienzo.text((40, 30), "LISTA DE PRECIOS", fill="black")
            lienzo.text((40, 70), "PEDIDOS WHATSAPP: 1123017122", fill="black")
            lienzo.line([(40, 110), (680, 110)], fill="black", width=2)

            lienzo.text((40, 130), "PRODUCTO", fill="black")
            lienzo.text((580, 130), "PRECIO", fill="black")
            lienzo.line([(40, 160), (680, 160)], fill="grey", width=1)

            y = 180
            for prod, precio in items:
                lienzo.text((40, y), str(prod), fill="black")
                lienzo.text((580, y), f"${precio:,.2f}", fill="black")
                y += 45

            from android.storage import primary_external_storage_path
            path_publico = primary_external_storage_path()
            self.ruta_final_foto = os.path.join(path_publico, "Download", "Lista_Precios_Lio.png")
            imagen.save(self.ruta_final_foto)
            self.lbl_info.text = "Lista de Precios\nPedidos WhatsApp: 1123017122\n\n¡Guardada en Descargas!"
        except Exception as e:
            ruta_local = os.path.join(App.get_running_app().user_data_dir, "Lista_Precios.png")
            imagen.save(ruta_local)
            self.ruta_final_foto = ruta_local
            self.lbl_info.text = f"Foto guardada localmente."

    def compartir_lista(self, instance):
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            
            archivo_foto = File(self.ruta_final_foto)
            intent = Intent(Intent.ACTION_SEND)
            intent.setType("image/png")
            intent.putExtra(Intent.EXTRA_STREAM, Uri.fromFile(archivo_foto))
            
            current_activity = autoclass('org.kivy.android.PythonActivity').mActivity
            current_activity.startActivity(Intent.createChooser(intent, "Compartir Lista via..."))
        except:
            self.lbl_info.text = "Compartir requiere ejecucion en Android."

    def volver(self, instance):
        self.manager.current = 'principal'

class LioLimpiezaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaPrincipal(name='principal'))
        sm.add_widget(PantallaLista(name='lista'))
        return sm

if __name__ == '__main__':
    LioLimpiezaApp().run()
