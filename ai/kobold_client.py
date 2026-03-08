import requests, json

URL = "http://localhost:5001/v1/chat/completions"

SYSTEM = {
    "role": "system",
    "content": (
        "Eres Athena A.I, un AGENTE DE PROGRAMACIÓN.\n"
        "NO generes imágenes.\n"
        "Planifica antes de ejecutar.\n"
        "Muestra siempre tus pasos."
    )
}

def stream_athena(prompt, on_token):
    payload = {
        "model": "koboldcpp",
        "messages": [SYSTEM, {"role": "user", "content": prompt}],
        "stream": True,
        "temperature": 0.3,
        "max_tokens": 100000
    }

    r = requests.post(URL, json=payload, stream=True)
    for line in r.iter_lines():
        if not line:
            continue
        if line.startswith(b"data: "):
            data = line.replace(b"data: ", b"").decode()
            if data == "[DONE]":
                break
            try:
                token = json.loads(data)["choices"][0]["delta"].get("content")
                if token:
                    on_token(token)
            except:
                pass
