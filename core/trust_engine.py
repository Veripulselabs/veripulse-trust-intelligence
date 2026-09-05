import re
import time
import asyncio
from typing import Optional, List, Tuple
import dns.resolver
import phonenumbers
from phonenumbers import geocoder, carrier as pn_carrier, PhoneNumberType

from app.models import (
    EmailIntelligence, PhoneIntelligence, CarrierInfo, TrustScoreResponse
)

# Common disposable domains
DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "sharklasers.com", "throwawaymail.com", "yopmail.com", "trashmail.com",
    "getairmail.com", "dispostable.com", "fakemailgenerator.com", "burnermail.io",
    "temp-mail.org", "mohmal.com", "nada.ltd", "crazymailing.com", "inboxkitten.com"
}

ROLE_PREFIXES = {
    "admin", "support", "sales", "info", "contact", "help", "billing",
    "office", "jobs", "marketing", "press", "legal", "security", "team"
}

FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "protonmail.com", "zoho.com", "mail.com", "gmx.com"
}

VIRTUAL_CARRIERS = {
    "twilio", "google voice", "bandwidth", "textnow", "telnyx", "sinch",
    "plivo", "skype", "vonage", "ringcentral", "nextiva", "grasshopper",
    "voxbone", "pinger", "enflick", "magicjack", "republic wireless"
}

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

class EmailEvaluator:
    @staticmethod
    async def evaluate(email_str: str) -> EmailIntelligence:
        email = email_str.strip().lower()
        signals = []
        risk = 0

        # Syntax check
        if not EMAIL_REGEX.match(email):
            return EmailIntelligence(
                email=email,
                is_valid=False,
                is_disposable=False,
                is_role_account=False,
                is_free_provider=False,
                has_mx_records=False,
                did_you_mean=None,
                domain="",
                risk_score=95,
                signals=["Malformed email syntax (RFC 5322 violation)"]
            )

        local_part, domain = email.split("@", 1)

        # Role account
        is_role = local_part in ROLE_PREFIXES
        if is_role:
            risk += 15
            signals.append(f"Generic role address prefix ({local_part}@)")

        # Free provider
        is_free = domain in FREE_PROVIDERS
        if is_free:
            signals.append(f"Public webmail provider ({domain})")

        # Disposable domain
        is_disposable = domain in DISPOSABLE_DOMAINS or "temp" in domain or "dispos" in domain
        if is_disposable:
            risk = max(risk, 90)
            signals.append(f"Known disposable / temporary email domain ({domain})")

        # DNS MX check
        has_mx = False
        if not is_disposable:
            try:
                loop = asyncio.get_running_loop()
                answers = await loop.run_in_executor(
                    None, lambda: dns.resolver.resolve(domain, 'MX', lifetime=2.0)
                )
                has_mx = len(answers) > 0
                signals.append("Active DNS MX records verified")
            except Exception:
                has_mx = False
                risk = max(risk, 80)
                signals.append(f"No routable MX records found for domain ({domain})")
        else:
            has_mx = True

        # Typo suggestion
        did_you_mean = None
        if domain == "gmial.com" or domain == "gmaill.com":
            did_you_mean = f"{local_part}@gmail.com"
        elif domain == "yaho.com":
            did_you_mean = f"{local_part}@yahoo.com"
        elif domain == "hotmial.com":
            did_you_mean = f"{local_part}@hotmail.com"

        if did_you_mean:
            risk = max(risk, 50)
            signals.append(f"Likely typo in domain; suggested: {did_you_mean}")

        return EmailIntelligence(
            email=email,
            is_valid=True,
            is_disposable=is_disposable,
            is_role_account=is_role,
            is_free_provider=is_free,
            has_mx_records=has_mx,
            did_you_mean=did_you_mean,
            domain=domain,
            risk_score=min(100, risk),
            signals=signals
        )

class PhoneEvaluator:
    @staticmethod
    def evaluate(phone_str: str, default_country: str = "US") -> PhoneIntelligence:
        raw = phone_str.strip()
        signals = []
        risk = 0

        try:
            parsed = phonenumbers.parse(raw, default_country)
            is_valid = phonenumbers.is_valid_number(parsed)
        except Exception:
            return PhoneIntelligence(
                phone_input=raw,
                is_valid=False,
                country_code="",
                risk_score=90,
                signals=["Unparseable phone number string"]
            )

        if not is_valid:
            return PhoneIntelligence(
                phone_input=raw,
                is_valid=False,
                country_code=phonenumbers.region_code_for_number(parsed) or "",
                risk_score=85,
                signals=["Invalid phone number format for region"]
            )

        country = phonenumbers.region_code_for_number(parsed) or default_country
        e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        nat = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

        ntype = phonenumbers.number_type(parsed)
        type_str = "UNKNOWN"
        if ntype == PhoneNumberType.MOBILE:
            type_str = "MOBILE"
        elif ntype == PhoneNumberType.FIXED_LINE:
            type_str = "FIXED_LINE"
        elif ntype == PhoneNumberType.VOIP:
            type_str = "VOIP"
        elif ntype == PhoneNumberType.TOLL_FREE:
            type_str = "TOLL_FREE"

        carrier_name = pn_carrier.name_for_number(parsed, "en") or "Unknown"
        is_virtual = (
            type_str == "VOIP" or
            any(v in carrier_name.lower() for v in VIRTUAL_CARRIERS)
        )

        if is_virtual:
            risk = max(risk, 85)
            signals.append(f"Virtual / VoIP provider detected ({carrier_name}) - high fraud risk for SMS OTP")
        elif type_str == "MOBILE":
            signals.append(f"Valid mobile subscriber line ({carrier_name}) - optimal for SMS delivery")
        elif type_str == "FIXED_LINE":
            risk = max(risk, 40)
            signals.append(f"Fixed landline ({carrier_name}) - cannot receive SMS OTP")

        return PhoneIntelligence(
            phone_input=raw,
            is_valid=True,
            country_code=country,
            e164_format=e164,
            international_format=intl,
            national_format=nat,
            carrier=CarrierInfo(
                name=carrier_name,
                line_type=type_str,
                is_virtual=is_virtual
            ),
            risk_score=risk,
            signals=signals
        )

class TrustEngine:
    @staticmethod
    async def evaluate(
        email: Optional[str] = None,
        phone: Optional[str] = None,
        country_code: str = "US"
    ) -> TrustScoreResponse:
        start_time = time.perf_counter()
        tasks = []
        signals = []

        if email:
            tasks.append(EmailEvaluator.evaluate(email))
        if phone:
            loop = asyncio.get_running_loop()
            tasks.append(loop.run_in_executor(None, PhoneEvaluator.evaluate, phone, country_code))

        results = await asyncio.gather(*tasks)

        email_intel = None
        phone_intel = None
        idx = 0
        if email:
            email_intel = results[idx]
            idx += 1
        if phone:
            phone_intel = results[idx]

        # Dual-Vector Synthesis
        composite_risk = 0
        if email_intel and phone_intel:
            composite_risk = max(email_intel.risk_score, phone_intel.risk_score)
            if email_intel.is_disposable and phone_intel.carrier and phone_intel.carrier.is_virtual:
                composite_risk = 98
                signals.append("CRITICAL: Both email and phone belong to disposable/virtual services (bot farm signature)")
            elif email_intel.is_disposable:
                composite_risk = max(composite_risk, 90)
                signals.append("Disposable email address detected")
            elif phone_intel.carrier and phone_intel.carrier.is_virtual:
                composite_risk = max(composite_risk, 85)
                signals.append("Virtual VoIP phone number detected")
                
            signals.extend([f"Email: {s}" for s in email_intel.signals])
            signals.extend([f"Phone: {s}" for s in phone_intel.signals])

        elif email_intel:
            composite_risk = email_intel.risk_score
            signals.extend([f"Email: {s}" for s in email_intel.signals])

        elif phone_intel:
            composite_risk = phone_intel.risk_score
            signals.extend([f"Phone: {s}" for s in phone_intel.signals])

        trust_score = max(0, min(100, 100 - composite_risk))

        if composite_risk >= 80:
            risk_level = "HIGH"
            action = "BLOCK"
        elif composite_risk >= 30:
            risk_level = "MEDIUM"
            action = "FLAG_FOR_REVIEW"
        else:
            risk_level = "LOW"
            action = "ALLOW"

        exec_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return TrustScoreResponse(
            trust_score=trust_score,
            risk_score=composite_risk,
            risk_level=risk_level,
            recommended_action=action,
            signals=signals,
            email_intelligence=email_intel,
            phone_intelligence=phone_intel,
            execution_time_ms=exec_ms
        )
