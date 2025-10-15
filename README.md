# LLM-Agent-with-Tools-Streamlit-App
Chat with OpenAI and Deepseek models that have access to tools to display charts, maps, and code within the chat.

This conversational AI interface built with **Streamlit**, allowing interaction with multiple large language models (LLMs) such as **OpenAI GPT models** and **DeepSeek** models.  
Chats can be saved, reloaded, and enhanced with rich interactive components — like charts, maps, and code editors — dynamically rendered in chat responses.

---

## ✨ Features

- 💬 **Multi-Model Chatting** — switch between OpenAI (GPT-4o, GPT-4o-Mini, GPT-3.5-Turbo) and DeepSeek (Chat, Reasoner).
- 🧠 **Auto-Saved Conversations** — chats are automatically stored in JSON files and can be renamed or reloaded later.
- 🧾 **Component-Enhanced Replies** — the AI can include data visualizations, code editors, or maps directly in its responses.
- ⚙️ **Streamlit UI Components** — minimal yet powerful layout using built-in and community Streamlit components.

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your API keys

Create a .env file in the project root:

```
OPENAI_API_KEY=your_openai_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### 3. Run the app

```
streamlit run app.py
```

🧩 Streamlit Components Used

Below are the extra Streamlit component libraries and what they do in this project:

🗺️ Folium (streamlit-folium)

Used to display interactive maps directly inside chat messages.
When the AI responds with <map> tags, a Folium map (with markers and zoom) is rendered inside the chat window.

📊 ECharts (streamlit-echarts)

Renders interactive bar and line charts.
Used when the AI outputs <chart> tags containing JSON data — ECharts handles dynamic, configurable chart visualizations.

💻 Ace Code Editor (streamlit-ace)

Provides an inline code editor inside the chat.
When the AI uses <embedcode> tags, users can view and edit runnable code with syntax highlighting in real-time.

📈 Lightweight Charts (streamlit-lightweight-charts)

A compact charting library for time-series or trend data.
Used via <lightchart> tags — ideal for financial, performance, or continuous data visualization.

🧭 Option Menu (streamlit-option-menu)

Adds a clean sidebar navigation menu.
Used to improve organization of settings like model selection or page navigation when available.
