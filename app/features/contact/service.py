from agents import Runner

from ...llm_agent import get_agent


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
        "- Email needs to be addressed to José"
        "- Do not include the subject on the message"
        "- Avoid commitments or scheduling.\n- Include a brief sign-off with the sender name."
    )

    agent = get_agent()
    result = await Runner.run(
        agent,
        user_prompt,
    )
    return (result.final_output or "").strip()



async def improve_contact_draft(draft: str, comment: str) -> str:
    """Improve a contact message draft based on a user's improvement comment.

    Preserve the original intent and any existing sign-off if appropriate. Do not
    add a subject line, and keep the message addressed to José.
    """
    user_prompt = (
        "You will receive a contact message draft and a user comment explaining how to improve it.\n"
        "Do not include the subject line. Keep it addressed to José. Preserve a brief sign-off if present.\n\n"
        f"Draft:\n{draft}\n\n"
        f"User comment:\n{comment}\n\n"
        "Return only the improved message."
    )

    agent = get_agent()
    result = await Runner.run(
        agent,
        user_prompt,
    )
    return (result.final_output or "").strip()


