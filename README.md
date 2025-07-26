# Food Delivery Chatbot

A conversational chatbot for ordering food, built with **Dialogflow**, **FastAPI**, and **MySQL**.
Users can place, modify, complete, and track orders via natural language.

---

## 🚀 Features

* **order.add**: Add items and quantities to an ongoing order
* **order.remove**: Remove items from the current order
* **order.complete**: Finalize and save the order to the database
* **track.order**: Query the status of a saved order by its ID

---

## 📦 Tech Stack

| Layer        | Technology                                 |
| ------------ | ------------------------------------------ |
| NLU / Intent | Dialogflow Messenger / Webhook integration |
| Backend      | Python 3.10, FastAPI                       |
| Database     | MySQL                                      |
| Deployment   | uvicorn                                    |

---

## 🔧 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/olavodd42/food-delivery-chatbot.git
cd food-delivery-chatbot
```

### 2. Create & initialize the database

1. Start MySQL and log in:

   ```bash
   mysql -u root -p
   ```

2. Create schema & tables:

   ```sql
   CREATE DATABASE food_delivery;
   USE food_delivery;

   -- run the init_db script
   SOURCE db/init_db.sql;
   ```

   This will create:

   * `food_items` (catalog of menu items)
   * `order_header` (order sessions)
   * `orders` (order line items)
   * `order_tracking` (status per order)

3. Verify the sample menu items:

   ```sql
   SELECT * FROM food_items;
   ```

### 3. Configure environment

Copy the example `.env.example` to `.env` and update:

```dotenv
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=food_delivery
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the backend

```bash
uvicorn main:app --reload
```

Your FastAPI webhook will be available at `http://localhost:8000/webhook`.

### 6. Encrypt the connection

```bash
ngrok http http://127.0.0.1:8000/
```
This will provide a public URL for your webhook, e.g., `https://<your-ngrok-id>.ngrok.io/webhook`.

---

## 💬 Dialogflow Setup

1. **Agent**: Create or open your Agent in Dialogflow Console.
2. **Entities**: Import the `entities/food.json` file (custom `@food` with 32 items).
3. **Intents**:

   * **order.add** (context: `ongoing-order`)
   * **order.remove** (context: `ongoing-order`)
   * **order.complete** (context: `ongoing-order`)
   * **track.order** (context: `ongoing-tracking`)
4. **Fulfillment**: Enable Webhook, set URL to `https://<your-domain>/webhook`.

---

## 🌐 Frontend

We use the **Dialogflow Messenger** Web Component:

```html
<df-messenger
  intent="WELCOME"
  chat-title="FoodBot"
  agent-id="YOUR_AGENT_ID"
  language-code="en">
</df-messenger>
<script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>
```

Embed in `index.html` with vibrant CSS (see `frontend/index.html`).

---

## 📂 Project Structure

```
.
├── backend/
│   └── db_helper.py      # Database helper functions
|   └── main.py             # FastAPI app + webhook handlers
├── db/
│   ├── db_config.sql        # SQL script to initialize the database
├── dialogflow-agent/
│   └── entities/
│       └── food-item.json       # Custom entity for food items
|       └── food-items_entries_en.json # Synonyms for food items
│   └── intents/
|       └── Default Fallback Intent.json # Default fallback intent
|       └── Default Welcome Intent.json # Default welcome intent
|       └── Default Welcome Intent_usersays_en.json # User says for welcome intent
|       └── new_order.json # Intent for new orders
|       └── new_order_usersays_en.json # User says for new orders
|       └── order.add - context_ ongoing-order.json.json # Intent for adding items to an order
|       └── order.add - context_ ongoing-order_usersays_en.json # User says for adding items
|       └── order.complete - context_ ongoing-order.json # Intent for completing an order
|       └── order.complete - context_ ongoing-order_usersays_en.json # User says
|       └── order.remove - context_ ongoing-order.json # Intent for removing items from an order
|       └── order.remove - context_ ongoing-order_usersays_en.json # User says for removing items
|       └── track.order.json # Intent for tracking an order
|       └── track.order_usersays_en.json # User says for tracking an order
|       └── track.order - context_ ongoing-tracking.json # Intent for tracking an order with context
|       └── track.order - context_ ongoing-tracking_usersays_en.json # User
|   └── agent.json          # Dialogflow agent configuration
|   └── package.json       # Dialogflow package configuration
|- frontend/
|   └── index.html          # Example chat frontend
|- .env.example          # Environment variable example
└── README.md
```

---

## 🛠️ Customization

* **Menu changes**: Edit `db/init_db.sql` and re-run to adjust `food_items`.
* **Entity synonyms**: Update `entities/food.json`, then re-import into Dialogflow.
* **Webhook logic**: Tweak handlers in `main.py`.

---

## 📬 Contact

For issues or contributions, please open a GitHub issue or pull request.
Made with ❤️ by Olavo Dalberto.
