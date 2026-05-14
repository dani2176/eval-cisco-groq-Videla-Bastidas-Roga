# web_app.py

import os

from flask import Flask, render_template, request

from groq import Groq

from dotenv import load_dotenv

# =========================
# CARGAR VARIABLES
# =========================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# =========================
# CLIENTE GROQ
# =========================

client = Groq(api_key=api_key)

# =========================
# APP FLASK
# =========================

app = Flask(__name__)

# =========================
# PROMPT SISTEMA
# =========================

system_prompt = """
Eres un experto en Cisco IOS.

Debes generar SOLO comandos Cisco IOS válidos.

NO expliques nada.
NO uses markdown.
NO uses texto adicional.
"""

# =========================
# HOME
# =========================

@app.route("/", methods=["GET", "POST"])
def index():

    respuesta = ""
    tipo = ""

    if request.method == "POST":

        tipo = request.form.get("tipo")

        prompt = ""

        # =========================
        # VLAN
        # =========================

        if tipo == "vlan":

            vlan = request.form.get("vlan")
            nombre = request.form.get("nombre")
            puerto = request.form.get("puerto")

            prompt = f"""
            Crear VLAN {vlan}
            Nombre {nombre}
            Puerto {puerto}
            """

        # =========================
        # OSPF
        # =========================

        elif tipo == "ospf":

            proceso = request.form.get("proceso")
            red = request.form.get("red")
            area = request.form.get("area")

            prompt = f"""
            Configurar OSPF

            Proceso: {proceso}

            Red: {red}

            Área: {area}
            """

        # =========================
        # SUBNETTING
        # =========================

        elif tipo == "subnetting":

            red = request.form.get("red")
            subredes = request.form.get("subredes")

            prompt = f"""
            Generar subnetting

            Red base: {red}

            Cantidad subredes: {subredes}
            """

        # =========================
        # DHCP
        # =========================

        elif tipo == "dhcp":

            gateway = request.form.get("gateway")
            dns = request.form.get("dns")

            prompt = f"""
            Configurar DHCP Cisco IOS

            Gateway: {gateway}

            DNS: {dns}
            """

        # =========================
        # ACL
        # =========================

        elif tipo == "acl":

            permitir = request.form.get("permitir")
            wildcard = request.form.get("wildcard")

            prompt = f"""
            Configurar ACL estándar Cisco IOS

            Permitir: {permitir}

            Wildcard: {wildcard}
            """

        # =========================
        # GENERAR IA
        # =========================

        try:

            completion = client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                temperature=0.2,

                max_tokens=800,

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

            respuesta = completion.choices[0].message.content

        except Exception as e:

            respuesta = f"ERROR: {e}"

    return render_template(
        "index.html",
        respuesta=respuesta,
        tipo=tipo
    )

# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(debug=True)