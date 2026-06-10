from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.metrics import dp
import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

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
        if not criterio:
            self.lbl_estado.text = "Ingresa un nombre para buscar."
            return

        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        # Buscamos coincidencias en cualquier parte del texto
        cursor.execute("SELECT nombre, precio FROM productos WHERE nombre LIKE ? COLLATE NOCASE ORDER BY nombre ASC", (f"%{criterio}%",))
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            self.input_nombre.text = criterio
            self.input_precio.text = ""
            self.lbl_estado.text = "No existe. Podes crearlo con ese nombre."
            self.btn_guardar.disabled = False
            self.btn_editar.disabled = True
            self.btn_borrar.disabled = True
        elif len(resultados) == 1:
            # Si hay uno solo, lo clava directo como antes
            self.cargar_producto_en_campos(resultados[0][0], resultados[0][1])
        else:
            # Si hay más de uno, abre la ventana flotante para elegir
            self.mostrar_popup_coincidencias(resultados)

    def mostrar_popup_coincidencias(self, coincidencias):
        layout_popup = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        scroll = ScrollView(size_hint=(1, 1))
        lista_botones = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        lista_botones.bind(minimum_height=lista_botones.setter('height'))

        popup = Popup(title='Selecciona el producto correcto', content=layout_popup, size_hint=(0.9, 0.7), auto_dismiss=True)

        for nombre, precio in coincidencias:
            btn_prod = Button(text=f"{nombre}  -  ${precio:,.2f}", size_hint_y=None, height=dp(45), halign='left', text_size=(dp(250), None))
            # Usamos un truco de Kivy para pasarle el producto seleccionado al botón
            btn_prod.bind(on_release=lambda instance, n=nombre, p=precio: self.seleccionar_desde_popup(n, p, popup))
            lista_botones.add_widget(btn_prod)

        scroll.add_widget(lista_botones)
        layout_popup.add_widget(scroll)
        
        btn_cerrar = Button(text="CANCELAR", size_hint_y=None, height=dp(45), background_color=(0.6, 0.1, 0.1, 1))
        btn_cerrar.bind(on_release=popup.dismiss)
        layout_popup.add_widget(btn_cerrar)
        
        popup.open()

    def seleccionar_desde_popup(self, nombre, precio, popup):
        self.cargar_producto_en_campos(nombre, precio)
        popup.dismiss()

    def cargar_producto_en_campos(self, nombre, precio):
        self.input_nombre.text = nombre
        self.input_precio.text = str(precio)
        self.lbl_estado.text = "Producto encontrado."
        self.btn_guardar.disabled = True
        self.btn_editar.disabled = False
        self.btn_borrar.disabled = False
        self.input_buscar.text = ""

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

            margen_izq = 80
            margen_der = 640
            separacion_y = 26
            
            ancho = 720
            alto = 280 + (len(items) * separacion_y)
            imagen = Image.new("RGB", (ancho, alto), "white")
            lienzo = ImageDraw.Draw(imagen)

            try:
                fuente_titulo = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 78)
                fuente_subtitulo_wp = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 52)
                fuente_texto_bold = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 26)
                fuente_texto = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 26)
            except:
                fuente_titulo = ImageFont.load_default()
                fuente_subtitulo_wp = ImageFont.load_default()
                fuente_texto_bold = ImageFont.load_default()
                fuente_texto = ImageFont.load_default()

            texto_titulo = "LISTA DE PRECIOS"
            try:
                bbox = lienzo.textbbox((0, 0), texto_titulo, font=fuente_titulo)
                ancho_texto = bbox[2] - bbox[0]
            except:
                ancho_texto = 500
            x_centrado = (ancho - ancho_texto) // 2
            lienzo.text((x_centrado, 25), texto_titulo, fill="black", font=fuente_titulo)

            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            texto_fecha = f"Fecha: {fecha_actual}"
            try:
                bbox_f = lienzo.textbbox((0, 0), texto_fecha, font=fuente_texto)
                ancho_fecha = bbox_f[2] - bbox_f[0]
            except:
                ancho_fecha = 150
            lienzo.text((margen_der - ancho_fecha, 115), texto_fecha, fill="black", font=fuente_texto)

            lienzo.text((margen_izq, 115), "PEDIDOS WHATSAPP: 1123017122", fill="green", font=fuente_subtitulo_wp)
            lienzo.line([(margen_izq, 185), (margen_der, 185)], fill="black", width=3)

            lienzo.text((margen_izq, 195), "ARTICULOS", fill="black", font=fuente_texto_bold)
            
            texto_sub_precio = "PRECIOS"
            try:
                bbox_sp = lienzo.textbbox((0, 0), texto_sub_precio, font=fuente_texto_bold)
                ancho_sp = bbox_sp[2] - bbox_sp[0]
            except:
                ancho_sp = 100
            lienzo.text((margen_der - ancho_sp, 195), texto_sub_precio, fill="black", font=fuente_texto_bold)
            
            lienzo.line([(margen_izq, 230), (margen_der, 230)], fill="grey", width=2)

            y = 245
            for prod, precio in items:
                lienzo.text((margen_izq, y), str(prod), fill="black", font=fuente_texto)
                
                texto_precio = f"${precio:,.2f}"
                try:
                    bbox_p = lienzo.textbbox((0, 0), texto_precio, font=fuente_texto)
                    ancho_p = bbox_p[2] - bbox_p[0]
                except:
                    ancho_p = 80
                lienzo.text((margen_der - ancho_p, y), texto_precio, fill="black", font=fuente_texto)
                
                y += separacion_y

            lienzo.line([(margen_izq, y + 10), (margen_der, y + 10)], fill="grey", width=2)

            ruta_app = App.get_running_app().user_data_dir
            temp_path = os.path.join(ruta_app, "temp_lista.png")
            imagen.save(temp_path)

            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            BitmapFactory = autoclass('android.graphics.BitmapFactory')
            MediaStore_Images_Media = autoclass('android.provider.MediaStore$Images$Media')
            
            actividad = PythonActivity.mActivity
            contenido_resolver = actividad.getContentResolver()
            bitmap = BitmapFactory.decodeFile(temp_path)
            
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
