from openai import OpenAI

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)

print(response.choices[0].message.content)