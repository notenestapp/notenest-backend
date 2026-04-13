from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

from services.payment_providers.base import (
    NormalizedInitResponse,
    NormalizedVerifyResponse,
)


class PaystackProvider:
    slug = "paystack"

    def initialize_payment(
        self,
        *,
        email: str,
        amount_kobo: int,
        currency: str,
        reference: str,
        callback_url: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NormalizedInitResponse:
        base_url = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co").rstrip("/")
        secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        if not secret_key:
            raise RuntimeError("PAYSTACK_SECRET_KEY is not set")

        payload: Dict[str, Any] = {
            "email": email,
            "amount": amount_kobo,  # Paystack expects kobo
            "reference": reference,
            "metadata": metadata or {},
            "callback_url": callback_url,
        }

        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{base_url}/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=30,
        )
        res_data = response.json()

        checkout_url = res_data["data"]["authorization_url"]
        return NormalizedInitResponse(
            provider=self.slug,
            reference=reference,
            checkout_url=checkout_url,
            raw=res_data,
        )

    def verify_payment(
        self,
        *,
        reference: str,
        provider_payload: Dict[str, Any],
    ) -> NormalizedVerifyResponse:
        base_url = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co").rstrip("/")
        secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        if not secret_key:
            raise RuntimeError("PAYSTACK_SECRET_KEY is not set")

        headers = {"Authorization": f"Bearer {secret_key}"}
        res = requests.get(
            f"{base_url}/transaction/verify/{reference}",
            headers=headers,
            timeout=30,
        )
        result = res.json()

        status = (result.get("data") or {}).get("status")
        success = status == "success"

        return NormalizedVerifyResponse(
            provider=self.slug,
            reference=reference,
            success=success,
            status=status or "unknown",
            raw=result,
        )

