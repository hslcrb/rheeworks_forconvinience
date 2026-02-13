# JUNI AI 릴레이 API 가이드 / JUNI AI Relay API Guide

> [!TIP]
> 이 문서는 JUNI AI 릴레이 엔드포인트를 사용하는 방법을 설명합니다.  
> (This document describes how to use the JUNI AI relay endpoints.)

## 1. Authentication / 인증
별도의 클라이언트 키는 필요하지 않으며, 서버 측 환경 변수를 통해 인증이 처리됩니다.  
(No separate client keys are required; authentication is handled via server-side environment variables.)

## 2. Endpoints / 엔드포인트
- **Gemini**: `POST https://rheehose.com/api/ai/v1/juni/gemini/relay`
- **Mistral**: `POST https://rheehose.com/api/ai/v1/juni/mistral/relay`

## 3. curl Examples / curl 예시

### Gemini
```bash
curl -sS -X POST 'https://rheehose.com/api/ai/v1/juni/gemini/relay' \
  -H 'Content-Type: application/json' \
  --data '{"contents":[{"parts":[{"text":"Hello JUNI."}]}]}'
```

### Mistral (Streaming / 스트리밍)
```bash
curl -sS -X POST 'https://rheehose.com/api/ai/v1/juni/mistral/relay' \
  -H 'Content-Type: application/json' \
  --data '{"model":"mistral-tiny","messages":[{"role":"user","content":"Hello JUNI."}],"stream":true}'
```

## 4. Python Example / Python 예시
표준 라이브러리(`urllib`)만을 사용한 예시입니다.  
(Example using only the standard library (`urllib`).)

```python
import json
import urllib.request

def call_juni(prompt: str, model: str = "mistral"):
    url = f"https://rheehose.com/api/ai/v1/juni/{model}/relay"
    
    # Mistral format
    if model == "mistral":
        body = {
            "model": "mistral-tiny",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    # Gemini format
    else:
        body = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except Exception as e:
        return {"error": str(e)}

# Usage
response = call_juni("What is the vision of RHEE CREATIVE?")
print(json.dumps(response, indent=2, ensure_ascii=False))
```

---
© 2008-2026 Rheehose (Rhee Creative). All rights reserved.
