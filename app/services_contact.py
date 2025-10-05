from agents import Runner

from .llm_agent import get_agent


async def draft_contact_message(sender_name: str, sender_email: str, subject: str) -> str:
    """Generate a concise, friendly contact message for a portfolio contact form.

    The draft should be professional, warm, and tailored to the subject. Keep it short
    (80-140 words) and avoid making promises. Include a polite sign-off.
    """
    user_prompt = (
        "Draft a message to include in a contact form. Personalize it to the sender.\n"
        f"Sender name: {sender_name}\n"
        f"Sender email: {sender_email}\n"
        f"Subject: {subject}\n\n"
        "Constraints:\n- Keep between 80 and 140 words.\n- Warm and professional tone.\n"
        "- Avoid commitments or scheduling.\n- Include a brief sign-off with the sender name."
    )

    agent = get_agent()
    result = await Runner.run(
        agent,
        user_prompt,
    )
    return (result.final_output or "").strip()


