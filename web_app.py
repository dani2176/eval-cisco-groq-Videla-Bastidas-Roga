import os
import ipaddress
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from datetime import timedelta

# CAMBIO 1: Se agregó 'send_from_directory' a las importaciones de Flask
from flask import Flask, render_template, request, send_from_directory, session

# Nuevas importaciones para la generación de PDFs
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

#------------------------ 
load_dotenv()

# client = Groq(api_key=api_key)

app = Flask(__name__)

app.secret_key = "cisco_ai_generator_2026"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_COOKIE_NAME"] = "cisco_session"

# Asegurar que la carpeta exista
if not os.path.exists("configs"):
    os.makedirs("configs")

# =========================
# LÓGICA DE REDES INTERNA
# =========================
def calcular_red(red_cidr):
    try:
        red = ipaddress.ip_network(red_cidr, strict=False)
        mascara = str(red.netmask)
        wildcard = ".".join(str(255 - int(octeto)) for octeto in mascara.split("."))
        gateway = str(next(red.hosts()))
        return {
            "red": str(red.network_address),
            "mascara": mascara,
            "wildcard": wildcard,
            "gateway": gateway
        }
    except Exception:
        return None

def generar_vlans(cantidad):
    nombres = ["VENTAS", "RRHH", "TI", "FINANZAS", "GERENCIA", "SOPORTE", "SEGURIDAD", "PRODUCCION"]
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

SYSTEM_PROMPT = """
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
# RUTA PRINCIPAL FLASK
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    resultado = ""
    archivos = sorted(os.listdir("configs"), reverse=True)

    
    # Recuperar API guardada en sesión
    api_key = session.get("groq_api_key")
    print("SESSION:", dict(session))
    
    if request.method == "POST":

        opcion = request.form.get("opcion")
        prompt = ""
        tipo = ""

        # Si el usuario escribió una nueva API
        nueva_api = request.form.get("groq_api_key")

        if nueva_api and nueva_api.strip():
            session.permanent = False
            session["groq_api_key"] = nueva_api.strip()
            api_key = nueva_api.strip()

        # Si no existe API ni en el formulario ni en sesión
        if not api_key or not str(api_key).startswith("gsk_"):
            resultado = "ERROR: Debes ingresar una API Key válida de Groq"
            return render_template(
                "index.html",
                resultado=resultado,
                archivos=archivos
            )

        # Crear cliente Groq usando la API de la sesión
        print("=" * 50)
        print("API_KEY:", api_key)
        print("=" * 50)
        print("API USADA:", api_key)
        client = Groq(api_key=api_key)


        # 1. VLAN
        if opcion == "1":
            cantidad = request.form.get("vlan_cantidad", "1")
            if cantidad.isdigit():
                vlans = generar_vlans(int(cantidad))
                tipo = "vlan"
                prompt = f"Generar configuración Cisco IOS para:\n{vlans}"
            else:
                resultado = "ERROR: Cantidad de VLANs inválida"

        # 2. OSPF
        elif opcion == "2":
            proceso = request.form.get("ospf_proceso")
            red_cidr = request.form.get("ospf_red_cidr")
            area = request.form.get("ospf_area")
            datos = calcular_red(red_cidr)
            if datos:
                tipo = "ospf"
                prompt = f"Configurar OSPF:\nProceso {proceso}\nRed {datos['red']}\nMascara {datos['mascara']}\nWildcard {datos['wildcard']}\nGateway {datos['gateway']}\nÁrea {area}"
            else:
                resultado = "ERROR: Formato de Red CIDR inválido"

        # 3. SUBNETTING
        elif opcion == "3":
            red = request.form.get("sub_red")
            prefijo = request.form.get("sub_prefijo")
            subredes = request.form.get("sub_subredes")
            datos_red = calcular_red(f"{red}/{prefijo}")
            if datos_red:
                tipo = "subnetting"
                prompt = f"Generar subnetting Cisco:\nRed base {red}/{prefijo}\nCantidad subredes {subredes}\n\nMostrar:\n- Subred\n- Máscara\n- Gateway\n- Hosts disponibles"
            else:
                resultado = "ERROR: Prefijo o Red Base inválida"

        # 4. STATIC ROUTE
        elif opcion == "4":
            red_cidr = request.form.get("static_red_cidr")
            gateway = request.form.get("static_gateway")
            datos = calcular_red(red_cidr)
            if datos:
                tipo = "static_route"
                prompt = f"Configurar ruta estática Cisco:\nRed destino {datos['red']}\nMáscara {datos['mascara']}\nGateway {gateway}"
            else:
                resultado = "ERROR: Red destino inválida"

        # 5. DHCP
        elif opcion == "5":
            pool = request.form.get("dhcp_pool")
            red_cidr = request.form.get("dhcp_red_cidr")
            datos = calcular_red(red_cidr)
            if datos:
                tipo = "dhcp"
                prompt = f"Configurar DHCP Cisco:\nPool {pool}\nRed {datos['red']}\nMáscara {datos['mascara']}\nGateway {datos['gateway']}"
            else:
                resultado = "ERROR: Red DHCP inválida"

        # 6. ACL
        elif opcion == "6":
            numero_acl = request.form.get("acl_numero")
            permiso = request.form.get("acl_permiso")
            red_cidr = request.form.get("acl_red_cidr")
            datos = calcular_red(red_cidr)
            if datos:
                tipo = "acl"
                prompt = f"Configurar ACL Cisco:\nACL {numero_acl}\nAcción {permiso}\nRed {datos['red']}\nWildcard {datos['wildcard']}"
            else:
                resultado = "ERROR: Red para ACL inválida"

        # 7. PORT SECURITY
        elif opcion == "7":
            interfaz = request.form.get("ps_interfaz")
            max_mac = request.form.get("ps_max_mac")
            violacion = request.form.get("ps_violacion")
            tipo = "port_security"
            prompt = f"Configurar Port-Security Cisco:\nInterfaz {interfaz}\nMáximo MAC {max_mac}\nViolación {violacion}"

        # 8. SSH
        elif opcion == "8":
            hostname = request.form.get("ssh_hostname")
            dominio = request.form.get("ssh_dominio")
            usuario = request.form.get("ssh_usuario")
            password = request.form.get("ssh_password")
            tipo = "ssh"
            prompt = f"Configurar SSH Cisco:\nHostname {hostname}\nDominio {dominio}\nUsuario {usuario}\nPassword {password}"

        # 9. TRUNK
        elif opcion == "9":
            interfaz = request.form.get("trunk_interfaz")
            vlans_permitidas = request.form.get("trunk_vlans")
            tipo = "trunk"
            prompt = f"Configurar Trunk Cisco:\nInterfaz {interfaz}\nVLANs permitidas {vlans_permitidas}"

        # 10. INTER-VLAN ROUTING
        elif opcion == "10":
            vlan = request.form.get("iv_vlan")
            red_cidr = request.form.get("iv_red_cidr")
            datos = calcular_red(red_cidr)
            if datos:
                tipo = "inter_vlan"
                prompt = f"Configurar Inter-VLAN Routing Cisco:\nVLAN {vlan}\nRed {datos['red']}\nMascara {datos['mascara']}\nGateway {datos['gateway']}"
            else:
                resultado = "ERROR: Red para Inter-VLAN inválida"

        # 11. NAT
        elif opcion == "11":
            red_cidr = request.form.get("nat_red_cidr")
            interfaz = request.form.get("nat_interfaz_ext")
            datos = calcular_red(red_cidr)
            if datos:
                tipo = "nat"
                prompt = f"Configurar NAT Cisco:\nRed interna {datos['red']}\nWildcard {datos['wildcard']}\nInterfaz externa {interfaz}"
            else:
                resultado = "ERROR: Red interna de NAT inválida"

        # 12. ETHERCHANNEL
        elif opcion == "12":
            interfaces = request.form.get("eth_interfaces")
            grupo = request.form.get("eth_grupo")
            tipo = "etherchannel"
            prompt = f"Configurar EtherChannel Cisco:\nInterfaces {interfaces}\nGrupo {grupo}"

        # 13. DISEÑO AUTOMÁTICO DE RED
        elif opcion == "13":
            descripcion = request.form.get("diseno_descripcion")
            tipo = "diseno_red"
            prompt = f"Diseña una red Cisco IOS completa.\nRequerimientos:\n{descripcion}\n\nIncluye:\n- VLAN\n- DHCP\n- OSPF\n- ACL\n- NAT\n- SSH\n- Trunk\n- Inter-VLAN Routing\n\nGenera únicamente comandos Cisco IOS."

        # Llamar a Groq e implementar ReportLab
        if prompt and not resultado.startswith("ERROR"):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=800
                )
                resultado = completion.choices[0].message.content

                # Generar nombres basados en marca de tiempo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo_txt = f"configs/{tipo}_{timestamp}.txt"
                archivo_pdf = f"configs/{tipo}_{timestamp}.pdf"

                # 1. Guardar archivo de texto (.txt)
                with open(archivo_txt, "w", encoding="utf-8") as f:
                    f.write(resultado)

                # 2. Guardar reporte en PDF (.pdf) usando tu lógica ReportLab
                doc = SimpleDocTemplate(archivo_pdf)
                styles = getSampleStyleSheet()
                
                # Definir un estilo de fuente monoespaciada para que el código Cisco mantenga las indentaciones
                style_codigo = ParagraphStyle(
                    'CiscoCodeStyle',
                    parent=styles['Normal'],
                    fontName='Courier',
                    fontSize=10,
                    leading=14,
                    alignment=TA_LEFT
                )

                contenido_pdf = [
                    Paragraph(f"Configuración Cisco IOS - {tipo.upper()}", styles["Title"]),
                    Spacer(1, 15),
                    Paragraph(resultado.replace("\n", "<br/>"), style_codigo)
                ]
                doc.build(contenido_pdf)

                # Actualizar lista de visualización para incluir los nuevos archivos
                archivos = sorted(os.listdir("configs"), reverse=True)
                
                # Mensaje de éxito en la interfaz web
                resultado = f"[✓ Guardado en TXT y PDF]\n\n{resultado}"

            except Exception as e:
                resultado = f"ERROR: {e}"

    return render_template("index.html", resultado=resultado, archivos=archivos, api_guardada=session.get("groq_api_key")) 

# CAMBIO 2: Nueva función para resolver la descarga segura de archivos locales
@app.route("/descargar/<nombre>")
def descargar(nombre):
    return send_from_directory(
        "configs",
        nombre,
        as_attachment=True
    )

@app.route("/borrar_api")
def borrar_api():
    session.clear()
    return "API borrada"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

