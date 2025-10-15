import streamlit as st
import json
import os
import re
from agent import generate_response, parse_tags
from renderers import render_component
from dotenv import load_dotenv

load_dotenv()


if not hasattr(st, "rerun"):
    st.rerun = st.experimental_rerun


st.set_page_config(page_title="AI Chatbot Agent", page_icon="🤖", layout="wide")

CHAT_DIR = "chat_history"
os.makedirs(CHAT_DIR, exist_ok=True)


# Providers and Models

PROVIDERS = {
    "openai": {
        "models": [
            ("gpt-4o", "GPT-4o (Advanced)"),
            ("gpt-4o-mini", "GPT-4o-Mini (Economy)"),
            ("gpt-3.5-turbo", "GPT-3.5-Turbo (Budget)")
        ]
    },
    "deepseek": {
        "models": [
            ("deepseek-chat", "DeepSeek Chat"),
            ("deepseek-reasoner", "DeepSeek Reasoner")
        ]
    }
}

try:
    from streamlit_option_menu import option_menu
    OPTION_MENU_AVAILABLE = True
except Exception:
    OPTION_MENU_AVAILABLE = False

st.sidebar.title("Settings")

# --- Provider select ---
provider = st.sidebar.selectbox("LLM Provider:", list(PROVIDERS.keys()),
                                index=0, key="provider_select")

# --- Model select ---
model_choices = PROVIDERS[provider]["models"]
model_labels = [m[1] for m in model_choices]
selected_label = st.sidebar.selectbox("Model:", model_labels, index=0, key="model_select")
selected_model = next(mid for mid, label in model_choices if label == selected_label)

# Store selections
st.session_state["llm_provider"] = provider
st.session_state["llm_model"] = selected_model


# Chat session management

st.sidebar.markdown("---")
st.sidebar.header("Chat Sessions")

def list_saved_chats():
    files = [f for f in os.listdir(CHAT_DIR) if f.endswith(".json")]
    return sorted(files)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_name" not in st.session_state:
    st.session_state.chat_name = "Untitled"
if "available_chats" not in st.session_state:
    st.session_state.available_chats = list_saved_chats()

available = st.session_state.available_chats
selected_chat = st.sidebar.selectbox("Saved chats:", (["-- new chat --"] + available),
                                     key="saved_chat_select")

# --- Helper ---
def sanitize_filename(name: str):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name).strip('_') or "chat"

def auto_save_chat():
    """Save chat automatically after every message."""
    if not st.session_state.messages:
        return
    name = st.session_state.get("chat_name", "Untitled")
    filename = sanitize_filename(name) + ".json"
    path = os.path.join(CHAT_DIR, filename)
    payload = {
        "chat_name": name,
        "provider": st.session_state.get("llm_provider", "openai"),
        "model": st.session_state.get("llm_model", ""),
        "messages": st.session_state.get("messages", [])
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        st.session_state.available_chats = list_saved_chats()
    except Exception as e:
        st.sidebar.error(f"Auto-save failed: {e}")

# --- New Chat ---
if st.sidebar.button("New Chat"):
    if st.session_state.messages:
        auto_save_chat()
    st.session_state.messages = []
    st.session_state.chat_name = "Untitled"
    st.rerun()

# --- Load Chat ---
if selected_chat and selected_chat != "-- new chat --":
    if st.sidebar.button("Load Chat"):
        path = os.path.join(CHAT_DIR, selected_chat)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state.messages = data.get("messages", [])
            st.session_state.chat_name = data.get("chat_name", selected_chat.replace(".json", ""))
            st.session_state["llm_provider"] = data.get("provider", "openai")
            st.session_state["llm_model"] = data.get("model", "gpt-3.5-turbo")
            st.success(f"Loaded chat: {selected_chat}")
            st.session_state.available_chats = list_saved_chats()
        except Exception as e:
            st.error(f"Failed to load chat: {e}")

# --- Save manually ---
st.sidebar.text_input("Chat name:", value=st.session_state.chat_name, key="chat_name_input")
if st.sidebar.button("Save Chat"):
    name = st.session_state.get("chat_name_input", "Untitled").strip()
    if not name:
        st.sidebar.error("Enter a valid name to save.")
    else:
        filename = f"{sanitize_filename(name)}.json"
        path = os.path.join(CHAT_DIR, filename)
        payload = {
            "chat_name": name,
            "provider": st.session_state.get("llm_provider", "openai"),
            "model": st.session_state.get("llm_model", ""),
            "messages": st.session_state.get("messages", [])
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            st.sidebar.success(f"Saved as {filename}")
            st.session_state.available_chats = list_saved_chats()
        except Exception as e:
            st.sidebar.error(f"Save failed: {e}")

# --- Delete Chat ---
if selected_chat and selected_chat != "-- new chat --":
    if st.sidebar.button("Delete Chat"):
        path = os.path.join(CHAT_DIR, selected_chat)
        try:
            os.remove(path)
            st.session_state.available_chats = list_saved_chats()
            st.sidebar.success(f"Deleted {selected_chat}")
            st.session_state.messages = []
            st.session_state.chat_name = "Untitled"
        except Exception as e:
            st.sidebar.error(f"Delete failed: {e}")

st.sidebar.markdown("---")
st.sidebar.write("Chats auto-save after every message and when new chats start.")


# Main chat area
st.title("🤖 AI Chatbot Agent — Multi-Model Edition")
st.caption(f"Provider: **{st.session_state.get('llm_provider','openai')}** • "
           f"Model: **{st.session_state.get('llm_model','gpt-3.5-turbo')}** • "
           f"Chat: **{st.session_state.get('chat_name','Untitled')}**")

chat_placeholder = st.container()

with chat_placeholder:
    for i, message in enumerate(st.session_state.messages):
        role = message.get("role", "assistant")
        content = message.get("content", "")
        try:
            with st.chat_message(role):
                st.markdown(content)
                for tag_type, params in message.get("components", []):
                    success = render_component(tag_type, params)
                    if not success:
                        st.markdown(f"*(Failed to render {tag_type})*")
        except Exception:
            st.markdown(f"**{role}**: {content}")
            for tag_type, params in message.get("components", []):
                render_component(tag_type, params)

# New Streamlit chat input handles Enter automatically
user_prompt = st.chat_input("Type your message and press Enter")

# Also include a Send button for mouse users
send = st.button("Send")

# Either pressing Enter or clicking Send will trigger this
if user_prompt or send:
    if user_prompt:  # chat_input returns value only when Enter is pressed
        message_text = user_prompt
    else:
        # Fallback: if user clicked Send without pressing Enter
        message_text = st.session_state.get("chat_input", "")

    if message_text.strip():
        # Auto name new chats
        if not st.session_state.messages:
            chat_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', message_text[:30]).strip('_') or "chat"
            st.session_state.chat_name = chat_name
        st.session_state.messages.append({"role": "user", "content": message_text, "components": []})
        auto_save_chat()
        st.rerun()


# Generate assistant response
if st.session_state.messages:
    last_msg = st.session_state.messages[-1]
    if last_msg.get("role") == "user" and not last_msg.get("_replied"):
        prompt = last_msg.get("content")
        st.session_state.messages[-1]["_replied"] = True

        with st.chat_message("assistant"):
            try:
                response = generate_response(prompt, provider=st.session_state.get("llm_provider", "openai"))
                plain_text, tags = parse_tags(response)
                st.markdown(plain_text)
                components = []
                for tag_type, params in tags:
                    success = render_component(tag_type, params)
                    if success:
                        components.append((tag_type, params))
                    else:
                        st.markdown(f"*(Render failed for {tag_type})*")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": plain_text,
                    "components": components
                })
                auto_save_chat()
            except Exception as e:
                error_msg = f"Oops! Error generating response: {str(e)}"
                st.markdown(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "components": []
                })
        st.rerun()

# Quick actions

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Clear Chat (local)"):
        st.session_state.messages = []
        st.session_state.chat_name = "Untitled"
        st.success("Cleared chat.")

with col2:
    if st.button("Export Chat (.json)"):
        payload = {
            "chat_name": st.session_state.get("chat_name", "Untitled"),
            "provider": st.session_state.get("llm_provider", "openai"),
            "model": st.session_state.get("llm_model", ""),
            "messages": st.session_state.get("messages", [])
        }
        fname = f"{payload['chat_name']}.json"
        st.download_button(label="Download chat JSON",
                           data=json.dumps(payload, indent=2),
                           file_name=fname, mime="application/json")

with col3:
    if st.button("Save to history"):
        name = st.session_state.get("chat_name_input", st.session_state.get("chat_name", "Untitled")).strip()
        if not name:
            st.error("Please set a chat name in the sidebar to save.")
        else:
            filename = f"{sanitize_filename(name)}.json"
            path = os.path.join(CHAT_DIR, filename)
            payload = {
                "chat_name": name,
                "provider": st.session_state.get("llm_provider", "openai"),
                "model": st.session_state.get("llm_model", ""),
                "messages": st.session_state.get("messages", [])
            }
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2)
                st.success(f"Saved to {filename}")
                st.session_state.available_chats = list_saved_chats()
            except Exception as e:
                st.error(f"Save failed: {e}")
