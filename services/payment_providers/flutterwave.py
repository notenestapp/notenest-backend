from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

from services.payment_providers.base import (
    NormalizedInitResponse,
    NormalizedVerifyResponse,
)


class FlutterwaveProvider:
    slug = "flutterwave"

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
        base_url = os.getenv("FLUTTERWAVE_BASE_URL", "https://api.flutterwave.com").rstrip("/")
        secret_key = os.getenv("FLUTTERWAVE_SECRET_KEY")

        if not secret_key:
            raise RuntimeError("FLUTTERWAVE_SECRET_KEY is not set")

        amount_naira = amount_kobo // 100  # Flutterwave expects naira
        payload: Dict[str, Any] = {
            "tx_ref": reference,
            "amount": amount_naira,
            "currency": currency,
            "redirect_url": callback_url,
            "customer": {"email": email},
        }
        if metadata:
            payload["meta"] = metadata

        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }

        res = requests.post(
            f"{base_url}/v3/payments",
            json=payload,
            headers=headers,
            timeout=30,
        )
        result = res.json()

        checkout_url = (result.get("data") or {}).get("link")
        if not checkout_url:
            raise RuntimeError(f"Flutterwave init failed: {result}")

        return NormalizedInitResponse(
            provider=self.slug,
            reference=reference,
            checkout_url=checkout_url,
            raw=result,
        )

    def verify_payment(
        self,
        *,
        reference: str,
        provider_payload: Dict[str, Any],
    ) -> NormalizedVerifyResponse:
        base_url = os.getenv("FLUTTERWAVE_BASE_URL", "https://api.flutterwave.com").rstrip("/")
        secret_key = os.getenv("FLUTTERWAVE_SECRET_KEY")
        if not secret_key:
            raise RuntimeError("FLUTTERWAVE_SECRET_KEY is not set")

        transaction_id = (
            provider_payload.get("transaction_id")
            or provider_payload.get("transactionId")
            or provider_payload.get("id")
        )
        if not transaction_id:
            return NormalizedVerifyResponse(
                provider=self.slug,
                reference=reference,
                success=False,
                status="missing_transaction_id",
                raw={"provider_payload": provider_payload},
            )

        headers = {"Authorization": f"Bearer {secret_key}"}
        res = requests.get(
            f"{base_url}/v3/transactions/{transaction_id}/verify",
            headers=headers,
            timeout=30,
        )
        result = res.json()

        data = result.get("data") or {}
        status = data.get("status") or "unknown"
        tx_ref = data.get("tx_ref") or data.get("txRef")

        success = status == "successful" and (not tx_ref or tx_ref == reference)

        return NormalizedVerifyResponse(
            provider=self.slug,
            reference=reference,
            success=success,
            status=status,
            raw=result,
        )

