from __future__ import annotations

from typing import Dict

from services.payment_providers.base import PaymentProvider
from services.payment_providers.flutterwave import FlutterwaveProvider
from services.payment_providers.paystack import PaystackProvider


_PROVIDERS: Dict[str, PaymentProvider] = {
    "paystack": PaystackProvider(),
    "flutterwave": FlutterwaveProvider(),
}


def normalize_provider(provider: str | None) -> str:
    return (provider or "paystack").strip().lower()


def get_payment_provider(provider: str | None) -> PaymentProvider:
    slug = normalize_provider(provider)
    if slug not in _PROVIDERS:
        raise ValueError(f"Unsupported payment provider '{provider}'")
    return _PROVIDERS[slug]

