#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Software FJ
Curso: Programación - UNAD
Autor: [Tu Nombre]
Descripción: Sistema orientado a objetos con interfaz gráfica Tkinter,
             manejo robusto de excepciones y logging de eventos.
"""

import logging
import sys
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGGING
# ============================================================================

def configurar_logger():
    """Configura el logger global del sistema."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
    
    file_handler = logging.FileHandler("eventos.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = configurar_logger()
logger.info("=" * 60)
logger.info("INICIANDO SISTEMA SOFTWARE FJ")
logger.info("=" * 60)


# ============================================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================================

class SoftwareFJException(Exception):
    """Excepción base del sistema."""
    pass

class ClienteInvalidoError(SoftwareFJException):
    """Error en datos del cliente."""
    pass

class ServicioNoDisponibleError(SoftwareFJException):
    """Error en creación de servicio."""
    pass

class ReservaInvalidaError(SoftwareFJException):
    """Error en reserva."""
    pass

class ParametroFaltanteError(SoftwareFJException):
    """Falta un parámetro obligatorio."""
    pass

class CalculoInconsistenteError(SoftwareFJException):
    """Error en cálculo de costos."""
    pass

class DuracionInvalidaError(ReservaInvalidaError):
    """Duración inválida."""
    pass


# ============================================================================
# 3. CLASE ABSTRACTA BASE
# ============================================================================

class EntidadBase(ABC):
    """Clase abstracta base para todas las entidades."""
    
    def __init__(self, id_entidad: str):
        if not id_entidad or len(id_entidad.strip()) == 0:
            raise ParametroFaltanteError("El ID de la entidad no puede estar vacío")
        self._id = id_entidad.strip()
    
    @abstractmethod
    def mostrar_informacion(self) -> str:
        pass
    
    @property
    def id(self) -> str:
        return self._id


# ============================================================================
# 4. CLASE CLIENTE
# ============================================================================

class Cliente(EntidadBase):
    """Representa un cliente con validaciones robustas."""
    
    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        super().__init__(id_cliente)
        self._nombre = None
        self._email = None
        self._telefono = None
        
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        
        logger.info(f"Nuevo cliente creado: {self._nombre} (ID: {self._id})")
    
    @property
    def nombre(self) -> str:
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 3:
            raise ClienteInvalidoError(f"El nombre '{valor}' es inválido. Debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, valor: str):
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron_email, valor):
            raise ClienteInvalidoError(f"El email '{valor}' no tiene un formato válido.")
        self._email = valor.strip()
    
    @property
    def telefono(self) -> str:
        return self._telefono
    
    @telefono.setter
    def telefono(self, valor: str):
        if not valor or len(valor.strip()) < 7:
            raise ClienteInvalidoError(f"El teléfono '{valor}' es inválido. Debe tener al menos 7 dígitos.")
        self._telefono = valor.strip()
    
    def mostrar_informacion(self) -> str:
        return f"Cliente: {self.nombre} | Email: {self.email} | Tel: {self.telefono}"


# ============================================================================
# 5. CLASE ABSTRACTA SERVICIO
# ============================================================================

class Servicio(EntidadBase, ABC):
    """Clase abstracta para servicios."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float):
        super().__init__(id_servicio)
        self._nombre = None
        self._precio_base = None
        
        self.nombre = nombre
        self.precio_base = precio_base
        
        logger.debug(f"Servicio '{self.nombre}' creado con precio base {self.precio_base}")
    
    @property
    def nombre(self) -> str:
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 3:
            raise ServicioNoDisponibleError(f"El nombre del servicio '{valor}' es inválido.")
        self._nombre = valor.strip()
    
    @property
    def precio_base(self) -> float:
        return self._precio_base
    
    @precio_base.setter
    def precio_base(self, valor: float):
        if valor <= 0:
            raise ServicioNoDisponibleError(f"El precio base {valor} debe ser mayor a cero.")
        self._precio_base = valor
    
    @abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        pass
    
    @abstractmethod
    def describir_servicio(self) -> str:
        pass
    
    def mostrar_informacion(self) -> str:
        return f"Servicio: {self.nombre} (ID: {self.id}) - ${self.precio_base:.2f}"


# ============================================================================
# 6. SERVICIOS ESPECIALIZADOS
# ============================================================================

class ReservaSalas(Servicio):
    """Servicio de reserva de salas."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, tiene_proyector: bool = False):
        super().__init__(id_servicio, nombre, precio_base)
        self.tiene_proyector = tiene_proyector
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        if duracion <= 0:
            raise DuracionInvalidaError(f"Duración {duracion} inválida para reserva de sala.")
        
        costo = self.precio_base * duracion
        if self.tiene_proyector:
            costo += 50
        
        descuento = kwargs.get('descuento', 0)
        if descuento < 0 or descuento > 100:
            raise CalculoInconsistenteError(f"Descuento {descuento}% inválido.")
        costo = costo * (1 - descuento / 100)
        
        return round(costo, 2)
    
    def describir_servicio(self) -> str:
        proyector = "con proyector" if self.tiene_proyector else "sin proyector"
        return f"Reserva de sala {proyector}. ${self.precio_base:.2f}/hora"


class AlquilerEquipos(Servicio):
    """Servicio de alquiler de equipos."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, requiere_seguro: bool = False):
        super().__init__(id_servicio, nombre, precio_base)
        self.requiere_seguro = requiere_seguro
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        if duracion <= 0:
            raise DuracionInvalidaError(f"Duración {duracion} inválida para alquiler de equipos.")
        
        costo = self.precio_base * duracion
        if self.requiere_seguro:
            costo += 20 * duracion
        
        impuesto = kwargs.get('impuesto', 0)
        if impuesto < 0:
            raise CalculoInconsistenteError(f"Impuesto {impuesto}% no puede ser negativo.")
        costo = costo * (1 + impuesto / 100)
        
        return round(costo, 2)
    
    def describir_servicio(self) -> str:
        seguro = "con seguro" if self.requiere_seguro else "sin seguro"
        return f"Alquiler de equipos {seguro}. ${self.precio_base:.2f}/día"


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada."""
    
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, nivel_experto: str = "junior"):
        super().__init__(id_servicio, nombre, precio_base)
        niveles_validos = ["junior", "senior", "master"]
        if nivel_experto.lower() not in niveles_validos:
            raise ServicioNoDisponibleError(f"Nivel '{nivel_experto}' no válido. Opciones: junior, senior, master")
        self.nivel_experto = nivel_experto.lower()
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        if duracion <= 0:
            raise DuracionInvalidaError(f"Duración {duracion} inválida para asesoría.")
        
        multiplicador = {"junior": 1.0, "senior": 1.5, "master": 2.0}
        costo = self.precio_base * duracion * multiplicador[self.nivel_experto]
        
        descuento_fidelidad = kwargs.get('descuento_fidelidad', 0)
        if descuento_fidelidad < 0 or descuento_fidelidad > 100:
            raise CalculoInconsistenteError(f"Descuento {descuento_fidelidad}% inválido.")
        costo = costo * (1 - descuento_fidelidad / 100)
        
        return round(costo, 2)
    
    def describir_servicio(self) -> str:
        niveles = {"junior": "Junior", "senior": "Senior", "master": "Master"}
        return f"Asesoría {niveles[self.nivel_experto]}. ${self.precio_base:.2f}/hora"


# ============================================================================
# 7. CLASE RESERVA
# ============================================================================

class Reserva(EntidadBase):
    """Integra cliente, servicio, duración y estado."""
    
    ESTADOS = ["PENDIENTE", "CONFIRMADA", "CANCELADA", "COMPLETADA"]
    
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: float,
                 parametros_extra: Optional[Dict[str, Any]] = None):
        super().__init__(id_reserva)
        self._cliente = None
        self._servicio = None
        self._duracion = None
        self._estado = "PENDIENTE"
        self._parametros_extra = parametros_extra or {}
        self.fecha_creacion = datetime.now()
        self.costo_total = 0.0
        
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        
        logger.info(f"Reserva {self.id} creada para {cliente.nombre} - {servicio.nombre}")
    
    @property
    def cliente(self) -> Cliente:
        return self._cliente
    
    @cliente.setter
    def cliente(self, valor: Cliente):
        if not isinstance(valor, Cliente):
            raise ReservaInvalidaError("El cliente debe ser una instancia de Cliente.")
        self._cliente = valor
    
    @property
    def servicio(self) -> Servicio:
        return self._servicio
    
    @servicio.setter
    def servicio(self, valor: Servicio):
        if not isinstance(valor, Servicio):
            raise ReservaInvalidaError("El servicio debe ser una instancia de Servicio.")
        self._servicio = valor
    
    @property
    def duracion(self) -> float:
        return self._duracion
    
    @duracion.setter
    def duracion(self, valor: float):
        if valor <= 0:
            raise DuracionInvalidaError(f"La duración {valor} debe ser positiva.")
        self._duracion = valor
    
    @property
    def estado(self) -> str:
        return self._estado
    
    def confirmar(self):
        """Confirma la reserva y calcula el costo total."""
        try:
            if self._estado != "PENDIENTE":
                raise ReservaInvalidaError(f"No se puede confirmar reserva en estado {self._estado}")
            
            self.costo_total = self._servicio.calcular_costo(self._duracion, **self._parametros_extra)
            self._estado = "CONFIRMADA"
            logger.info(f"Reserva {self.id} CONFIRMADA. Costo: ${self.costo_total:.2f}")
        except Exception as e:
            raise ReservaInvalidaError(f"Error al confirmar reserva {self.id}") from e
    
    def cancelar(self):
        """Cancela la reserva."""
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError(f"La reserva {self.id} ya está cancelada.")
        if self._estado == "COMPLETADA":
            raise ReservaInvalidaError(f"No se puede cancelar una reserva completada.")
        
        self._estado = "CANCELADA"
        logger.info(f"Reserva {self.id} CANCELADA")
    
    def completar(self):
        """Completa la reserva."""
        if self._estado != "CONFIRMADA":
            raise ReservaInvalidaError(f"Solo se pueden completar reservas confirmadas.")
        self._estado = "COMPLETADA"
        logger.info(f"Reserva {self.id} COMPLETADA")
    
    def mostrar_informacion(self) -> str:
        return f"{self.id} | {self.cliente.nombre} | {self.servicio.nombre} | {self.duracion}h | {self.estado} | ${self.costo_total:.2f}"


# ============================================================================
# FUNCIÓN AUXILIAR PARA OBTENER TIPO DE SERVICIO
# ============================================================================

def tipo_servicio_str(servicio: Servicio) -> str:
    """Retorna el tipo de servicio como string."""
    if isinstance(servicio, ReservaSalas):
        return "Reserva de Salas"
    elif isinstance(servicio, AlquilerEquipos):
        return "Alquiler de Equipos"
    elif isinstance(servicio, AsesoriaEspecializada):
        return "Asesoría Especializada"
    return "Desconocido"


# ============================================================================
# 8. APLICACIÓN PRINCIPAL CON TKINTER
# ============================================================================

class AplicacionSoftwareFJ:
    """Aplicación principal con interfaz gráfica Tkinter."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Sistema de Gestión de Clientes, Servicios y Reservas")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        
        # Configurar estilo
        self.root.configure(bg='#f0f0f0')
        
        # Almacenamiento en memoria
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []
        
        # Contadores para IDs automáticos
        self.contador_clientes = 1
        self.contador_servicios = 1
        self.contador_reservas = 1
        
        # Cargar datos de ejemplo
        self.cargar_datos_ejemplo()
        
        # Configurar la interfaz
        self.configurar_interfaz()
        
        logger.info("Interfaz gráfica inicializada correctamente")
    
    def cargar_datos_ejemplo(self):
        """Carga datos de ejemplo para demostrar el funcionamiento."""
        try:
            # Clientes de ejemplo
            cliente1 = Cliente("C001", "Ana María López", "ana.lopez@email.com", "3001234567")
            cliente2 = Cliente("C002", "Carlos Pérez Rodríguez", "carlos.perez@email.com", "3109876543")
            self.clientes.extend([cliente1, cliente2])
            self.contador_clientes = 3
            
            # Servicios de ejemplo
            servicio1 = ReservaSalas("S001", "Sala Ejecutiva Premium", 25.0, tiene_proyector=True)
            servicio2 = AlquilerEquipos("S002", "Kit de Cómputo Profesional", 40.0, requiere_seguro=True)
            servicio3 = AsesoriaEspecializada("S003", "Consultoría Avanzada Python", 35.0, nivel_experto="senior")
            servicio4 = ReservaSalas("S004", "Sala Básica", 15.0, tiene_proyector=False)
            self.servicios.extend([servicio1, servicio2, servicio3, servicio4])
            self.contador_servicios = 5
            
            logger.info("Datos de ejemplo cargados correctamente")
        except Exception as e:
            logger.error(f"Error cargando datos de ejemplo: {e}")
    
    def configurar_interfaz(self):
        """Configura todos los elementos de la interfaz gráfica."""
        # Barra de menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Ver Logs", command=self.ver_logs)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        
        menu_datos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datos", menu=menu_datos)
        menu_datos.add_command(label="Exportar Listados", command=self.exportar_listados)
        
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.acerca_de)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_servicios = ttk.Frame(self.notebook)
        self.tab_reservas = ttk.Frame(self.notebook)
        self.tab_listados = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_clientes, text="👥 Clientes")
        self.notebook.add(self.tab_servicios, text="🔧 Servicios")
        self.notebook.add(self.tab_reservas, text="📅 Reservas")
        self.notebook.add(self.tab_listados, text="📋 Listados")
        
        # Configurar cada pestaña
        self.configurar_tab_clientes()
        self.configurar_tab_servicios()
        self.configurar_tab_reservas()
        self.configurar_tab_listados()
    
    # ==================== PESTAÑA CLIENTES ====================
    def configurar_tab_clientes(self):
        """Configura el formulario y listado de clientes."""
        # Frame del formulario
        frame_form = ttk.LabelFrame(self.tab_clientes, text="Registrar Nuevo Cliente", padding=10)
        frame_form.pack(fill=tk.X, padx=10, pady=10)
        
        # Campos del formulario
        ttk.Label(frame_form, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_id_cliente = ttk.Entry(frame_form, width=15)
        self.entry_id_cliente.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_form, text="(dejar vacío para auto-generar)").grid(row=0, column=2, sticky=tk.W, padx=5)
        
        ttk.Label(frame_form, text="Nombre:*").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_nombre = ttk.Entry(frame_form, width=40)
        self.entry_nombre.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(frame_form, text="Email:*").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_email = ttk.Entry(frame_form, width=40)
        self.entry_email.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(frame_form, text="Teléfono:*").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_telefono = ttk.Entry(frame_form, width=20)
        self.entry_telefono.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Botones
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(frame_botones, text="Registrar Cliente", command=self.registrar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Limpiar", command=self.limpiar_form_cliente).pack(side=tk.LEFT, padx=5)
        
        # Listado de clientes
        frame_lista = ttk.LabelFrame(self.tab_clientes, text="Clientes Registrados", padding=10)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Nombre", "Email", "Teléfono")
        self.tree_clientes = ttk.Treeview(frame_lista, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=scrollbar.set)
        
        self.tree_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar listado
        self.actualizar_lista_clientes()
    
    def registrar_cliente(self):
        """Registra un nuevo cliente con validaciones."""
        try:
            id_cliente = self.entry_id_cliente.get().strip()
            if not id_cliente:
                id_cliente = f"C{self.contador_clientes:03d}"
            
            nombre = self.entry_nombre.get().strip()
            email = self.entry_email.get().strip()
            telefono = self.entry_telefono.get().strip()
            
            if not nombre or not email or not telefono:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            cliente = Cliente(id_cliente, nombre, email, telefono)
            self.clientes.append(cliente)
            self.contador_clientes += 1
            
            messagebox.showinfo("Éxito", f"Cliente {nombre} registrado correctamente")
            self.limpiar_form_cliente()
            self.actualizar_lista_clientes()
            self.actualizar_combo_clientes()
            logger.info(f"Cliente registrado: {nombre} (ID: {id_cliente})")
            
        except ClienteInvalidoError as e:
            messagebox.showerror("Error de validación", str(e))
            logger.error(f"Error validando cliente: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
            logger.error(f"Error inesperado: {e}")
    
    def limpiar_form_cliente(self):
        self.entry_id_cliente.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
    
    def actualizar_lista_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        for cliente in self.clientes:
            self.tree_clientes.insert("", tk.END, values=(
                cliente.id, cliente.nombre, cliente.email, cliente.telefono
            ))
    
    # ==================== PESTAÑA SERVICIOS ====================
    def configurar_tab_servicios(self):
        """Configura el formulario y listado de servicios."""
        frame_form = ttk.LabelFrame(self.tab_servicios, text="Registrar Nuevo Servicio", padding=10)
        frame_form.pack(fill=tk.X, padx=10, pady=10)
        
        # Tipo de servicio
        ttk.Label(frame_form, text="Tipo de Servicio:*").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.tipo_servicio = ttk.Combobox(frame_form, values=["Reserva de Salas", "Alquiler de Equipos", "Asesoría Especializada"], width=30)
        self.tipo_servicio.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.tipo_servicio.bind("<<ComboboxSelected>>", self.actualizar_campos_servicio)
        
        ttk.Label(frame_form, text="ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_id_servicio = ttk.Entry(frame_form, width=15)
        self.entry_id_servicio.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame_form, text="(dejar vacío para auto-generar)").grid(row=1, column=2, sticky=tk.W, padx=5)
        
        ttk.Label(frame_form, text="Nombre:*").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_nombre_servicio = ttk.Entry(frame_form, width=40)
        self.entry_nombre_servicio.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(frame_form, text="Precio Base:*").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_precio_base = ttk.Entry(frame_form, width=15)
        self.entry_precio_base.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Campos específicos
        self.frame_extra = ttk.Frame(frame_form)
        self.frame_extra.grid(row=4, column=0, columnspan=3, pady=10, sticky=tk.W)
        
        self.campos_extra = {}
        
        # Botones
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(frame_botones, text="Registrar Servicio", command=self.registrar_servicio).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Limpiar", command=self.limpiar_form_servicio).pack(side=tk.LEFT, padx=5)
        
        # Listado de servicios
        frame_lista = ttk.LabelFrame(self.tab_servicios, text="Servicios Registrados", padding=10)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Nombre", "Tipo", "Precio Base", "Detalles")
        self.tree_servicios = ttk.Treeview(frame_lista, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree_servicios.heading(col, text=col)
            if col == "Detalles":
                self.tree_servicios.column(col, width=300)
            else:
                self.tree_servicios.column(col, width=130)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_servicios.yview)
        self.tree_servicios.configure(yscrollcommand=scrollbar.set)
        
        self.tree_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.actualizar_lista_servicios()
    
    def actualizar_campos_servicio(self, event=None):
        """Actualiza los campos adicionales según el tipo de servicio."""
        for widget in self.frame_extra.winfo_children():
            widget.destroy()
        
        self.campos_extra.clear()
        tipo = self.tipo_servicio.get()
        
        if tipo == "Reserva de Salas":
            var = tk.BooleanVar()
            ttk.Checkbutton(self.frame_extra, text="¿Incluye proyector? (costo adicional $50)", variable=var).pack(anchor=tk.W)
            self.campos_extra["tiene_proyector"] = var
        
        elif tipo == "Alquiler de Equipos":
            var = tk.BooleanVar()
            ttk.Checkbutton(self.frame_extra, text="¿Requiere seguro? (+$20 por día)", variable=var).pack(anchor=tk.W)
            self.campos_extra["requiere_seguro"] = var
        
        elif tipo == "Asesoría Especializada":
            ttk.Label(self.frame_extra, text="Nivel del experto:").pack(anchor=tk.W)
            combo = ttk.Combobox(self.frame_extra, values=["junior", "senior", "master"], width=15)
            combo.pack(anchor=tk.W)
            combo.set("junior")
            self.campos_extra["nivel_experto"] = combo
    
    def registrar_servicio(self):
        """Registra un nuevo servicio."""
        try:
            tipo = self.tipo_servicio.get()
            if not tipo:
                messagebox.showerror("Error", "Seleccione un tipo de servicio")
                return
            
            id_servicio = self.entry_id_servicio.get().strip()
            if not id_servicio:
                id_servicio = f"S{self.contador_servicios:03d}"
            
            nombre = self.entry_nombre_servicio.get().strip()
            
            try:
                precio_base = float(self.entry_precio_base.get().strip())
            except ValueError:
                raise ValueError("El precio base debe ser un número válido")
            
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            servicio = None
            
            if tipo == "Reserva de Salas":
                tiene_proyector = self.campos_extra.get("tiene_proyector", tk.BooleanVar()).get() if "tiene_proyector" in self.campos_extra else False
                servicio = ReservaSalas(id_servicio, nombre, precio_base, tiene_proyector)
            
            elif tipo == "Alquiler de Equipos":
                requiere_seguro = self.campos_extra.get("requiere_seguro", tk.BooleanVar()).get() if "requiere_seguro" in self.campos_extra else False
                servicio = AlquilerEquipos(id_servicio, nombre, precio_base, requiere_seguro)
            
            elif tipo == "Asesoría Especializada":
                nivel = self.campos_extra.get("nivel_experto").get() if self.campos_extra.get("nivel_experto") else "junior"
                servicio = AsesoriaEspecializada(id_servicio, nombre, precio_base, nivel)
            
            if servicio:
                self.servicios.append(servicio)
                self.contador_servicios += 1
                messagebox.showinfo("Éxito", f"Servicio {nombre} registrado correctamente")
                self.limpiar_form_servicio()
                self.actualizar_lista_servicios()
                self.actualizar_combo_servicios()
                logger.info(f"Servicio registrado: {nombre} (ID: {id_servicio})")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except ServicioNoDisponibleError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
    
    def limpiar_form_servicio(self):
        self.entry_id_servicio.delete(0, tk.END)
        self.entry_nombre_servicio.delete(0, tk.END)
        self.entry_precio_base.delete(0, tk.END)
        self.tipo_servicio.set("")
        self.actualizar_campos_servicio()
    
    def actualizar_lista_servicios(self):
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        
        for servicio in self.servicios:
            tipo = tipo_servicio_str(servicio)
            self.tree_servicios.insert("", tk.END, values=(
                servicio.id, servicio.nombre, tipo, f"${servicio.precio_base:.2f}", servicio.describir_servicio()
            ))
    
    # ==================== PESTAÑA RESERVAS ====================
    def configurar_tab_reservas(self):
        """Configura el formulario y listado de reservas."""
        frame_form = ttk.LabelFrame(self.tab_reservas, text="Crear Nueva Reserva", padding=10)
        frame_form.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(frame_form, text="Cliente:*").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_cliente = ttk.Combobox(frame_form, width=45)
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(frame_form, text="Servicio:*").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_servicio = ttk.Combobox(frame_form, width=45)
        self.combo_servicio.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(frame_form, text="Duración (horas/días):*").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_duracion = ttk.Entry(frame_form, width=15)
        self.entry_duracion.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(frame_form, text="Parámetros extras (opcional):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_form, text="Ej: descuento=10, impuesto=19, descuento_fidelidad=15").grid(row=3, column=1, sticky=tk.W, padx=5)
        self.entry_extras = ttk.Entry(frame_form, width=50)
        self.entry_extras.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Botones
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botones, text="Crear y Confirmar Reserva", command=self.crear_reserva).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Limpiar", command=self.limpiar_form_reserva).pack(side=tk.LEFT, padx=5)
        
        # Listado de reservas
        frame_lista = ttk.LabelFrame(self.tab_reservas, text="Reservas Registradas", padding=10)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para botones de acción sobre reservas
        frame_acciones = ttk.Frame(frame_lista)
        frame_acciones.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_acciones, text="Cancelar Reserva Seleccionada", command=self.cancelar_reserva).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acciones, text="Completar Reserva Seleccionada", command=self.completar_reserva).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acciones, text="Actualizar Lista", command=self.actualizar_lista_reservas).pack(side=tk.LEFT, padx=5)
        
        columns = ("ID", "Cliente", "Servicio", "Duración", "Estado", "Costo Total")
        self.tree_reservas = ttk.Treeview(frame_lista, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree_reservas.heading(col, text=col)
            self.tree_reservas.column(col, width=140)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_reservas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar combos
        self.actualizar_combo_clientes()
        self.actualizar_combo_servicios()
        self.actualizar_lista_reservas()
    
    def actualizar_combo_clientes(self):
        """Actualiza el combobox de clientes."""
        valores = [f"{c.id} - {c.nombre}" for c in self.clientes]
        self.combo_cliente['values'] = valores
        if valores:
            self.combo_cliente.set(valores[0])
    
    def actualizar_combo_servicios(self):
        """Actualiza el combobox de servicios."""
        valores = [f"{s.id} - {s.nombre} ({tipo_servicio_str(s)})" for s in self.servicios]
        self.combo_servicio['values'] = valores
        if valores:
            self.combo_servicio.set(valores[0])
    
    def parsear_parametros_extras(self, texto: str) -> Dict[str, Any]:
        """Parsea los parámetros extras del formato 'clave=valor, clave2=valor2'."""
        params = {}
        if not texto.strip():
            return params
        
        try:
            partes = texto.split(',')
            for parte in partes:
                if '=' in parte:
                    clave, valor = parte.split('=', 1)
                    clave = clave.strip()
                    valor = valor.strip()
                    # Intentar convertir a número si es posible
                    try:
                        if '.' in valor:
                            params[clave] = float(valor)
                        else:
                            params[clave] = int(valor)
                    except ValueError:
                        params[clave] = valor
        except Exception as e:
            logger.warning(f"Error parseando parámetros extras: {e}")
        
        return params
    
    def crear_reserva(self):
        """Crea una nueva reserva."""
        try:
            # Obtener cliente seleccionado
            cliente_str = self.combo_cliente.get()
            if not cliente_str:
                messagebox.showerror("Error", "Seleccione un cliente")
                return
            
            cliente_id = cliente_str.split(" - ")[0]
            cliente = next((c for c in self.clientes if c.id == cliente_id), None)
            if not cliente:
                messagebox.showerror("Error", "Cliente no encontrado")
                return
            
            # Obtener servicio seleccionado
            servicio_str = self.combo_servicio.get()
            if not servicio_str:
                messagebox.showerror("Error", "Seleccione un servicio")
                return
            
            servicio_id = servicio_str.split(" - ")[0]
            servicio = next((s for s in self.servicios if s.id == servicio_id), None)
            if not servicio:
                messagebox.showerror("Error", "Servicio no encontrado")
                return
            
            # Obtener duración
            try:
                duracion = float(self.entry_duracion.get().strip())
                if duracion <= 0:
                    raise ValueError("La duración debe ser mayor a 0")
            except ValueError as e:
                messagebox.showerror("Error", f"Duración inválida: {e}")
                return
            
            # Parámetros extras
            parametros = self.parsear_parametros_extras(self.entry_extras.get().strip())
            
            # Crear reserva
            id_reserva = f"R{self.contador_reservas:03d}"
            reserva = Reserva(id_reserva, cliente, servicio, duracion, parametros)
            reserva.confirmar()
            
            self.reservas.append(reserva)
            self.contador_reservas += 1
            
            messagebox.showinfo("Éxito", f"Reserva creada y confirmada.\nCosto total: ${reserva.costo_total:.2f}")
            self.limpiar_form_reserva()
            self.actualizar_lista_reservas()
            logger.info(f"Reserva creada: {id_reserva} - Cliente: {cliente.nombre} - Costo: ${reserva.costo_total:.2f}")
            
        except ReservaInvalidaError as e:
            messagebox.showerror("Error en reserva", str(e))
            logger.error(f"Error creando reserva: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
            logger.error(f"Error inesperado: {e}")
    
    def cancelar_reserva(self):
        """Cancela la reserva seleccionada."""
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una reserva para cancelar")
            return
        
        item = seleccion[0]
        id_reserva = self.tree_reservas.item(item, 'values')[0]
        
        reserva = next((r for r in self.reservas if r.id == id_reserva), None)
        if reserva:
            try:
                reserva.cancelar()
                self.actualizar_lista_reservas()
                messagebox.showinfo("Éxito", f"Reserva {id_reserva} cancelada")
                logger.info(f"Reserva {id_reserva} cancelada")
            except ReservaInvalidaError as e:
                messagebox.showerror("Error", str(e))
    
    def completar_reserva(self):
        """Completa la reserva seleccionada."""
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una reserva para completar")
            return
        
        item = seleccion[0]
        id_reserva = self.tree_reservas.item(item, 'values')[0]
        
        reserva = next((r for r in self.reservas if r.id == id_reserva), None)
        if reserva:
            try:
                reserva.completar()
                self.actualizar_lista_reservas()
                messagebox.showinfo("Éxito", f"Reserva {id_reserva} completada")
                logger.info(f"Reserva {id_reserva} completada")
            except ReservaInvalidaError as e:
                messagebox.showerror("Error", str(e))
    
    def limpiar_form_reserva(self):
        self.entry_duracion.delete(0, tk.END)
        self.entry_extras.delete(0, tk.END)
    
    def actualizar_lista_reservas(self):
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        
        for reserva in self.reservas:
            self.tree_reservas.insert("", tk.END, values=(
                reserva.id, reserva.cliente.nombre, reserva.servicio.nombre, 
                f"{reserva.duracion}h", reserva.estado, f"${reserva.costo_total:.2f}"
            ))
    
    # ==================== PESTAÑA LISTADOS ====================
    def configurar_tab_listados(self):
        """Configura la pestaña de listados y reportes."""
        # Frame principal
        frame_principal = ttk.Frame(self.tab_listados)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones de acción
        frame_botones = ttk.Frame(frame_principal)
        frame_botones.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_botones, text="Actualizar Todos los Listados", 
                   command=self.actualizar_listados_completos).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Exportar a Archivo", 
                   command=self.exportar_listados).pack(side=tk.LEFT, padx=5)
        
        # Notebook interno para listados
        notebook_interno = ttk.Notebook(frame_principal)
        notebook_interno.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestaña de clientes
        frame_clientes_lista = ttk.Frame(notebook_interno)
        notebook_interno.add(frame_clientes_lista, text="Clientes")
        
        columns_clientes = ("ID", "Nombre", "Email", "Teléfono")
        self.tree_lista_clientes = ttk.Treeview(frame_clientes_lista, columns=columns_clientes, show="headings", height=12)
        for col in columns_clientes:
            self.tree_lista_clientes.heading(col, text=col)
            self.tree_lista_clientes.column(col, width=180)
        self.tree_lista_clientes.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de servicios
        frame_servicios_lista = ttk.Frame(notebook_interno)
        notebook_interno.add(frame_servicios_lista, text="Servicios")
        
        columns_servicios = ("ID", "Nombre", "Tipo", "Precio Base", "Descripción")
        self.tree_lista_servicios = ttk.Treeview(frame_servicios_lista, columns=columns_servicios, show="headings", height=12)
        for col in columns_servicios:
            self.tree_lista_servicios.heading(col, text=col)
            if col == "Descripción":
                self.tree_lista_servicios.column(col, width=350)
            else:
                self.tree_lista_servicios.column(col, width=120)
        self.tree_lista_servicios.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de reservas
        frame_reservas_lista = ttk.Frame(notebook_interno)
        notebook_interno.add(frame_reservas_lista, text="Reservas")
        
        columns_reservas = ("ID", "Cliente", "Servicio", "Duración", "Estado", "Costo")
        self.tree_lista_reservas = ttk.Treeview(frame_reservas_lista, columns=columns_reservas, show="headings", height=12)
        for col in columns_reservas:
            self.tree_lista_reservas.heading(col, text=col)
            self.tree_lista_reservas.column(col, width=140)
        self.tree_lista_reservas.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de estadísticas
        frame_estadisticas = ttk.Frame(notebook_interno)
        notebook_interno.add(frame_estadisticas, text="Estadísticas")
        
        self.txt_estadisticas = scrolledtext.ScrolledText(frame_estadisticas, wrap=tk.WORD, height=15)
        self.txt_estadisticas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cargar datos iniciales
        self.actualizar_listados_completos()
    
    def actualizar_listados_completos(self):
        """Actualiza todos los listados."""
        # Clientes
        for item in self.tree_lista_clientes.get_children():
            self.tree_lista_clientes.delete(item)
        for cliente in self.clientes:
            self.tree_lista_clientes.insert("", tk.END, values=(cliente.id, cliente.nombre, cliente.email, cliente.telefono))
        
        # Servicios
        for item in self.tree_lista_servicios.get_children():
            self.tree_lista_servicios.delete(item)
        for servicio in self.servicios:
            self.tree_lista_servicios.insert("", tk.END, values=(
                servicio.id, servicio.nombre, tipo_servicio_str(servicio), 
                f"${servicio.precio_base:.2f}", servicio.describir_servicio()
            ))
        
        # Reservas
        for item in self.tree_lista_reservas.get_children():
            self.tree_lista_reservas.delete(item)
        for reserva in self.reservas:
            self.tree_lista_reservas.insert("", tk.END, values=(
                reserva.id, reserva.cliente.nombre, reserva.servicio.nombre,
                f"{reserva.duracion}h", reserva.estado, f"${reserva.costo_total:.2f}"
            ))
        
        # Estadísticas
        self.txt_estadisticas.delete(1.0, tk.END)
        total_clientes = len(self.clientes)
        total_servicios = len(self.servicios)
        total_reservas = len(self.reservas)
        
        reservas_confirmadas = sum(1 for r in self.reservas if r.estado == "CONFIRMADA")
        reservas_canceladas = sum(1 for r in self.reservas if r.estado == "CANCELADA")
        reservas_completadas = sum(1 for r in self.reservas if r.estado == "COMPLETADA")
        
        ingreso_total = sum(r.costo_total for r in self.reservas if r.estado in ["CONFIRMADA", "COMPLETADA"])
        
        stats = f"""
{'='*60}
ESTADÍSTICAS DEL SISTEMA SOFTWARE FJ
{'='*60}

📊 RESÚMEN GENERAL:
──────────────────────────────────────────────────
• Total de clientes registrados: {total_clientes}
• Total de servicios disponibles: {total_servicios}
• Total de reservas procesadas: {total_reservas}

📋 DETALLE DE RESERVAS:
──────────────────────────────────────────────────
• Reservas confirmadas: {reservas_confirmadas}
• Reservas canceladas: {reservas_canceladas}
• Reservas completadas: {reservas_completadas}

💰 INGRESOS:
──────────────────────────────────────────────────
• Ingreso total generado: ${ingreso_total:,.2f}

📈 PROMEDIOS:
──────────────────────────────────────────────────
• Costo promedio por reserva: ${(ingreso_total / total_reservas if total_reservas > 0 else 0):,.2f}

📅 ÚLTIMA RESERVA:
──────────────────────────────────────────────────
{f"ID: {self.reservas[-1].id} - Cliente: {self.reservas[-1].cliente.nombre} - Costo: ${self.reservas[-1].costo_total:.2f}" if self.reservas else "No hay reservas aún"}

{'='*60}
Sistema funcionando de manera estable con manejo robusto de excepciones
{'='*60}
"""
        self.txt_estadisticas.insert(1.0, stats)
    
    # ==================== FUNCIONES DE MENÚ ====================
    def ver_logs(self):
        """Muestra el contenido del archivo de logs."""
        try:
            ventana_logs = tk.Toplevel(self.root)
            ventana_logs.title("Registro de Eventos - Software FJ")
            ventana_logs.geometry("800x500")
            
            txt_logs = scrolledtext.ScrolledText(ventana_logs, wrap=tk.WORD)
            txt_logs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            try:
                with open("eventos.log", "r", encoding='utf-8') as f:
                    contenido = f.read()
                txt_logs.insert(1.0, contenido)
            except FileNotFoundError:
                txt_logs.insert(1.0, "No se encontró el archivo de logs. Aún no se han registrado eventos.")
            
            ttk.Button(ventana_logs, text="Cerrar", command=ventana_logs.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo de logs: {e}")
    
    def exportar_listados(self):
        """Exporta los listados a un archivo de texto."""
        try:
            with open("reporte_software_fj.txt", "w", encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("SOFTWARE FJ - REPORTE COMPLETO DEL SISTEMA\n")
                f.write(f"Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("CLIENTES REGISTRADOS:\n")
                f.write("-" * 60 + "\n")
                for c in self.clientes:
                    f.write(f"  {c.id} | {c.nombre} | {c.email} | {c.telefono}\n")
                
                f.write("\nSERVICIOS DISPONIBLES:\n")
                f.write("-" * 60 + "\n")
                for s in self.servicios:
                    f.write(f"  {s.id} | {s.nombre} | {tipo_servicio_str(s)} | ${s.precio_base:.2f}\n")
                    f.write(f"      Descripción: {s.describir_servicio()}\n")
                
                f.write("\nRESERVAS REALIZADAS:\n")
                f.write("-" * 60 + "\n")
                for r in self.reservas:
                    f.write(f"  {r.id} | Cliente: {r.cliente.nombre} | Servicio: {r.servicio.nombre}\n")
                    f.write(f"      Duración: {r.duracion}h | Estado: {r.estado} | Costo: ${r.costo_total:.2f}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("FIN DEL REPORTE\n")
            
            messagebox.showinfo("Éxito", "Reporte exportado correctamente a 'reporte_software_fj.txt'")
            logger.info("Reporte exportado a archivo")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {e}")
    
    def acerca_de(self):
        """Muestra información acerca del sistema."""
        messagebox.showinfo("Acerca de", 
            "Sistema Integral de Gestión - Software FJ\n\n"
            "Versión: 1.0\n"
            "Curso: Programación - UNAD\n"
            "Código: 213023\n\n"
            "Sistema orientado a objetos con manejo robusto de excepciones\n"
            "e interfaz gráfica Tkinter.\n\n"
            "© 2024 - Todos los derechos reservados")


# ============================================================================
# 9. PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AplicacionSoftwareFJ(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Error crítico al iniciar la aplicación: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        print(f"Error fatal: {e}")