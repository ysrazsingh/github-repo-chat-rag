from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_CONTEXT_CHARS = 12000

def trim_context(context):
    return context[:MAX_CONTEXT_CHARS]


def build_prompt_with_verification(query, context):
    return f"""
Answer ONLY using the context.

Then provide:
1. Final Answer
2. Supporting Snippets (copy exact lines)

If not found → say "Not found in repository"

Context:
{context}

Question:
{query}
"""

def validate_answer(answer: str):
    if "not found" in answer.lower():
        return answer

    # basic sanity check
    if len(answer.strip()) < 20:
        return "Not enough information found in repository"

    return answer

def build_prompt(query: str, context: str):
    return f"""
You are a codebase assistant.

Answer the question using ONLY the provided context.

Rules:
- Do NOT use outside knowledge
- If the answer is not in the context, say: "Not found in repository"
- Be precise and technical
- Cite file paths when possible

Context:
{context}

Question:
{query}

Answer:
"""
def generate_answer(query, context):
    context = trim_context(context)

    prompt = build_prompt(query, context)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict code assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0  # 🔥 critical for accuracy
    )

    answer = response.choices[0].message.content

    return validate_answer(answer)