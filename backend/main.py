from fastapi import FastAPI, Request
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from starlette.responses import JSONResponse
from db_helper import get_order_status, save_to_db

import uvicorn

app = FastAPI()

# ----- DTOs -----
class Context(BaseModel):
    name: str
    lifespanCount: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = {}

class QueryResult(BaseModel):
    queryText: str
    parameters: Dict[str, Any]
    allRequiredParamsPresent: bool
    outputContexts: Optional[List[Context]] = None
    intent: Dict[str, Any]
    intentDetectionConfidence: float

class WebhookRequest(BaseModel):
    responseId: str
    session: str
    queryResult: QueryResult
    originalDetectIntentRequest: Optional[Dict[str, Any]] = None

# ----- Helpers -----

def extract_session_id(contexts: Optional[List[Context]]) -> Optional[str]:
    if not contexts:
        return None
    for ctx in contexts:
        parts = ctx.name.split("/")
        if "sessions" in parts:
            idx = parts.index("sessions")
            if idx + 1 < len(parts):
                return parts[idx + 1]
    return None


def make_ongoing_order_context(full_session_path: str, lifespan: int = 5) -> Dict[str, Any]:
    # full_session_path is wf_req.session, e.g. 'projects/.../sessions/{session_id}'
    return {
        "name": f"{full_session_path}/contexts/ongoing-order",
        "lifespanCount": lifespan,
        "parameters": {}
    }

inprogress_orders: Dict[str, Dict[str, int]] = {}

# ----- Intent Handlers -----

def handle_order_add(params: Dict[str, Any], session_path: str, session_id: str) -> Dict[str, Any]:
    raw_food = params.get("food") or params.get("food-item")
    raw_qty  = params.get("quantity") or params.get("number")

    items = raw_food if isinstance(raw_food, list) else ([raw_food] if raw_food else [])
    qtys  = raw_qty  if isinstance(raw_qty, list)  else ([raw_qty]  if raw_qty  else [])

    if not session_id:
        return {"fulfillmentText": "Could not identify session. Please try again."}

    if session_id not in inprogress_orders:
        inprogress_orders[session_id] = {}
    session_order = inprogress_orders[session_id]

    parts = []
    for i, item in enumerate(items):
        q = int(qtys[i]) if i < len(qtys) else 1
        session_order[item] = session_order.get(item, 0) + q
        parts.append(f"{q} x {item}")

    if parts:
        fulfillment_text = f"Added to your order ({session_id}): " + ", ".join(parts)
        return {
            "fulfillmentText": fulfillment_text,
            "outputContexts": [make_ongoing_order_context(session_path)]
        }
    else:
        return {"fulfillmentText": "I didn't catch what you'd like to add. Can you repeat?"}


def handle_order_remove(params: Dict[str, Any], session_path: str, session_id: str) -> Dict[str, Any]:
    raw_food = params.get("food") or params.get("food-item")
    items = raw_food if isinstance(raw_food, list) else ([raw_food] if raw_food else [])

    if session_id in inprogress_orders:
        session_order = inprogress_orders[session_id]
        for item in items:
            session_order.pop(item, None)

    print(inprogress_orders)

    if items:
        return {"fulfillmentText": f"Removed from your order ({session_id}): " + ", ".join(items)}
    else:
        return {"fulfillmentText": "I didn't catch which item to remove. Please specify."}


def complete_order(params: Dict[str, Any], session_path: str, session_id: str) -> Dict[str, Any]:
    order = inprogress_orders.pop(session_id, {})
    if not order:
        return {"fulfillmentText": "Your order was empty. Nothing to complete."}

    # passe também session_id
    order_id = save_to_db(order, session_id)

    print(inprogress_orders)

    return {
        "fulfillmentText": (
            f"Your order has been placed! Your order ID is {order_id}. "
            "You can track it anytime by telling me 'track order' and giving me that number."
        )
    }

def handle_track_order(params: Dict[str, Any], session_path: str, session_id: str) -> Dict[str, Any]:
    raw_number = params.get("number") or params.get("order_id")
    order_id = raw_number[0] if isinstance(raw_number, list) and raw_number else raw_number
    if not order_id:
        return {"fulfillmentText": "I didn't catch your order ID. Could you please repeat it?"}

    status = get_order_status(int(order_id))
    if status:
        return {"fulfillmentText": f"Status for order {order_id}: {status}"}
    else:
        return {"fulfillmentText": f"No tracking information found for order ID {order_id}."}

# ----- Webhook Endpoint -----
@app.post("/webhook")
async def webhook(req: Request):
    payload = await req.json()
    wf_req = WebhookRequest(**payload)
    intent_name = wf_req.queryResult.intent.get("displayName")
    params = wf_req.queryResult.parameters
    session_path = wf_req.session  # full path: projects/.../sessions/{session_id}
    session_id = extract_session_id(wf_req.queryResult.outputContexts)
    handlers = {
        "order.add - context: ongoing-order": handle_order_add,
        "order.remove - context: ongoing-order": handle_order_remove,
        "order.complete - context: ongoing-order": complete_order,
        "track.order - context: ongoing-tracking": handle_track_order
    }
    handler = handlers.get(intent_name, lambda p, sp, sid: {"fulfillmentText": f"Unknown intent {intent_name}."})
    return JSONResponse(content=handler(params, session_path, session_id))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
