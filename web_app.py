from flask import Flask, render_template, request
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import os

# cargar variables .env
load_dotenv()

# obtener API key
api_key = os.getenv("GROQ_API_KEY")

# validar key
if not api_key:
    print("ERROR: No se encontró GROQ_API_KEY")
    exit()

# cliente Groq
client = Groq(api_key=api_key)

# app flask
app = Flask(__name__)

# crear carpeta configs
if not os.path.exists("configs"):
    os.makedirs("configs")

# prompt sistema
SYSTEM_PROMPT = """
Eres experto en Cisco IOS.

Debes generar SOLO comandos Cisco IOS válidos.

NO expliques nada.
NO uses markdown.
NO uses texto extra.
"""

@app.route("/", methods=["GET", "POST"])
def index():

    resultado = ""

    if request.method == "POST":

        opcion = request.form.get("opcion")

        prompt = ""
        tipo = ""

        # VLAN
        if opcion == "vlan":

            vlan = request.form.get("vlan")
            nombre = request.form.get("nombre")
            puerto = request.form.get("puerto")

            tipo = "vlan"

            prompt = f"""
            Crear VLAN {vlan}
            Nombre {nombre}
            Puerto {puerto}
            """

        # OSPF
        elif opcion == "ospf":

            proceso = request.form.get("proceso")
            red = request.form.get("red")
            area = request.form.get("area")

            tipo = "ospf"

            prompt = f"""
            Configurar OSPF:

            proceso {proceso}
            red {red}
            area {area}
            """

        # SUBNETTING
        elif opcion == "subnetting":

            red_base = request.form.get("red_base")
            subredes = request.form.get("subredes")

            tipo = "subnetting"

            prompt = f"""
            Generar subnetting:

            red {red_base}
            subredes {subredes}
            """

        # STATIC ROUTE
        elif opcion == "static":

            red_destino = request.form.get("red_destino")
            mascara = request.form.get("mascara")
            gateway = request.form.get("gateway")

            tipo = "static_route"

            prompt = f"""
            Configurar ruta estática:

            red destino {red_destino}
            mascara {mascara}
            gateway {gateway}
            """

        # DHCP
        elif opcion == "dhcp":

            pool = request.form.get("pool")
            red = request.form.get("red_dhcp")
            mascara = request.form.get("mascara_dhcp")
            gateway = request.form.get("gateway_dhcp")

            tipo = "dhcp"

            prompt = f"""
            Configurar DHCP Cisco:

            pool {pool}
            red {red}
            mascara {mascara}
            gateway {gateway}
            """

        # ACL
        elif opcion == "acl":

            numero_acl = request.form.get("numero_acl")
            permiso = request.form.get("permiso")
            red_acl = request.form.get("red_acl")
            wildcard = request.form.get("wildcard")

            tipo = "acl"

            prompt = f"""
            Configurar ACL Cisco:

            ACL {numero_acl}
            accion {permiso}
            red {red_acl}
            wildcard {wildcard}
            """

        try:

            completion = client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.2,
                max_tokens=800
            )

            resultado = completion.choices[0].message.content

            # guardar archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            archivo = f"configs/{tipo}_{timestamp}.txt"

            with open(archivo, "w", encoding="utf-8") as f:
                f.write(resultado)

        except Exception as e:

            resultado = f"ERROR: {e}"

    return render_template(
        "index.html",
        resultado=resultado
    )

if __name__ == "__main__":
    app.run(debug=True)