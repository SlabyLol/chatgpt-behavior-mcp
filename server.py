"""
ChatGPT Behavior MCP Server
===========================
A safe, ethical Model Context Protocol (MCP) server for ChatGPT.

It lets you gently shape ChatGPT responses by providing:
- Temporary persona / response-style instructions
- Extra context notes
- Reusable safe prompt templates

It deliberately refuses any request that tries to bypass safety rules,
jailbreak, or enable harmful behavior.
"""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP(
    name="ChatGPT Behavior Controller",
    instructions=(
        "This server helps shape ChatGPT's tone, persona and context in a safe way. "
        "Use the tools to set a temporary style, add context notes, or fetch a safe prompt template. "
        "Never use these tools to attempt jailbreaks, remove safety rules, or request harmful content."
    ),
)

# In-memory store for the current session (simple demo – not persistent)
_current_persona: str | None = None
_context_notes: list[str] = []


@mcp.tool()
def set_persona(
    persona: Annotated[
        str,
        Field(
            description=(
                "A short, positive description of the desired response style. "
                "Examples: 'friendly teacher', 'concise technical writer', "
                "'patient coding mentor', 'enthusiastic science explainer'. "
                "Must stay helpful and ethical."
            )
        ),
    ],
) -> str:
    """
    Set a temporary persona / response style for ChatGPT.
    The persona is applied as soft guidance only and never overrides safety rules.
    """
    global _current_persona

    forbidden = [
        "jailbreak",
        "ignore previous",
        "ignore all",
        "DAN",
        "developer mode",
        "no restrictions",
        "bypass",
        "unrestricted",
        "evil",
        "harmful",
        "illegal",
    ]
    lower = persona.lower()
    if any(word in lower for word in forbidden):
        return (
            "Rejected: The requested persona contains terms that could be used "
            "to bypass safety. Please choose a positive, helpful style instead."
        )

    _current_persona = persona.strip()
    return f"Persona set to: '{_current_persona}'. ChatGPT will try to match this style while remaining helpful and safe."


@mcp.tool()
def clear_persona() -> str:
    """Clear the currently set persona so ChatGPT returns to its default style."""
    global _current_persona
    _current_persona = None
    return "Persona cleared. ChatGPT will use its default helpful style."


@mcp.tool()
def add_context_note(
    note: Annotated[
        str,
        Field(
            description=(
                "A short piece of extra context you want ChatGPT to remember "
                "for the current conversation (e.g. 'User is learning Python', "
                "'Prefer metric units', 'Explain like I'm 12')."
            )
        ),
    ],
) -> str:
    """
    Add a short context note that ChatGPT can use to tailor answers.
    Notes are stored only for the current server session.
    """
    cleaned = note.strip()
    if len(cleaned) > 500:
        return "Note too long. Please keep context notes under 500 characters."
    if not cleaned:
        return "Empty note ignored."

    _context_notes.append(cleaned)
    return f"Context note added. Total notes: {len(_context_notes)}."


@mcp.tool()
def list_context_notes() -> str:
    """List all currently stored context notes."""
    if not _context_notes:
        return "No context notes stored."
    lines = [f"{i+1}. {n}" for i, n in enumerate(_context_notes)]
    return "Current context notes:\n" + "\n".join(lines)


@mcp.tool()
def clear_context_notes() -> str:
    """Remove all stored context notes."""
    global _context_notes
    count = len(_context_notes)
    _context_notes = []
    return f"Cleared {count} context note(s)."


@mcp.tool()
def get_current_guidance() -> str:
    """
    Return the currently active persona and context notes
    so ChatGPT can incorporate them into its replies.
    """
    parts: list[str] = []
    if _current_persona:
        parts.append(f"Active persona: {_current_persona}")
    else:
        parts.append("Active persona: (default)")

    if _context_notes:
        parts.append("Context notes:")
        for i, n in enumerate(_context_notes, 1):
            parts.append(f"  {i}. {n}")
    else:
        parts.append("Context notes: (none)")

    parts.append(
        "Remember: Always stay helpful, truthful and safe. "
        "Never ignore OpenAI safety policies."
    )
    return "\n".join(parts)


@mcp.tool()
def get_safe_prompt_template(
    template_name: Annotated[
        str,
        Field(
            description=(
                "Name of a safe prompt template. Available: "
                "'teacher', 'code_review', 'summarizer', 'brainstorm', 'explain_simple'."
            )
        ),
    ],
) -> str:
    """
    Return a ready-to-use, ethical prompt template that improves ChatGPT responses.
    """
    templates = {
        "teacher": (
            "You are a patient and encouraging teacher. "
            "Explain concepts step by step, check understanding, "
            "and use simple examples. Stay accurate and positive."
        ),
        "code_review": (
            "You are a careful code reviewer. "
            "Point out bugs, security issues, readability problems and possible improvements. "
            "Be constructive and suggest concrete fixes. Never recommend insecure practices."
        ),
        "summarizer": (
            "Summarize the following content clearly and neutrally. "
            "Keep the most important facts, remove fluff, and preserve the original meaning."
        ),
        "brainstorm": (
            "Help brainstorm creative but practical ideas. "
            "List several options, briefly evaluate pros and cons, "
            "and stay realistic and ethical."
        ),
        "explain_simple": (
            "Explain the topic in plain language as if talking to a curious beginner. "
            "Avoid jargon or define it immediately. Use analogies when helpful."
        ),
    }

    key = template_name.lower().strip()
    if key not in templates:
        available = ", ".join(templates.keys())
        return f"Unknown template '{template_name}'. Available templates: {available}"

    return templates[key]


@mcp.resource("guidance://current")
def current_guidance_resource() -> str:
    """Resource version of the current persona + context notes."""
    return get_current_guidance()


@mcp.prompt()
def apply_persona_prompt(
    topic: str = "the current question",
) -> str:
    """
    A prompt that asks ChatGPT to answer while respecting the active persona and context.
    """
    guidance = get_current_guidance()
    return (
        f"Please answer about {topic} while following this guidance:\n\n"
        f"{guidance}\n\n"
        "Stay helpful, accurate and within normal safety boundaries."
    )


if __name__ == "__main__":
    # Streamable HTTP is the transport ChatGPT expects for remote MCP servers
    mcp.run(transport="streamable-http")
