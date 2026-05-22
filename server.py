from flask import Flask, request, Response, abort, jsonify
import os
import json
import urllib.request
from datetime import datetime

app = Flask(__name__)

# Token do GitHub pro repo privado
GITHUB_TOKEN = "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"
SCRIPT_URL = "https://raw.githubusercontent.com/aucerolanocry/ff-installer/main/install.sh"

# Senha do painel admin (só você usa)
ADMIN_KEY = "NOCRY_ADMIN_2025"

# Arquivo de licenças
LICENSES_FILE = "licenses.json"

def load_licenses():
    if not os.path.exists(LICENSES_FILE):
        return {}
    with open(LICENSES_FILE, 'r') as f:
        return json.load(f)

def save_licenses(data):
    with open(LICENSES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ===== ROTA: BAIXAR SCRIPT =====
@app.route('/get')
def get_script():
    license_key = request.args.get('key', '')
    
    if not license_key:
        abort(403)
    
    licenses = load_licenses()
    
    # Verifica se licença existe
    if license_key not in licenses:
        return Response("LICENCA_INVALIDA", status=403)
    
    user = licenses[license_key]
    
    # Verifica se está ativa
    if not user.get('ativo', False):
        return Response("LICENCA_REVOGADA", status=403)
    
    # Atualiza último acesso
    user['ultimo_acesso'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    user['acessos'] = user.get('acessos', 0) + 1
    save_licenses(licenses)
    
    # Baixa e serve o script
    req = urllib.request.Request(SCRIPT_URL, headers={
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3.raw'
    })
    with urllib.request.urlopen(req) as response:
        content = response.read()
    
    return Response(content, mimetype='text/plain')

# ===== ROTA: CRIAR LICENÇA =====
@app.route('/admin/criar')
def criar_licenca():
    admin = request.args.get('admin', '')
    nome = request.args.get('nome', 'Sem nome')
    key = request.args.get('key', '')
    
    if admin != ADMIN_KEY:
        abort(403)
    
    if not key:
        import random, string
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    licenses = load_licenses()
    licenses[key] = {
        'nome': nome,
        'ativo': True,
        'criado': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'ultimo_acesso': 'Nunca',
        'acessos': 0
    }
    save_licenses(licenses)
    
    return jsonify({
        'status': 'criado',
        'nome': nome,
        'key': key
    })

# ===== ROTA: REVOGAR LICENÇA =====
@app.route('/admin/revogar')
def revogar_licenca():
    admin = request.args.get('admin', '')
    key = request.args.get('key', '')
    
    if admin != ADMIN_KEY:
        abort(403)
    
    licenses = load_licenses()
    if key not in licenses:
        return jsonify({'status': 'nao_encontrada'})
    
    licenses[key]['ativo'] = False
    save_licenses(licenses)
    
    return jsonify({'status': 'revogada', 'key': key})

# ===== ROTA: LISTAR LICENÇAS =====
@app.route('/admin/listar')
def listar_licencas():
    admin = request.args.get('admin', '')
    
    if admin != ADMIN_KEY:
        abort(403)
    
    licenses = load_licenses()
    return jsonify(licenses)

# ===== ROTA: REATIVAR LICENÇA =====
@app.route('/admin/ativar')
def ativar_licenca():
    admin = request.args.get('admin', '')
    key = request.args.get('key', '')
    
    if admin != ADMIN_KEY:
        abort(403)
    
    licenses = load_licenses()
    if key not in licenses:
        return jsonify({'status': 'nao_encontrada'})
    
    licenses[key]['ativo'] = True
    save_licenses(licenses)
    
    return jsonify({'status': 'ativada', 'key': key})

@app.route('/')
def index():
    abort(403)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
