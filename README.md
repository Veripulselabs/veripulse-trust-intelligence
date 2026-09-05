<div align="center">

<img src="assets/veripulse_logo.png" alt="VeriPulse Labs Logo" width="620" />

<br />

# ⚡ VeriPulse Trust Intelligence API
### Unified Dual-Engine B2B Signup Fraud Defense & Bot Blocker

[![RapidAPI](https://img.shields.io/badge/RapidAPI-Marketplace%20Live-0052CC?style=for-the-badge&logo=rapidapi)](https://rapidapi.com/jasdebarreau3/api/veripulse-trust-intelligence-api)
[![Latency](https://img.shields.io/badge/Latency-%3C50ms-brightgreen?style=for-the-badge)](https://rapidapi.com/jasdebarreau3/api/veripulse-trust-intelligence-api)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br />

**Stop managing separate vendors for email verification and SMS fraud detection. In a single HTTP roundtrip (<50ms), VeriPulse correlates email deliverability, disposable inbox blacklists, and telecom VoIP carrier intelligence into a definitive 0–100 Trust Score.**

[Get Free API Key on RapidAPI](https://rapidapi.com/jasdebarreau3/api/veripulse-trust-intelligence-api) • [API Documentation](https://rapidapi.com/jasdebarreau3/api/veripulse-trust-intelligence-api/details) • [Official Website](https://veripulselabs.com)

</div>

---

## 🎯 What is VeriPulse Trust Intelligence?

Modern fraud attacks are multi-vector. Attackers generate throwaway email addresses (Mailinator, TempMail) paired with virtual VoIP burner numbers (Google Voice, Twilio, TextNow) to bypass standard sign-up verification, burn free trial credits, and abuse SaaS onboarding.

**VeriPulse Trust Intelligence** is an enterprise-grade composite scoring engine. Instead of evaluating email and phone numbers in isolated silos, it correlates risk signals simultaneously to deliver a unified **0–100 Trust Score** and clear, deterministic policy decisions (`ALLOW`, `FLAG_FOR_REVIEW`, `BLOCK`).

### 🛡️ Core Capabilities

- **📬 Dual-Engine Cross-Correlation:** Synthesizes email syntax, DNS MX deliverability, and carrier line-type intelligence in parallel.
- **🚫 Dual Disposable Filter:** Flags 50,000+ burner email domains and 15+ major virtual telecom providers in under 50ms.
- **📡 Telecom Carrier Resolution:** Identifies line type (`MOBILE`, `FIXED_LINE`, `VOIP`), network carrier, and E.164 normalization across 240+ countries.
- **🎯 0–100 Composite Trust Score:** Deterministic scoring with automated policy actions (`ALLOW`, `FLAG_FOR_REVIEW`, `BLOCK`).
- **⚡ Sub-50ms Global Latency:** Built with non-blocking asynchronous Python, in-memory domain sets, and 24/7 keepalive warming.

---

## 🚀 Quickstart (Under 60 Seconds)

### 1. Get your API Key
Subscribe to the **Free Basic Tier** (1,000 free requests/month) on [RapidAPI](https://rapidapi.com/jasdebarreau3/api/veripulse-trust-intelligence-api).

### 2. Make your first request

#### Python (`requests`)
```python
import requests

url = "https://veripulse-trust-intelligence-api.p.rapidapi.com/v1/trust-score"

payload = {
    "email": "jane.doe@company.com",
    "phone": "+14155552671",
    "country_code": "US"
}

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
    "X-RapidAPI-Host": "veripulse-trust-intelligence-api.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

#### Node.js / JavaScript (`fetch`)
```javascript
const url = 'https://veripulse-trust-intelligence-api.p.rapidapi.com/v1/trust-score';
const options = {
    method: 'POST',
    headers: {
        'content-type': 'application/json',
        'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY',
        'X-RapidAPI-Host': 'veripulse-trust-intelligence-api.p.rapidapi.com'
    },
    body: JSON.stringify({
        email: 'jane.doe@company.com',
        phone: '+14155552671',
        country_code: 'US'
    })
};

const response = await fetch(url, options);
const data = await response.json();
console.log(data);
```

#### cURL
```bash
curl -X POST "https://veripulse-trust-intelligence-api.p.rapidapi.com/v1/trust-score" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "X-RapidAPI-Host: veripulse-trust-intelligence-api.p.rapidapi.com" \
  -d '{
    "email": "jane.doe@company.com",
    "phone": "+14155552671",
    "country_code": "US"
  }'
```

---

## 📦 Sample API Responses

### Low Risk / Legitimate Business Registration
```json
{
  "trust_score": 95,
  "risk_score": 5,
  "risk_level": "LOW",
  "recommended_action": "ALLOW",
  "signals": [
    "Email: Active DNS MX records verified",
    "Phone: Valid mobile subscriber line (Verizon Wireless) - optimal for SMS delivery"
  ],
  "email_intelligence": {
    "email": "jane.doe@company.com",
    "is_valid": true,
    "is_disposable": false,
    "is_role_account": false,
    "is_free_provider": false,
    "has_mx_records": true,
    "did_you_mean": null,
    "domain": "company.com",
    "risk_score": 0,
    "signals": ["Active DNS MX records verified"]
  },
  "phone_intelligence": {
    "phone_input": "+14155552671",
    "is_valid": true,
    "country_code": "US",
    "e164_format": "+14155552671",
    "international_format": "+1 415-555-2671",
    "national_format": "(415) 555-2671",
    "carrier": {
      "name": "Verizon Wireless",
      "line_type": "MOBILE",
      "is_virtual": false
    },
    "risk_score": 0,
    "signals": ["Valid mobile subscriber line (Verizon Wireless) - optimal for SMS delivery"]
  },
  "execution_time_ms": 32.4
}
```

### High Risk / Coordinated Bot Signup Attack
```json
{
  "trust_score": 2,
  "risk_score": 98,
  "risk_level": "HIGH",
  "recommended_action": "BLOCK",
  "signals": [
    "CRITICAL: Both email and phone belong to disposable/virtual services (bot farm signature)",
    "Email: Known disposable / temporary email domain (mailinator.com)",
    "Phone: Virtual / VoIP provider detected (Google Voice) - high fraud risk for SMS OTP"
  ],
  "email_intelligence": {
    "email": "burner99@mailinator.com",
    "is_valid": true,
    "is_disposable": true,
    "risk_score": 90
  },
  "phone_intelligence": {
    "phone_input": "+12025550143",
    "is_valid": true,
    "carrier": {
      "name": "Google Voice",
      "line_type": "VOIP",
      "is_virtual": true
    },
    "risk_score": 85
  },
  "execution_time_ms": 18.2
}
```

---

## ⚙️ Decision Matrix & Policy Rules

| Trust Score | Composite Risk | Risk Level | Policy Action | Typical Scenario |
| :---: | :---: | :---: | :---: | :--- |
| **80 – 100** | 0 – 20 | `LOW` | `ALLOW` | Legitimate corporate or personal email + verified mobile carrier. |
| **30 – 79** | 21 – 70 | `MEDIUM` | `FLAG_FOR_REVIEW` | Landline phone, generic role inbox (`support@`), or minor domain typo. |
| **0 – 29** | 71 – 100 | `HIGH` | `BLOCK` | Disposable burner domain, virtual VoIP range, or malformed credentials. |

---

## 🏢 VeriPulse Labs Product Ecosystem

| Service | Focus Area | GitHub Repository | RapidAPI Listing |
| :--- | :--- | :--- | :--- |
| **VeriPulse Email** | In-depth MX, disposable, and mailbox fraud screening | [VeriPulse GitHub](https://github.com/Veripulselabs/veripulse) | [RapidAPI Storefront](https://rapidapi.com/jasdebarreau3/api/veripulse-email-verification-and-fraud-detection) |
| **NumGuard Phone** | Telecom carrier lookup & VoIP virtual line detection | [NumGuard GitHub](https://github.com/Veripulselabs/numguard) | [RapidAPI Storefront](https://rapidapi.com/jasdebarreau3/api/numguard-phone-voip-fraud-detection) |
| **Trust Intelligence** | Flagship dual-engine signup fraud defense | [Trust Intelligence GitHub](https://github.com/Veripulselabs/veripulse-trust-intelligence) | [RapidAPI Storefront](https://rapidapi.com/jasdebarreau3/api/veripulse-trust-intelligence-api) |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
Built with precision by <strong>VeriPulse Labs</strong> • <a href="https://veripulselabs.com">veripulselabs.com</a>
</div>
