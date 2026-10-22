# ChatGPT Behavior MCP Server

A **safe and ethical** Model Context Protocol (MCP) server for ChatGPT.

It gives you light control over how ChatGPT answers — persona, tone, and extra context — **without** allowing jailbreaks, safety bypasses, or harmful instructions.

## What it does

| Tool | Purpose |
|------|---------|
| `set_persona` | Set a temporary friendly style (e.g. "patient coding mentor") |
| `clear_persona` | Reset to default style |
| `add_context_note` | Add short context the model should remember |
| `list_context_notes` | Show stored notes |
| `clear_context_notes` | Delete all notes |
| `get_current_guidance` | Return active persona + notes |
| `get_safe_prompt_template` | Get ready-made ethical prompts (`teacher`, `code_review`, `summarizer`, `brainstorm`, `explain_simple`) |

Also exposes a resource `guidance://current` and a prompt `apply_persona_prompt`.

Any attempt to set a persona that contains jailbreak-related words is automatically rejected.

## Requirements

- Python 3.11+
- A public HTTPS URL (or OpenAI Secure MCP Tunnel / ngrok) so ChatGPT can reach the server

## Quick start

```bash
git clone https://github.com/SlabyLol/chatgpt-behavior-mcp.git
cd chatgpt-behavior-mcp
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

The server starts with **streamable-http** transport (the one ChatGPT expects).

For local testing you can also use the MCP Inspector:

```bash
uv run mcp dev server.py
```

## Connect to ChatGPT

1. Deploy the server somewhere with a public HTTPS endpoint (or use ngrok / OpenAI Secure MCP Tunnel).
2. In ChatGPT (web) go to **Plugins** → **Add custom MCP server**.
3. Enter a name, paste the server URL (usually ending with `/mcp` or the root depending on your setup), choose authentication ("No authentication" is fine for this demo).
4. Accept the risk warning and create the plugin.

Once connected, ChatGPT can call the tools above during a conversation.

## Safety design

- Persona text is scanned for common jailbreak keywords and rejected if found.
- All tools are designed only for positive style and context control.
- The server never tries to override OpenAI safety policies.
- No tools for executing code, accessing files, or performing write actions on external systems.

## License

MIT – use it, modify it, keep it ethical.

---

Made for people who want better control over ChatGPT style **without** going dark side.
