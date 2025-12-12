import os
import time
import logging
from flask import Flask, render_template, request, jsonify
from agent import ShoppingAgent

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object("config")

# --- Global Agent ---
agent = None

def init_agent():
    global agent
    try:
        logger.info("Initializing Shopping Agent...")
        agent = ShoppingAgent()
        logger.info("Shopping Agent Ready.")
    except Exception as e:
        logger.error(f"Failed to initialize Agent: {e}")

# Call init immediately
init_agent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not agent:
            return jsonify({"error": "Agent not initialized"}), 500
            
        user_input = request.form.get('user_input')
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        
        # We can eventually pass history here if the frontend sends it, 
        # or rely on the agent's internal memory (Chroma)
        response_text = agent.chat(user_input)
        return jsonify({"response": response_text})
    except Exception as e:
        logger.error(f"Route error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    # For now, we just acknowledge. The Agent manages state.
    # Future: agent.reset_memory()
    return jsonify({"status": "success", "message": "Memory cleared (Simulated)."})

@app.route('/simulate_purchase', methods=['POST'])
def simulate_purchase():
    """Trigger a mock purchase event."""
    try:
        product = request.form.get('product', 'Generic Item')
        category = request.form.get('category', 'General')
        
        if agent and agent.connector.simulate_purchase(product, category):
             return jsonify({"status": "success", "message": f"Successfully purchased {product}!"})
        else:
             return jsonify({"error": "Failed to simulate purchase"}), 500
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/train', methods=['POST'])
def train():
    """Feedback loop input."""
    try:
        product = request.form.get('product')
        liked = request.form.get('liked') == 'true'
        
        # Simple extraction if product name isn't sent explicitly, 
        # but for now we expect the frontend to send it.
        if not product:
             return jsonify({"error": "No product specified"}), 400

        if agent and agent.train_preference(product, liked):
            action = "Liked" if liked else "Disliked"
            return jsonify({"status": "success", "message": f"Agent learned you {action} {product}"})
        return jsonify({"error": "Training failed"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure templates folder exists
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    logger.info("Starting Flask Server...")
    app.run(debug=False, port=5000)