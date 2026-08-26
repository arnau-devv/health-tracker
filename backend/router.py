from modules.sports.strength_training.handlers import (
    handle_save_exercise, handle_save_workout, 
    handle_get_strength_training_data, handle_get_heatmap_data
)

MESSAGNE_HANDLERS = {
    "save_exercise": handle_save_exercise,
    "save_workout": handle_save_workout,
    "get_strength_training_data": handle_get_strength_training_data,
    "get_heatmap_data": handle_get_heatmap_data
}



async def route_message(websocket, msg_type: str, payload: dict) -> bool:
    """Returns True if a handler was found and executed, False otherwise."""
    handler = MESSAGNE_HANDLERS.get(msg_type)
    
    if handler is None:
        return False
    
    await handler(websocket, payload)
    return True