import os

import httpx
from fastapi import HTTPException

from app.config import MAX_CONTEXT_CHARS


class OllamaService:
    def __init__(self) -> None:
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "phi3")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "120"))

    async def generate_response(self, message: str) -> str:
        messages = [{"role": "user", "content": message}]
        return await self._send_messages(messages)

    async def generate_with_context(
        self,
        message: str,
        context: str,
        source_label: str,
    ) -> str:
        truncated_context = context[:MAX_CONTEXT_CHARS]
        system_prompt = (
            f"Você é um assistente local que responde com base no conteúdo de um {source_label}. "
            "Use apenas as informações do contexto fornecido. "
            "Se a resposta não estiver no contexto, informe claramente que não encontrou a informação.\n\n"
            f"Contexto:\n{truncated_context}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        return await self._send_messages(messages)

    async def _send_messages(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]
        except httpx.ConnectError as exc:
            raise HTTPException(
                status_code=503,
                detail="Não foi possível conectar ao Ollama. Verifique se o serviço está em execução.",
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Erro ao comunicar com o Ollama: {exc.response.text}",
            ) from exc
        except (KeyError, TypeError) as exc:
            raise HTTPException(
                status_code=502,
                detail="Resposta inválida recebida do Ollama.",
            ) from exc
