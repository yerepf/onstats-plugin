# ⛏️ OnStats - Plugin MCDR

Plugin para [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) que envía estadísticas de minería de tu servidor de Minecraft al backend de [OnStats](https://onstats-portal.vercel.app).

## 📥 Instalación

1. Descarga `OnStats.py` y colócalo en la carpeta `plugins/` de tu servidor MCDR.
2. Reinicia MCDR o usa `!!MCDR reload plugin`.
3. Se creará automáticamente la carpeta `config/OnStats/`.

## ⚙️ Configuración

### 1. Configurar el token de API

Cada servidor necesita un token único proporcionado por el administrador de OnStats.

```
!!onstats set token <tu-token-uuid>
```

El token se valida contra el backend y se guarda en `config/OnStats/OnStats_token.txt`.

### 2. Agregar jugadores

Agrega los jugadores que quieres trackear:

```
!!onstats add <username>
```

La lista se guarda en `config/OnStats/OnStats_users.json`.

## 📋 Comandos

| Comando | Descripción |
|---|---|
| `!!onstats add <username>` | Agrega un jugador a la lista |
| `!!onstats del <username>` | Elimina un jugador de la lista |
| `!!onstats list` | Muestra los jugadores registrados |
| `!!onstats update` | Envía las estadísticas al backend |
| `!!onstats set token <token>` | Configura el token de API |

## 🔄 ¿Cómo funciona?

1. Al ejecutar `!!onstats update`, el plugin:
   - Ejecuta `save-all` en el servidor
   - Lee los archivos de estadísticas de cada jugador en `server/world/stats/`
   - Suma todos los bloques minados (`minecraft:mined`)
   - Envía los datos al backend via POST a `/stats/`

2. El backend almacena un snapshot con la fecha actual, permitiendo ver el progreso a lo largo del tiempo en el [portal web](https://onstats-portal.vercel.app).

## 📁 Estructura de archivos

```
config/OnStats/
├── OnStats_token.txt    # Token de API del servidor
└── OnStats_users.json   # Lista de jugadores a trackear
```

## 🔗 Links

- **Portal web:** https://onstats-portal.vercel.app
- **Backend API:** https://onstats-backend.onrender.com
- **Frontend repo:** https://github.com/yerepf/onstats-portal
- **Backend repo:** https://github.com/yerepf/onstats-backend

## 📦 Requisitos

- [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) 2.x+
- Python 3.8+
- `requests` (incluido en la mayoría de entornos Python)

## 📝 Licencia

MIT
