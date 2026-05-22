from flask import Flask, request, Response, abort, jsonify
import os
import json
import urllib.request
from datetime import datetime

app = Flask(__name__)

# Token do GitHub pro repo privado
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
SCRIPT_URL = "https://raw.githubusercontent.com/aucerolanocry/ff-installer/main/install.sh"

# ===== LICENÇAS VIA VARIÁVEL DE AMBIENTE =====
# No painel do Render, crie a variável LICENSES com o valor:
# {"SUACHAVE": {"nome": "Fulano", "ativo": true}}

def load_licenses():
    raw = os.environ.get('LICENSES', '{}')
    try:
        return json.loads(raw)
    except:
        return {}

# ===== ROTA: BAIXAR SCRIPT =====
@app.route('/get')
def get_script():
    license_key = request.args.get('key', '')

    if not license_key:
        abort(403)

    licenses = load_licenses()

    if license_key not in licenses:
        return Response("LICENCA_INVALIDA", status=403)

    user = licenses[license_key]

    if not user.get('ativo', False):
        return Response("LICENCA_REVOGADA", status=403)

    req = urllib.request.Request(SCRIPT_URL, headers={
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3.raw'
    })
    with urllib.request.urlopen(req) as response:
        content = response.read()

    return Response(content, mimetype='text/plain')

@app.route('/')
def index():
    abort(403)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
