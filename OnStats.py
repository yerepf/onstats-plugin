import os
import json
from time import sleep
import requests
from collections import defaultdict
from uuid import UUID


PLUGIN_META = {
    'name': 'OnStats',
    'version': '1.1',
    'description': 'Envía estadísticas de minería al backend',
    'author': 'yerepf'
}

API_BASE_URL = 'https://backend.onstats.rep.software/'
VALIDATE_TOKEN_ENDPOINT = 'servers/validate-token'
UPDATE_STATS_ENDPOINT = 'stats/'
STATS_DIR = 'server/world/stats/'
USERCACHE_PATH = 'server/usercache.json'
LIST_FILE = 'config/OnStats/OnStats_users.json'
TOKEN_FILE = 'config/OnStats/OnStats_token.txt'


def on_load(server, old):
    os.makedirs(os.path.dirname(LIST_FILE), exist_ok=True)
    if not os.path.exists(LIST_FILE):
        with open(LIST_FILE, 'w', encoding='utf8') as f:
            json.dump([], f)


def load_user_list():
    if not os.path.exists(LIST_FILE):
        return []
    with open(LIST_FILE, 'r', encoding='utf8') as f:
        return json.load(f)


def save_user_list(userlist):
    os.makedirs(os.path.dirname(LIST_FILE), exist_ok=True)
    with open(LIST_FILE, 'w', encoding='utf8') as f:
        json.dump(userlist, f, indent=2)


def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, 'r', encoding='utf8') as f:
        return f.read().strip()


def is_valid_uuid(token):
    try:
        UUID(token)
        return True
    except ValueError:
        return False

def save_stats_data(data, token):
    if not token:
        print("[onStats] No se encontró token de API.")
        return
    headers = {'X-API-Token': token}
    try:
        response = requests.post(API_BASE_URL + UPDATE_STATS_ENDPOINT, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        print("[onStats] Datos enviados correctamente.")
    except requests.RequestException as e:
        print(f"[onStats] Error al enviar datos al backend: {e}")


def sum_mined_for_name(target_name):
    target_name_lower = target_name.lower()
    total = 0
    
    print(f"[DEBUG] Buscando estadísticas para: {target_name_lower}")  # Log de depuración
    
    # Buscar en todos los archivos de stats
    for filename in os.listdir(STATS_DIR):
        if not filename.endswith('.json'):
            continue
            
        uuid = filename[:-5]
        path = os.path.join(STATS_DIR, filename)
        
        try:
            with open(path, 'r', encoding='utf8') as f:
                data = json.load(f)
                
            # Opción 1: Buscar por playername en minecraft:custom
            player_name = data.get('stats', {}).get('minecraft:custom', {}).get('minecraft:playername', "")
            if player_name.lower() == target_name_lower:
                mined = data.get('stats', {}).get('minecraft:mined', {})
                total += sum(mined.values()) if mined else 0
                print(f"[DEBUG] Encontrado en {filename} por playername: {mined}")  # Log
                continue
                
            # Opción 2: Buscar en DataVersion más reciente
            player_name = data.get('Data', {}).get('playerName', "")
            if player_name.lower() == target_name_lower:
                mined = data.get('stats', {}).get('minecraft:mined', {})
                total += sum(mined.values()) if mined else 0
                print(f"[DEBUG] Encontrado en {filename} por Data.playerName: {mined}")  # Log
                continue
                
            # Opción 3: Buscar en usercache.json si el UUID coincide
            try:
                with open(USERCACHE_PATH, 'r', encoding='utf8') as f:
                    entries = json.load(f)
                for entry in entries:
                    if entry.get('uuid') == uuid and entry.get('name', "").lower() == target_name_lower:
                        mined = data.get('stats', {}).get('minecraft:mined', {})
                        total += sum(mined.values()) if mined else 0
                        print(f"[DEBUG] Encontrado en {filename} por usercache: {mined}")  # Log
                        break
            except Exception:
                continue
                
        except Exception as e:
            print(f"[ERROR] Procesando {filename}: {str(e)}")
            continue
            
    print(f"[DEBUG] Total para {target_name}: {total}")  # Log final
    return total


def on_info(server, info):
    if not info.content.startswith('!!onstats'):
        return

    args = info.content.strip().split()
    if len(args) < 2:
        server.reply(info, "§7Uso: !!onstats [add/del/list/update/set token] [username/token]")
        return

    cmd = args[1]
    userlist = load_user_list()

    if cmd == 'add':
        if len(args) < 3:
            server.reply(info, "§7Uso: !!onstats add [username]")
            return
        username = args[2]
        if username in userlist:
            server.reply(info, f"§e{username} ya está en la lista.")
        else:
            userlist.append(username)
            save_user_list(userlist)
            server.reply(info, f"§aUsuario {username} agregado.")

    elif cmd == 'del':
        if len(args) < 3:
            server.reply(info, "§7Uso: !!onstats del [username]")
            return
        username = args[2]
        if username not in userlist:
            server.reply(info, f"§e{username} no está en la lista.")
        else:
            userlist.remove(username)
            save_user_list(userlist)
            server.reply(info, f"§cUsuario {username} eliminado.")

    elif cmd == 'list':
        if not userlist:
            server.reply(info, "§7No hay usuarios registrados.")
        else:
            msg = "§bUsuarios: §7" + ", ".join(userlist)
            server.reply(info, msg)

    elif cmd == 'set' and len(args) >= 4 and args[2] == 'token':
        token = args[3].strip()

        if not is_valid_uuid(token):
            server.reply(info, "§cEl token no tiene formato UUID válido.")
            return

        headers = {'X-API-Token': token}
        try:
            response = requests.get(API_BASE_URL + VALIDATE_TOKEN_ENDPOINT, headers=headers, timeout=5)

            if response.status_code == 401:
                server.reply(info, "§cToken inválido según el backend (401).")
                return

            response.raise_for_status()
            data = response.json()

            if not data.get('valid', False):
                server.reply(info, "§cToken rechazado por el backend (valid=False).")
                return

            # ✅ Guardar token
            os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
            with open(TOKEN_FILE, 'w', encoding='utf8') as f:
                f.write(token)

            server_name = data.get('name', 'desconocido')
            server.reply(info, f"§aToken validado y guardado correctamente. Servidor: §b{server_name}")

        except requests.RequestException as e:
            print(f"[onStats] Error al validar token: {e}")
            server.reply(info, "§cError al conectar con el backend para validar el token.")

    elif cmd == 'update':
        if not userlist:
            server.reply(info, "§7No hay usuarios configurados.")
            return

        token = load_token()
        if not token:
            server.reply(info, "§cToken no configurado. Usa: !!onstats set token [api-key]")
            return

        server.execute('save-all')
        sleep(2)

        msg = "§e§lTotal bloques minados:"
        stats_data = {}
        for username in userlist:
            total = sum_mined_for_name(username)
            stats_data[username] = total
            msg += f"\n§b{username}§7: §a{total}"
        save_stats_data(stats_data, token)
        server.reply(info, msg)

    else:
        server.reply(info, "§7Comando desconocido. Usa: !!onstats [add/del/list/update/set token]")