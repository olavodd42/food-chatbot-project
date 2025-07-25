from fastapi import FastAPI, Request
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import uvicorn
from starlette.responses import JSONResponse

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
    Connects to the MySQL database and retrieves the status for the given order_id.
    """
    conn = mysql.connector.connect(
        host='localhost',         # replace with your host
        user='olavo',     # replace with your MySQL username
        password='12345678', # replace with your MySQL password
        database='`pandeyj_eatery`'  # replace with your database name
    )
    cursor = conn.cursor()

    query = "SELECT status FROM order_tracking WHERE order_id = %s"
    cursor.execute(query, (order_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None


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
