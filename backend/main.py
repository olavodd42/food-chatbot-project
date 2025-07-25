from fastapi import FastAPI, Request
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from starlette.responses import JSONResponse
from db_helper import get_order_status

import uvicorn

app = FastAPI()

class Context(BaseModel):
    name: str
    lifespanCount: Optional[int] = None       # agora opcional
    parameters: Optional[Dict[str, Any]] = {} # agora opcional e default vazio

class QueryResult(BaseModel):
    queryText: str
    parameters: Dict[str, Any]
    allRequiredParamsPresent: bool
    outputContexts: Optional[List[Context]] = None  # contexts também podem faltar
    intent: Dict[str, Any]
    intentDetectionConfidence: float

class WebhookRequest(BaseModel):
    responseId: str
    session: str
    queryResult: QueryResult
    originalDetectIntentRequest: Optional[Dict[str, Any]] = None



def extract_session_id(contexts: Optional[List[Context]]) -> Optional[str]:
    """
    Dialogflow contexts look like:
     projects/.../agent/sessions/{session_id}/contexts/{ctx_name}
    We'll pull {session_id} from the first context we find.
    """
    if not contexts:
        return None
    for ctx in contexts:
        parts = ctx.name.split("/")
        if "sessions" in parts:
            idx = parts.index("sessions")
            # session id follows immediately after "sessions"
            if idx + 1 < len(parts):
                return parts[idx + 1]
    return None


def handle_order_add(parameters: Dict[str, Any], session_id: Optional[str]) -> Dict[str, Any]:
    """
    Business logic for adding to an order.
    `parameters` will contain whatever Dialogflow extracted,
     e.g. {'food': ['Burger','Fries'], 'quantity': [2,1], ...}
    """
    # stub: echo back what was asked
    items = []
    qtys = []
    # assume parallel lists or single values
    raw_food = parameters.get("food")
    raw_qty = parameters.get("quantity")
    # normalize to lists
    if isinstance(raw_food, list):
        items = raw_food
    elif raw_food:
        items = [raw_food]
    if isinstance(raw_qty, list):
        qtys = raw_qty
    elif raw_qty:
        qtys = [raw_qty]

    parts = []
    for i, item in enumerate(items):
        q = qtys[i] if i < len(qtys) else 1
        parts.append(f"{q} x {item}")

    fulfillment_text = (
        f"Added to your order ({session_id}): " + ", ".join(parts)
        if parts
        else "I didn't catch what you'd like to add. Can you repeat?"
    )
    return {"fulfillmentText": fulfillment_text}


def handle_order_remove(parameters: Dict[str, Any], session_id: Optional[str]) -> Dict[str, Any]:
    """
    Business logic for removing from an order.
    """
    items = []
    raw_food = parameters.get("food")
    if isinstance(raw_food, list):
        items = raw_food
    elif raw_food:
        items = [raw_food]

    if items:
        fulfillment_text = (
            f"Removed from your order ({session_id}): " + ", ".join(items)
        )
    else:
        fulfillment_text = "I didn't catch which item to remove. Please specify."
    return {"fulfillmentText": fulfillment_text}

def handle_track_order(parameters: Dict[str, Any], session_id: Optional[str]) -> Dict[str, Any]:
    """
    Conecta ao MySQL e retorna o fulfillmentText com o status do pedido.
    """
    raw_number = parameters.get("number") or parameters.get("order_id")
    if isinstance(raw_number, list) and raw_number:
        order_id = raw_number[0]
    else:
        order_id = raw_number

    if order_id is None:
        return {"fulfillmentText": "I didn't catch your order ID. Could you please repeat it?"}

    status = get_order_status(order_id)
    if status:
        return {"fulfillmentText": f"Status for order {order_id}: {status}"}
    else:
        return {"fulfillmentText": f"No tracking information found for order ID {order_id}."}


@app.post("/webhook")
async def webhook(req: Request):
    payload = await req.json()
    wf_req = WebhookRequest(**payload)

    intent_name = wf_req.queryResult.intent.get("displayName")
    params = wf_req.queryResult.parameters
    session_id = extract_session_id(wf_req.queryResult.outputContexts)

    # Route to intent-specific handler
    if intent_name == "order.add":
        return handle_order_add(params, session_id)
    elif intent_name == "order.remove":
        return handle_order_remove(params, session_id)
    elif intent_name == "track.order - context: ongoing-tracking":
        return handle_track_order(params, session_id)
    else:
        # fallback for any other intents
        return {"fulfillmentText": f"Sorry, I don't know how to handle `{intent_name}`."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
