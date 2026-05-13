from flask import Flask, render_template, request
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
Eres experto en Cisco IOS.

Genera SOLO comandos Cisco IOS válidos.
NO expliques nada.
"""

@app.route("/", methods=["GET", "POST"])
def index():

    resultado = ""

    if request.method == "POST":

        vlan = request.form["vlan"]
        nombre = request.form["nombre"]
        puerto = request.form["puerto"]

        prompt = f"""
        Crear VLAN {vlan}
        Nombre {nombre}
        Puerto {puerto}
        """

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
            max_tokens=500
        )

        resultado = completion.choices[0].message.content

    return render_template(
        "index.html",
        resultado=resultado
    )

if __name__ == "__main__":
    app.run(debug=True)