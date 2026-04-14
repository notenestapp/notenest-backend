from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass(frozen=True)
class NormalizedInitResponse:
    provider: str
    reference: str
    checkout_url: str
    raw: Dict[str, Any]


@dataclass(frozen=True)
class NormalizedVerifyResponse:
    provider: str
    reference: str
    success: bool
    status: str
    raw: Dict[str, Any]


class PaymentProvider(Protocol):
    slug: str

    def initialize_payment(
        self,
        *,
        email: str,
        amount_kobo: int,
        currency: str,
        reference: str,
        callback_url: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NormalizedInitResponse: ...

    def verify_payment(
        self,
        *,
        reference: str,
        provider_payload: Dict[str, Any],
    ) -> NormalizedVerifyResponse: ...

