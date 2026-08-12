import asyncio
import json
import websockets

connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print(f"Cliente conectado. Total: {len(connected_clients)}")

    try:
        async for message in websocket:
            await handle_message(websocket, message)

    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado", flush=True)

    finally:
        connected_clients.remove(websocket)


async def handle_message(websocket, raw_message):
    try:
        data = json.loads(raw_message)
    except json.JSONDecodeError:
        print(f"Mensaje no válido (no es JSON): {raw_message}", flush=True)
        return

    msg_type = data.get("type")
    payload = data.get("payload")

    print(f"Mensaje recibido -> type: {msg_type}, payload: {payload}", flush=True)

    response = {"type": "ack", "received": data}
    await websocket.send(json.dumps(response))


async def start_server(host="localhost", port=8765):
    print(f"Servidor WebSocket escuchando en ws://{host}:{port}", flush=True)
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # se mantiene corriendo indefinidamente