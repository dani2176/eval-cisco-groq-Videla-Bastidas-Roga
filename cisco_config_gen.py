import os
import ipaddress
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# =========================
# CARGAR VARIABLES .ENV
# =========================
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: No se encontró GROQ_API_KEY")
    exit()

client = Groq(api_key=api_key)

def calcular_red(red_cidr):
    red = ipaddress.ip_network(red_cidr, strict=False)

    mascara = str(red.netmask)

    wildcard = ".".join(
        str(255 - int(octeto))
        for octeto in mascara.split(".")
    )

    gateway = str(list(red.hosts())[0])

    return {
        "red": str(red.network_address),
        "mascara": mascara,
        "wildcard": wildcard,
        "gateway": gateway
    }

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
print("\n===== GENERADOR CISCO IOS =====")
print("1. VLAN")
print("2. OSPF")
print("3. SUBNETTING")
print("4. STATIC ROUTE")
print("5. DHCP")
print("6. ACL")
print("7. PORT-SECURITY")
print("8. SSH")
print("9. TRUNK")
print("10. INTER-VLAN ROUTING")
print("11. NAT")
print("12. ETHERCHANNEL")

opcion = input("\nSeleccione opción: ")

prompt = ""
tipo = ""

# =========================
# VLAN
# =========================
if opcion == "1":

    vlan = input("ID VLAN: ")

    if not vlan.isdigit():
        print("ERROR: VLAN inválida")
        exit()

    vlan = int(vlan)

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

# =========================
# OSPF
# =========================
elif opcion == "2":

    proceso = input("Proceso OSPF: ")

    if not proceso.isdigit():
        print("ERROR: proceso inválido")
        exit()

    red_cidr = input("Red CIDR (ej: 192.168.1.0/24): ")

    datos = calcular_red(red_cidr)

    area = input("Área: ")

    if not area.isdigit():
        print("ERROR: área inválida")
        exit()

    tipo = "ospf"

    prompt = f"""
Configurar OSPF:

Proceso {proceso}

Red {datos['red']}
Mascara {datos['mascara']}
Wildcard {datos['wildcard']}
Gateway {datos['gateway']}

Área {area}
"""

# =========================
# SUBNETTING
# =========================
elif opcion == "3":

    red = input("Red base: ")
    prefijo = input("Prefijo CIDR: ")
    subredes = input("Cantidad subredes: ")

    if not prefijo.isdigit():
        print("ERROR: prefijo inválido")
        exit()

    prefijo = int(prefijo)

    datos_red = calcular_red(f"{red}/{prefijo}")

    print("\n===== DATOS CALCULADOS =====")
    print("Red:", datos_red["red"])
    print("Máscara:", datos_red["mascara"])
    print("Wildcard:", datos_red["wildcard"])
    print("Gateway sugerido:", datos_red["gateway"])

    if prefijo < 8 or prefijo > 30:
        print("ERROR: prefijo fuera de rango")
        exit()

    if not subredes.isdigit():
        print("ERROR: cantidad de subredes inválida")
        exit()

    tipo = "subnetting"

    prompt = f"""
Generar subnetting Cisco:

Red base {red}/{prefijo}
Cantidad subredes {subredes}

Mostrar:
- Subred
- Máscara
- Gateway
- Hosts disponibles
"""

# =========================
# STATIC ROUTE
# =========================
elif opcion == "4":

    red_destino = input("Red destino: ")
    mascara = input("Máscara: ")
    gateway = input("Gateway: ")

    tipo = "static_route"

    prompt = f"""
Configurar ruta estática:

Red destino {red_destino}
Máscara {mascara}
Gateway {gateway}
"""

# =========================
# DHCP
# =========================
elif opcion == "5":

    pool = input("Nombre pool DHCP: ")
    red = input("Red: ")
    mascara = input("Máscara: ")
    gateway = input("Gateway: ")

    tipo = "dhcp"

    prompt = f"""
Configurar DHCP Cisco:

Pool {pool}
Red {red}
Máscara {mascara}
Gateway {gateway}
"""

# =========================
# ACL
# =========================
elif opcion == "6":

    numero_acl = input("Número ACL: ")
    permiso = input("permit/deny: ")
    red = input("Red: ")
    wildcard = input("Wildcard: ")

    tipo = "acl"

    prompt = f"""
Configurar ACL Cisco:

ACL {numero_acl}
Acción {permiso}
Red {red}
Wildcard {wildcard}
"""

# =========================
# PORT SECURITY
# =========================
elif opcion == "7":

    interfaz = input("Interfaz (ej. FastEthernet0/1): ")
    max_mac = input("Máximo de MACs permitidas: ")
    violacion = input("Acción (protect/restrict/shutdown): ")

    tipo = "port_security"

    prompt = f"""
Configurar Port-Security Cisco:

Interfaz {interfaz}
Máximo MAC {max_mac}
Violación {violacion}
"""

# =========================
# SSH
# =========================
elif opcion == "8":

    hostname = input("Hostname: ")
    dominio = input("Dominio: ")
    usuario = input("Usuario: ")
    password = input("Password: ")

    tipo = "ssh"

    prompt = f"""
Configurar SSH Cisco:

Hostname {hostname}
Dominio {dominio}
Usuario {usuario}
Password {password}
"""

# =========================
# TRUNK
# =========================
elif opcion == "9":

    interfaz = input("Interfaz trunk: ")
    vlans = input("VLANs permitidas (ej: 10,20,30): ")

    tipo = "trunk"

    prompt = f"""
Configurar Trunk Cisco:

Interfaz {interfaz}
VLANs permitidas {vlans}
"""

# =========================
# INTER-VLAN ROUTING
# =========================
elif opcion == "10":

    vlan = input("Número VLAN: ")
    gateway = input("Gateway: ")

    tipo = "inter_vlan"

    prompt = f"""
Configurar Inter-VLAN Routing Cisco:

VLAN {vlan}
Gateway {gateway}
"""

# =========================
# NAT
# =========================
elif opcion == "11":

    red = input("Red interna: ")
    wildcard = input("Wildcard: ")
    interfaz = input("Interfaz externa: ")

    tipo = "nat"

    prompt = f"""
Configurar NAT Cisco:

Red interna {red}
Wildcard {wildcard}
Interfaz externa {interfaz}
"""

# =========================
# ETHERCHANNEL
# =========================
elif opcion == "12":

    interfaces = input("Interfaces (ej: Fa0/1-Fa0/2): ")
    grupo = input("Número de grupo: ")

    tipo = "etherchannel"

    prompt = f"""
Configurar EtherChannel Cisco:

Interfaces {interfaces}
Grupo {grupo}
"""
    
# =========================
# OPCIÓN INVÁLIDA
# =========================
else:
    print("ERROR: opción inválida")
    exit()

# =========================
# LLAMADA A GROQ
# =========================
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

    print("\n===== CONFIGURACIÓN GENERADA =====\n")

    respuesta = ""

    for chunk in stream:

        contenido = chunk.choices[0].delta.content

        if contenido:
            print(contenido, end="")
            respuesta += contenido

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    archivo = f"configs/{tipo}_{timestamp}.txt"

    with open(archivo, "w", encoding="utf-8") as f:
        f.write(respuesta)

    print(f"\n\nConfiguración guardada en:")
    print(archivo)

except Exception as e:
    print("\nERROR:", e)
    