import tkinter as tk
from tkinter import messagebox, ttk
import json
from PIL import Image, ImageTk
import os
import re

# Cargar la base de datos
with open("mutantes.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Aplanar lista de personajes
personajes = []
for nivel in data["Mutantes"].values():
    personajes.extend(nivel)

# Atributos a excluir
ATRIBUTOS_EXCLUIDOS = ["Nombre", "Sexo", "Poder", "imagen", "Imagen"]

# Obtener atributos válidos para preguntas
atributos_preguntas = [key for key in personajes[0].keys() if key not in ATRIBUTOS_EXCLUIDOS]

class AkinatorMutante:
    def __init__(self, root):
        self.root = root
        self.root.title("Akinator Mutante Definitivo")
        self.root.geometry("750x700")
        
        # Variables de estado
        self.preguntas_restantes = atributos_preguntas.copy()
        self.personajes_restantes = personajes.copy()
        self.atributos_confirmados = {}
        self.current_image = None
        
        # Configurar interfaz
        self.setup_ui()
        self.hacer_pregunta()

    def setup_ui(self):
        # Frame principal para preguntas
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=20)
        
        # Etiqueta de pregunta
        self.label = tk.Label(self.main_frame, text="¿Tu personaje tiene esta característica?", 
                            font=("Arial", 14, "bold"), fg="#333")
        self.label.pack()
        
        # Pregunta actual
        self.pregunta_label = tk.Label(self.main_frame, text="", 
                                     font=("Arial", 16, "bold"), fg="#0066cc")
        self.pregunta_label.pack(pady=15)
        
        # Frame para botones
        self.btn_frame = tk.Frame(self.main_frame)
        self.btn_frame.pack(pady=10)
        
        # Botones Sí/No
        self.btn_si = tk.Button(self.btn_frame, text="Sí", command=lambda: self.responder(True), 
                              width=10, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.btn_si.pack(side=tk.LEFT, padx=20)
        
        self.btn_no = tk.Button(self.btn_frame, text="No", command=lambda: self.responder(False), 
                              width=10, bg="#f44336", fg="white", font=("Arial", 12))
        self.btn_no.pack(side=tk.RIGHT, padx=20)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", 
                                      length=300, mode="determinate")
        self.progress.pack(pady=10)
        self.progress["maximum"] = len(atributos_preguntas)
        
        # Frame para resultados
        self.result_frame = tk.Frame(self.root)
        
        # Contenedor de imagen con borde
        self.img_container = tk.Frame(self.result_frame, bd=2, relief="groove")
        self.img_container.pack(pady=10)
        
        # Label para imagen
        self.imagen_label = tk.Label(self.img_container)
        self.imagen_label.pack()
        
        # Frame para información del personaje
        self.info_frame = tk.Frame(self.result_frame)
        self.info_frame.pack(pady=10)
        
        # Etiquetas de información
        self.nombre_label = tk.Label(self.info_frame, text="", font=("Arial", 18, "bold"), fg="#333")
        self.nombre_label.pack()
        
        self.poder_label = tk.Label(self.info_frame, text="", font=("Arial", 14))
        self.poder_label.pack(pady=5)
        
        self.afiliaciones_label = tk.Label(self.info_frame, text="", font=("Arial", 14))
        self.afiliaciones_label.pack(pady=5)
        
        # Botón de reinicio
        self.btn_reiniciar = tk.Button(self.result_frame, text="Jugar otra vez", 
                                     command=self.reiniciar_completo,
                                     font=("Arial", 12), bg="#2196F3", fg="white")
        
        # Frame para atributos específicos
        self.atributos_frame = tk.Frame(self.result_frame)
        self.atributos_text = tk.Text(self.atributos_frame, height=10, width=40,
                                     font=("Arial", 11), wrap="word")
        self.scroll = ttk.Scrollbar(self.atributos_frame, orient="vertical", 
                                  command=self.atributos_text.yview)
        self.atributos_text.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.atributos_text.pack(side="left", fill="both", expand=True)

    def normalizar_nombre_archivo(self, nombre):
        """Convierte el nombre del personaje a formato de nombre de archivo válido"""
        # Eliminar espacios y caracteres especiales
        nombre = re.sub(r'[^\w]', '', nombre)  # Elimina todo lo que no sea alfanumérico
        nombre = nombre.lower()  # Convertir a minúsculas
        return nombre + ".jpg"  # Agregar extensión

    def hacer_pregunta(self):
        # Limpiar frame de resultados
        self.result_frame.pack_forget()
        self.main_frame.pack(pady=20)
        
        # Verificar si tenemos resultado final
        if len(self.personajes_restantes) == 1:
            self.mostrar_resultado_detallado()
            return
            
        if not self.personajes_restantes:
            self.mostrar_mensaje("No encontré ningún personaje con esas características")
            self.reiniciar_completo()
            return
            
        # Obtener siguiente pregunta válida
        while self.preguntas_restantes:
            pregunta = self.preguntas_restantes.pop(0)
            if pregunta not in ATRIBUTOS_EXCLUIDOS:
                self.pregunta_actual = pregunta
                self.pregunta_label.config(text=self.formatear_pregunta(pregunta))
                self.progress["value"] = len(atributos_preguntas) - len(self.preguntas_restantes)
                return
        
        # Si no hay más preguntas
        self.mostrar_resultado_detallado()

    def formatear_pregunta(self, texto):
        texto = texto.replace("_", " ").replace("Afiliacion ", "")
        return f"¿{texto.capitalize()}?"

    def responder(self, respuesta):
        if self.pregunta_actual in ATRIBUTOS_EXCLUIDOS:
            self.hacer_pregunta()
            return
            
        # Filtrar personajes
        self.personajes_restantes = [
            p for p in self.personajes_restantes 
            if p.get(self.pregunta_actual) == respuesta
        ]
        
        if respuesta:
            self.atributos_confirmados[self.pregunta_actual] = True
        
        self.hacer_pregunta()

    def mostrar_resultado_detallado(self):
        # Cambiar a pantalla de resultados
        self.main_frame.pack_forget()
        self.result_frame.pack(pady=20)
        
        if not self.personajes_restantes:
            self.nombre_label.config(text="No encontré ningún personaje")
            self.btn_reiniciar.pack(pady=20)
            return
            
        personaje = self.personajes_restantes[0]
        
        # Mostrar información principal
        self.nombre_label.config(text=f"¡Personaje identificado!\n{personaje['Nombre']}")
        self.poder_label.config(text=f"Poder: {personaje['Poder']}")
        
        # Mostrar afiliaciones
        afiliaciones = self.obtener_afiliaciones(personaje)
        self.afiliaciones_label.config(text=f"Afiliaciones: {afiliaciones if afiliaciones else 'Ninguna'}")
        
        # Mostrar imagen con nombre normalizado
        nombre_archivo = self.normalizar_nombre_archivo(personaje['Nombre'])
        self.mostrar_imagen_personaje(nombre_archivo)
        
        # Mostrar atributos adicionales
        self.mostrar_atributos_adicionales(personaje)
        
        self.btn_reiniciar.pack(pady=20)
        self.atributos_frame.pack(pady=10)

    def mostrar_imagen_personaje(self, nombre_archivo):
        # Limpiar imagen anterior
        self.imagen_label.config(image="", text="Cargando imagen...")
        
        # Ruta a la imagen
        ruta_imagen = os.path.join("imagenes", nombre_archivo)
        
        # Verificar si la imagen existe
        if not os.path.exists(ruta_imagen):
            self.imagen_label.config(text=f"Imagen no disponible\n({nombre_archivo})")
            return
            
        try:
            # Cargar y redimensionar imagen
            imagen_pil = Image.open(ruta_imagen)
            imagen_pil = imagen_pil.resize((300, 300), Image.Resampling.LANCZOS)
            
            # Convertir a formato Tkinter
            imagen_tk = ImageTk.PhotoImage(imagen_pil)
            
            # Actualizar label y mantener referencia
            self.imagen_label.config(image=imagen_tk)
            self.imagen_label.image = imagen_tk
            
        except Exception as e:
            self.imagen_label.config(text=f"Error cargando imagen:\n{str(e)}")

    def mostrar_atributos_adicionales(self, personaje):
        # Limpiar texto anterior
        self.atributos_text.config(state=tk.NORMAL)
        self.atributos_text.delete(1.0, tk.END)
        
        # Encabezado
        self.atributos_text.insert(tk.END, "Atributos adicionales:\n", "header")
        self.atributos_text.tag_configure("header", font=("Arial", 12, "bold"))
        
        # Mostrar todos los atributos (excepto los excluidos)
        for atributo, valor in personaje.items():
            if atributo not in ATRIBUTOS_EXCLUIDOS:
                nombre_atributo = atributo.replace("_", " ").capitalize()
                self.atributos_text.insert(tk.END, f"{nombre_atributo}: ", "bold")
                self.atributos_text.insert(tk.END, f"{valor}\n")
        
        self.atributos_text.tag_configure("bold", font=("Arial", 11, "bold"))
        self.atributos_text.config(state=tk.DISABLED)

    def obtener_afiliaciones(self, personaje):
        afiliaciones = []
        if personaje.get("Afiliacion_X-Men", False):
            afiliaciones.append("X-Men")
        if personaje.get("Afiliacion_Krakoa", False):
            afiliaciones.append("Krakoa")
        if personaje.get("Afiliacion_Imperio_Shiar", False):
            afiliaciones.append("Imperio Shi'ar")
        if personaje.get("Afiliacion_X-Force", False):
            afiliaciones.append("X-Force")
        if personaje.get("Afiliacion_4_Fantasticos", False):
            afiliaciones.append("4 Fantásticos")
        return ", ".join(afiliaciones)

    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Resultado", mensaje)

    def reiniciar_completo(self):
        # Destruir y recrear la ventana para un reinicio limpio
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = AkinatorMutante(root)
    root.mainloop()