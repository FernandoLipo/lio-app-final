from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont

class PantallaPrincipal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        ruta_app = App.get_running_app().user_data_dir
        self.base_datos = os.path.join(ruta_app, "lio_limpieza.db")
        self.crear_base_datos()

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        layout.add_widget(Label(text="LIO LIMPIEZA APP", font_size='24sp', bold=True, size_hint_y=None, height=dp(40)))
        layout.add_widget(Label(text="BUSCAR PRODUCTO (Por Nombre o Parte)", font_size='16sp', size_hint_y=None, height=dp(25)))
        
        self.input_buscar = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_buscar)

        btn_buscar = Button(text="BUSCAR", font_size='18sp', bold=True, size_hint_y=None, height=dp(45), background_color=(0.1, 0.4, 0.1, 1))
        btn_buscar.bind(on_release=self.buscar_producto)
        layout.add_widget(btn_buscar)

        layout.add_widget(Label(text="DESCRIPCIÓN COMPLETA:", font_size='16sp', size_hint_y=None, height=dp(25)))
        self.input_nombre = TextInput(multiline=False, font_size='16sp', size_hint_y=None, height=dp(45))
        layout.add_widget(self.input_nombre)

        layout.add_widget(Label(text="PRECIO ($):", font_size='16sp', size_hint_y=None, height=dp(25)))
        self.input_precio = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=dp(45), input_type='number')
        layout.add_widget(self.input_precio)

        self.lbl_estado = Label(text="Listo.", font_size='14sp', color=(1, 1, 0, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_estado)

        layout.add_widget(Widget())

        self.btn_guardar = Button(text="GUARDAR NUEVO", font_size='18sp', bold=True, size_hint_y=None, height=dp(45), background_color=(0.1, 0.3, 0.5, 1))
        self.btn_guardar.bind(on_release=self.guardar_producto)
        layout.add_widget(self.btn_guardar)

        layout_edicion = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(45))
        
        self.btn_editar = Button(text="EDITAR", font_size='16sp', bold=True, background_color=(0.7, 0.4, 0.1, 1), disabled=True)
        self.btn_editar.bind(on_release=self.editar_producto)
        layout_edicion.add_widget(self.btn_editar)
        
        self.btn_borrar = Button(text="BORRAR", font_size='16sp', bold=True, background_color=(0.6, 0.1, 0.1, 1), disabled=True)
        self.btn_borrar.bind(on_release=self.borrar_producto)
        layout_edicion.add_widget(self.btn_borrar)
        layout.add_widget(layout_edicion)

        btn_exportar = Button(text="VER LISTA DE PRECIOS", font_size='16sp', bold=True, size_hint_y=None, height=dp(50))
        btn_exportar.bind(on_release=self.ir_a_lista)
        layout.add_widget(btn_exportar)

        self.add_widget(layout)

    def crear_base_datos(self):
        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS productos (nombre TEXT PRIMARY KEY, precio REAL)")
        conn.commit()
        conn.close()

    def buscar_producto(self, instance):
        criterio = self.input_buscar.text.strip()
        if not criterion:
            self.lbl_estado.text = "Ingresa un nombre para buscar."
            return

        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, precio FROM productos WHERE nombre LIKE ? COLLATE NOCASE", (f"%{criterio}%",))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.input_nombre.text = resultado[0]
            self.input_precio.text = str(resultado[1])
            self.lbl_estado.text = "Producto encontrado."
            self.btn_guardar.disabled = True
            self.btn_editar.disabled = False
            self.btn_borrar.disabled = False
            self.input_buscar.text = ""
        else:
            self.input_nombre.text = criterio
            self.input_precio.text = ""
            self.lbl_estado.text = "No existe. Podes crearlo con ese nombre."
            self.btn_guardar.disabled = False
            self.btn_editar.disabled = True
            self.btn_borrar.disabled = True

    def guardar_producto(self, instance):
        nombre = self.input_nombre.text.strip()
        precio_txt = self.input_precio.text.strip()

        if not nombre or not precio_txt:
            self.lbl_estado.text = "Error: Faltan completar datos."
            return
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos VALUES (?, ?)", (nombre, float(precio_txt)))
            conn.commit()
            conn.close()
            self.lbl_estado.text = "Producto guardado con éxito."
            self.input_buscar.text = ""
            self.input_nombre.text = ""
            self.input_precio.text = ""
        except Exception as e:
            self.lbl_estado.text = "Error al guardar: El producto ya existe."

    def editar_producto(self, instance):
        nombre = self.input_nombre.text.strip()
        precio_txt = self.input_precio.text.strip()

        if not nombre or not precio_txt:
            self.lbl_estado.text = "Error: Campos vacíos."
            return

        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET precio=? WHERE nombre=?", (float(precio_txt), nombre))
        conn.commit()
        conn.close()
        self.lbl_estado.text = "Precio modificado correctamente."
        self.input_buscar.text = ""
        self.input_nombre.text = ""
        self.input_precio.text = ""

    def borrar_producto(self, instance):
        nombre = self.input_nombre.text.strip()
        if not nombre: return

        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE nombre=?", (nombre,))
        conn.commit()
        conn.close()
        
        self.input_buscar.text = ""
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
        self.cargar_vista_previa_texto()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout_principal = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        self.layout_principal.add_widget(Label(text="VISTA PREVIA DE TU LISTA", font_size='22sp', bold=True, size_hint_y=None, height=dp(40)))
        
        self.lbl_encabezado = Label(
            text="Lista de Precios\nPedidos WhatsApp: 1123017122", 
            font_size='16sp',
            halign='center',
            size_hint_y=None,
            height=dp(50)
        )
        self.layout_principal.add_widget(self.lbl_encabezado)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout_productos = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.layout_productos.bind(minimum_height=self.layout_productos.setter('height'))
        self.scroll.add_widget(self.layout_productos)
        self.layout_principal.add_widget(self.scroll)

        self.lbl_aviso = Label(text="", font_size='14sp', color=(0, 1, 0, 1), size_hint_y=None, height=dp(25))
        self.layout_principal.add_widget(self.lbl_aviso)

        layout_acciones = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        
        btn_volver = Button(text="VOLVER ATRÁS", font_size='16sp', bold=True)
        btn_volver.bind(on_release=self.volver)
        layout_acciones.add_widget(btn_volver)

        btn_exportar_imagen = Button(text="EXPORTAR LISTA", font_size='16sp', bold=True, background_color=(0.1, 0.4, 0.1, 1))
        btn_exportar_imagen.bind(on_release=self.exportar_a_galeria_nativa)
        layout_acciones.add_widget(btn_exportar_imagen)
        
        self.layout_principal.add_widget(layout_acciones)
        self.add_widget(self.layout_principal)

    def obtener_items(self):
        ruta_app = App.get_running_app().user_data_dir
        base_datos = os.path.join(ruta_app, "lio_limpieza.db")
        conn = sqlite3.connect(base_datos)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, precio FROM productos ORDER BY nombre ASC")
        items = cursor.fetchall()
        conn.close()
        return items

    def cargar_vista_previa_texto(self):
        self.layout_productos.clear_widgets()
        self.lbl_aviso.text = ""
        items = self.obtener_items()
        
        if not items:
            self.layout_productos.add_widget(Label(text="No hay productos guardados.", font_size='16sp', color=(1,0,0,1)))
            return

        for prod, precio in items:
            fila = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            fila.add_widget(Label(text=str(prod), font_size='16sp', halign='left', text_size=(dp(200), None)))
            fila.add_widget(Label(text=f"${precio:,.2f}", font_size='16sp', halign='right', text_size=(dp(100), None)))
            self.layout_productos.add_widget(fila)

    def exportar_a_galeria_nativa(self, instance):
        try:
            items = self.obtener_items()
            if not items:
                self.lbl_aviso.text = "No hay productos para exportar."
                return

            # 1. Dibujamos la imagen limpia con Pillow
            ancho = 720
            alto = 240 + (len(items) * 55)
            imagen = Image.new("RGB", (ancho, alto), "white")
            lienzo = ImageDraw.Draw(imagen)

            try:
                fuente_titulo = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 36)
                fuente_texto = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 26)
            except:
                fuente_titulo = ImageFont.load_default()
                fuente_texto = ImageFont.load_default()

            lienzo.text((40, 30), "LIO LIMPIEZA - LISTA DE PRECIOS", fill="black", font=fuente_titulo)
            lienzo.text((40, 85), "PEDIDOS WHATSAPP: 1123017122", fill="green", font=fuente_texto)
            lienzo.line([(40, 135), (680, 135)], fill="black", width=3)

            y = 160
            for prod, precio in items:
                lienzo.text((40, y), str(prod), fill="black", font=fuente_texto)
                lienzo.text((540, y), f"${precio:,.2f}", fill="black", font=fuente_texto)
                y += 55

            # Guardado temporal interno
            ruta_app = App.get_running_app().user_data_dir
            temp_path = os.path.join(ruta_app, "temp_lista.png")
            imagen.save(temp_path)

            # 2. Inyección forzada en la Galería usando MediaStore (Nativo Android sin permisos externos)
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            BitmapFactory = autoclass('android.graphics.BitmapFactory')
            MediaStore_Images_Media = autoclass('android.provider.MediaStore$Images$Media')
            
            actividad = PythonActivity.mActivity
            contenido_resolver = actividad.getContentResolver()
            
            # Decodificamos el archivo temporal como un Bitmap de Android
            bitmap = BitmapFactory.decodeFile(temp_path)
            
            # Insertamos directamente en el carrete del sistema público
            MediaStore_Images_Media.insertImage(
                contenido_resolver, 
                bitmap, 
                "Lista_Precios_Lio", 
                "Lista de precios generada desde LioApp"
            )
            
            self.lbl_aviso.text = "¡Guardada en la Galería de Fotos!"
        except Exception as e:
            self.lbl_aviso.text = "Error al guardar en Galería."

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
