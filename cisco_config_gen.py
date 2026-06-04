import os
import ipaddress
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

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
    try:
        red = ipaddress.ip_network(red_cidr, strict=False)

        mascara = str(red.netmask)

        wildcard = ".".join(
            str(255 - int(octeto))
            for octeto in mascara.split(".")
        )

        gateway = str(next(red.hosts()))

        return {
            "red": str(red.network_address),
            "mascara": mascara,
            "wildcard": wildcard,
            "gateway": gateway
        }

    except Exception:
        print("ERROR: Red inválida")
        exit()

def validar_ip(ip):

    try:
        ipaddress.ip_address(ip)
        return True

    except ValueError:
        return False

def validar_interfaz(interfaz):

    prefijos_validos = [
        "FastEthernet",
        "GigabitEthernet",
        "Fa",
        "Gi"
    ]

    return any(
        interfaz.startswith(prefijo)
        for prefijo in prefijos_validos
    )

def generar_vlans(cantidad):

    nombres = [
        "VENTAS",
        "RRHH",
        "TI",
        "FINANZAS",
        "GERENCIA",
        "SOPORTE",
        "SEGURIDAD",
        "PRODUCCION"
    ]

    resultado = []

    for i in range(cantidad):

        vlan_id = (i + 1) * 10

        resultado.append({
            "vlan": vlan_id,
            "nombre": nombres[i % len(nombres)],
            "red": f"192.168.{vlan_id}.0/24",
            "gateway": f"192.168.{vlan_id}.1"
        })

    return resultado   

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
print("13. DISEÑO AUTOMÁTICO DE RED")
print("14. VER HISTORIAL")

opcion = input("\nSeleccione opción: ")

prompt = ""
tipo = ""

# =========================
# VLAN
# =========================
if opcion == "1":

    cantidad = input("Cantidad de VLANs: ")

    if not cantidad.isdigit():
        print("ERROR: valor inválido")
        exit()

    cantidad = int(cantidad)

    vlans = generar_vlans(cantidad)

    print("\n===== VLANS GENERADAS =====")

    for vlan in vlans:
        print(
            f"VLAN {vlan['vlan']} - "
            f"{vlan['nombre']} - "
            f"{vlan['red']} - "
            f"GW {vlan['gateway']}"
        )

    tipo = "vlan"

    prompt = f"""
Generar configuración Cisco IOS para:

{vlans}
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

    red_cidr = input("Red destino CIDR (ej: 10.0.0.0/24): ")

    datos = calcular_red(red_cidr)

    gateway = input("Gateway siguiente salto: ")

    if not validar_ip(gateway):
        print("ERROR: Gateway inválido")
        exit()

    print("\n===== DATOS CALCULADOS =====")
    print("Red:", datos["red"])
    print("Máscara:", datos["mascara"])

    tipo = "static_route"

    prompt = f"""
Configurar ruta estática Cisco:

Red destino {datos['red']}
Máscara {datos['mascara']}
Gateway {gateway}
"""

# =========================
# DHCP
# =========================
elif opcion == "5":

    pool = input("Nombre pool DHCP: ")

    if not pool.strip():
        print("ERROR: nombre de pool inválido")
        exit()

    red_cidr = input("Red CIDR (ej: 192.168.1.0/24): ")

    datos = calcular_red(red_cidr)

    print("\n===== DATOS CALCULADOS =====")
    print("Red:", datos["red"])
    print("Máscara:", datos["mascara"])
    print("Gateway sugerido:", datos["gateway"])
    print("Wildcard:", datos["wildcard"])

    tipo = "dhcp"

    prompt = f"""
Configurar DHCP Cisco:

Pool {pool}

Red {datos['red']}
Máscara {datos['mascara']}
Gateway {datos['gateway']}
"""
    
# =========================
# ACL
# =========================
elif opcion == "6":

    numero_acl = input("Número ACL: ")

    if not numero_acl.isdigit():
        print("ERROR: número ACL inválido")
        exit()

    permiso = input("permit/deny: ").lower()

    if permiso not in ["permit", "deny"]:
        print("ERROR: acción inválida")
        exit()

    red_cidr = input("Red CIDR (ej: 192.168.1.0/24): ")

    datos = calcular_red(red_cidr)

    tipo = "acl"

    prompt = f"""
Configurar ACL Cisco:

ACL {numero_acl}
Acción {permiso}

Red {datos['red']}
Wildcard {datos['wildcard']}
"""

# =========================
# PORT SECURITY
# =========================
elif opcion == "7":

    interfaz = input("Interfaz (ej. FastEthernet0/1): ")

    if not validar_interfaz(interfaz):
        print("ERROR: interfaz inválida")
        exit()

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

    if not hostname.strip():
        print("ERROR: hostname inválido")
        exit()

    if not dominio.strip():
        print("ERROR: dominio inválido")
        exit()

    if not usuario.strip():
        print("ERROR: usuario inválido")
        exit()

    if len(password) < 4:
        print("ERROR: password demasiado corta")
        exit()

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

    if not validar_interfaz(interfaz):
        print("ERROR: interfaz inválida")
        exit()

    vlans = input("VLANs permitidas (ej: 10,20,30): ")

    if not vlans.strip():
        print("ERROR: VLANs vacías")
        exit()

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

    red_cidr = input("Red CIDR (ej: 192.168.10.0/24): ")

    datos = calcular_red(red_cidr)

    print("\n===== DATOS CALCULADOS =====")
    print("Red:", datos["red"])
    print("Máscara:", datos["mascara"])
    print("Gateway:", datos["gateway"])

    tipo = "inter_vlan"

    prompt = f"""
Configurar Inter-VLAN Routing Cisco:

VLAN {vlan}

Red {datos['red']}
Mascara {datos['mascara']}
Gateway {datos['gateway']}
"""

# =========================
# NAT
# =========================
elif opcion == "11":

    red_cidr = input("Red interna CIDR (ej: 192.168.1.0/24): ")

    datos = calcular_red(red_cidr)

    interfaz = input("Interfaz externa: ")

    if not validar_interfaz(interfaz):
        print("ERROR: interfaz inválida")
        exit()

    print("\n===== DATOS CALCULADOS =====")
    print("Red:", datos["red"])
    print("Wildcard:", datos["wildcard"])

    tipo = "nat"

    prompt = f"""
Configurar NAT Cisco:

Red interna {datos['red']}
Wildcard {datos['wildcard']}
Interfaz externa {interfaz}
"""

# =========================
# ETHERCHANNEL
# =========================
elif opcion == "12":

    interfaces = input(
        "Interfaces (ej: Fa0/1-Fa0/2): "
    )

    grupo = input("Número de grupo: ")

    if not grupo.isdigit():
        print("ERROR: grupo inválido")
        exit()

    if "-" not in interfaces:
        print("ERROR: formato inválido")
        exit()

    tipo = "etherchannel"

    prompt = f"""
Configurar EtherChannel Cisco:

Interfaces {interfaces}
Grupo {grupo}
"""

# =========================
# DISEÑO AUTOMÁTICO DE RED
# =========================
elif opcion == "13":

    descripcion = input(
        "Describe la red que deseas crear: "
    )

    tipo = "diseno_red"

    prompt = f"""
Diseña una red Cisco IOS completa.

Requerimientos:
{descripcion}

Incluye:
- VLAN
- DHCP
- OSPF
- ACL
- NAT
- SSH
- Trunk
- Inter-VLAN Routing

Genera únicamente comandos Cisco IOS.
"""
    
# =========================
# VER HISTORIAL
# =========================
elif opcion == "14":

    print("\n===== HISTORIAL =====\n")

    archivos = os.listdir("configs")

    if not archivos:
        print("No hay configuraciones guardadas.")
        exit()

    for i, archivo in enumerate(sorted(archivos), start=1):
        print(f"{i}. {archivo}")

    exit()

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
        messages=[
            {
            "role": "system",
            "content": system_prompt
            },
            {
            "role": "user",
            "content": prompt
           }
       ],
       temperature=0.2,
       max_tokens=800,
       stream=True
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

    pdf_file = archivo.replace(".txt", ".pdf")

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    contenido = [
        Paragraph("Configuración Cisco IOS", styles["Title"]),
        Paragraph(
            respuesta.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    ]

    doc.build(contenido)

    print("\n\nConfiguración guardada en:")
    print(archivo)

    print("PDF generado en:")
    print(pdf_file)

except Exception as e:
    print("\nERROR:", e)
    