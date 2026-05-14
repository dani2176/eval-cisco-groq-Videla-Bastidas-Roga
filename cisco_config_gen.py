import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# =========================
# CARGAR VARIABLES .ENV
# =========================
load_dotenv()

# obtener API key
api_key = os.getenv("GROQ_API_KEY")

# validar API key
if not api_key:
    print("ERROR: No se encontró GROQ_API_KEY")
    exit()

# cliente Groq
client = Groq(api_key=api_key)

# =========================
# CREAR CARPETA CONFIGS
# =========================
if not os.path.exists("configs"):
    os.makedirs("configs")

# =========================
# SYSTEM PROMPT
# =========================
system_prompt = """
Eres un experto en Cisco IOS.

Tu tarea es generar SOLO configuraciones Cisco IOS válidas.

REGLAS:
- SOLO devolver comandos Cisco IOS
- NO explicar nada
- NO usar markdown
- NO usar bloques de código
- NO agregar texto extra
- La salida debe estar lista para copiar y pegar
"""

# =========================
# MENÚ
# =========================
print("===== GENERADOR CISCO IOS =====")
print("1. VLAN")
print("2. OSPF")
print("3. SUBNETTING")
print("1. VLAN")
print("2. OSPF")
print("3. SUBNETTING")
print("4. STATIC ROUTE")
print("5. DHCP")
print("6. ACL")
print("5. DHCP")
print("6. ACL")
print("7. PORT-SECURITY")

opcion = input("Seleccione opción: ")

prompt = ""
tipo = ""

# =====================================================
# ESCENARIO VLAN
# =====================================================
if opcion == "1":

    vlan = input("ID VLAN: ")

    # validar número
    if not vlan.isdigit():
        print("ERROR: VLAN inválida")
        exit()

    vlan = int(vlan)

    # validar rango VLAN
    if vlan < 1 or vlan > 4094:
        print("ERROR: VLAN fuera de rango")
        exit()

    nombre = input("Nombre VLAN: ")
    puerto = input("Puerto: ")

    tipo = "vlan"

    prompt = f"""
Crear VLAN {vlan}
Nombre {nombre}
Puerto {puerto}
"""

# =====================================================
# ESCENARIO OSPF
# =====================================================
elif opcion == "2":

    proceso = input("Proceso OSPF: ")

    # validar proceso
    if not proceso.isdigit():
        print("ERROR: proceso inválido")
        exit()

    red = input("Red: ")
    area = input("Área: ")

    # validar área
    if not area.isdigit():
        print("ERROR: área inválida")
        exit()

    tipo = "ospf"

    prompt = f"""
Configurar OSPF:
Proceso {proceso}
Red {red}
Área {area}
"""

# =====================================================
# ESCENARIO SUBNETTING
# =====================================================
elif opcion == "3":

    red = input("Red base: ")
    prefijo = input("Prefijo CIDR: ")
    subredes = input("Cantidad subredes: ")

    # validar prefijo
    if not prefijo.isdigit():
        print("ERROR: prefijo inválido")
        exit()

    prefijo = int(prefijo)

    if prefijo < 8 or prefijo > 30:
        print("ERROR: prefijo fuera de rango")
        exit()

    # validar subredes
    if not subredes.isdigit():
        print("ERROR: subredes inválidas")
        exit()

    tipo = "subnetting"

    prompt = f"""
Generar subnetting Cisco:
Red base {red}/{prefijo}
Cantidad subredes {subredes}
Asignar gateways válidos
"""
    
# ... (código anterior de tus compañeros) ...


elif opcion == "4":
    red_destino = input("Red destino: ")
    mascara = input("Máscara: ")
    gateway = input("Gateway: ")
    tipo = "static_route"
    prompt = f"""
    Configurar ruta estática:

    red destino {red_destino}
    mascara {mascara}
    gateway {gateway}
    """

elif opcion == "5":
    pool = input("Nombre pool DHCP: ")
    red = input("Red: ")
    mascara = input("Máscara: ")
    gateway = input("Gateway: ")
    tipo = "dhcp"
    prompt = f"""
    Configurar DHCP Cisco:

    pool {pool}
    red {red}
    mascara {mascara}
    gateway {gateway}
    """

elif opcion == "6":
    numero_acl = input("Número ACL: ")
    permiso = input("permit/deny: ")
    red = input("Red: ")
    wildcard = input("Wildcard: ")
    tipo = "acl"
    prompt = f"""
    Configurar ACL Cisco:

    ACL {numero_acl}
    accion {permiso}
    red {red}
    wildcard {wildcard}
    """
    elif opcion == "7":
    interfaz = input("Interfaz (ej. FastEthernet 0/1): ")
    max_mac = input("Máximo de MACs permitidas (ej. 2): ")
    violacion = input("Acción de violación (protect / restrict / shutdown): ")
    
    tipo = "port_security"
    prompt = f"""
    Configurar Port-Security Cisco:

    interfaz {interfaz}
    maximo MAC {max_mac}
    violacion {violacion}
    """

else:
    print("Opción inválida")
    exit()

# =====================================================
# OPCIÓN INVÁLIDA
# =====================================================
else:
    print("ERROR: opción inválida")
    exit()

# =====================================================
# LLAMADA API GROQ
# =====================================================
try:

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=800,
        stream=True,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("\n===== CONFIGURACIÓN =====\n")

    respuesta = ""

    # streaming en tiempo real
    for chunk in stream:

        contenido = chunk.choices[0].delta.content

        if contenido:
            print(contenido, end="")
            respuesta += contenido

    # timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # nombre archivo
    archivo = f"configs/{tipo}_{timestamp}.txt"

    # guardar archivo
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(respuesta)

    print(f"\n\nArchivo guardado en: {archivo}")

# =====================================================
# MANEJO DE ERRORES
# =====================================================
except Exception as e:
    print("\nERROR:", e)
    