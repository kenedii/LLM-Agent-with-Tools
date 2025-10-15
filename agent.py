import re
import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()  # Load .env vars

def get_llm_provider():
    """Return the currently selected provider from session state (set in app.py)."""
    return st.session_state.get('llm_provider', 'openai')


def generate_response(user_input: str, provider: str = None) -> str:
    """
    Generates response using provider (openai or deepseek).
    System prompt teaches tag usage.
    """
    if provider is None:
        provider = get_llm_provider()

    system_prompt = """You are a helpful AI agent in a Streamlit chat. Respond concisely and helpfully.
    To render components in chat, wrap instructions in XML-like tags:
    - <chart>data: JSON array e.g. [{"value":10,"name":"Q1"}]; type: bar|line</chart> for ECharts.
    - <map>lat: 40.7128; lon: -74.0060</map> for Folium map.
    - <code>language: python; content: print("Hello")</code> for a simple code block/editor.
    - <embedcode>language: python; content: print("Hello Ace!")</embedcode> for an embedded Ace editor.
    - <lightchart>series: JSON array of numbers; labels: JSON array of labels</lightchart> for a lightweight chart.
    Only use tags when relevant (e.g., if user asks for chart/map/code). Keep plain text natural.
    """

    provider = provider.lower()
    if provider == 'openai':
        return _openai_response(system_prompt, user_input)
    elif provider == 'deepseek':
        return _deepseek_response(system_prompt, user_input)
    else:
        # Defensive: UI should not present other options, but give helpful message.
        return "Error: Unknown provider selected. Please choose 'openai' or 'deepseek' in the sidebar."


def _openai_response(system_prompt: str, user_input: str) -> str:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "OpenAI API key missing. Add OPENAI_API_KEY to your .env and restart."
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini" if False else "gpt-3.5-turbo",  # change if you want different model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {str(e)}. Please check your key and network."


def _deepseek_response(system_prompt: str, user_input: str) -> str:
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        return "DeepSeek API key missing. Add DEEPSEEK_API_KEY to your .env and restart."
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek Error: {str(e)}. Please check your key and network."


def parse_tags(response: str):
    """
    Parse XML-like tags safely. Returns plain_text and a list of (tag_type, params).
    Example tag content format inside is 'key: value; key2: value2'
    """
    tags = []
    pattern = r'<(\w+)>(.*?)</\1>'
    matches = re.findall(pattern, response, re.DOTALL)
    for tag_type, content in matches:
        params = {}
        for pair in content.split(';'):
            if ':' in pair:
                key, value = pair.strip().split(':', 1)
                params[key.strip()] = value.strip()
        tags.append((tag_type.lower(), params))
    # Remove all tags from plain text
    plain_text = re.sub(pattern, '', response, flags=re.DOTALL).strip()
    return plain_text or " ", tags  # ensure non-empty plain text
