from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import os
import uvicorn

app = FastAPI()

LOCAL_BIN_FALLBACK = {
    "400001": {
        "bank": "INTL HDQTRS-CENTER OWNED",
        "brand": "TRADITIONAL / INFINITE",
        "country": "UNITED STATES",
        "country_code": "US",
        "type": "Kredi",
        "scheme": "visa",
        "segment": "consumer",
        "prepaid": "Hayır",
    },
    "540045": {
        "bank": "TÜRKİYE İŞ BANKASI A.Ş.",
        "brand": "WORLD / MAXIMUM",
        "country": "TÜRKİYE",
        "country_code": "TR",
        "type": "Kredi",
        "scheme": "mastercard",
        "segment": "consumer",
        "prepaid": "Hayır",
    },
    "555555": {
        "bank": "GARANTİ BBVA (TEST)",
        "brand": "WORLD ELITE / BONUS",
        "country": "TÜRKİYE",
        "country_code": "TR",
        "type": "Kredi",
        "scheme": "mastercard",
        "segment": "consumer",
        "prepaid": "Hayır",
    },
    "979200": {
        "bank": "ZİRAAT BANKASI (TEST)",
        "brand": "TROY PLATINUM",
        "country": "TÜRKİYE",
        "country_code": "TR",
        "type": "Kredi",
        "scheme": "troy",
        "segment": "consumer",
        "prepaid": "Hayır",
    },
    "979201": {
        "bank": "HALKBANK (TEST)",
        "brand": "TROY DEBIT",
        "country": "TÜRKİYE",
        "country_code": "TR",
        "type": "Banka (Debit)",
        "scheme": "troy",
        "segment": "consumer",
        "prepaid": "Hayır",
    },
}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workspace &gt; BIN Sorgu</title>
    <style>
        :root {
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-box: #f8fafc;
            --border-color: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --accent: #0d7377;
            --accent-hover: #095457;
            --pill-bg: #f1f5f9;
        }
        body.dark {
            --bg-body: #0f172a;
            --bg-card: #1e293b;
            --bg-box: #0f172a;
            --border-color: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #14b8a6;
            --accent-hover: #0d9488;
            --pill-bg: #334155;
        }
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body {
            background-color: var(--bg-body);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            transition: background 0.2s, color 0.2s;
        }
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 28px;
            border-bottom: 1px solid var(--border-color);
            background-color: var(--bg-card);
            font-size: 14px;
        }
        .breadcrumb { color: var(--text-muted); }
        .breadcrumb strong { color: var(--text-main); }
        .theme-btn {
            background: var(--bg-box);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
        }
        .container {
            max-width: 780px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .header-title { font-size: 24px; font-weight: 700; margin: 0 0 6px 0; }
        .header-sub { color: var(--text-muted); font-size: 14px; margin: 0 0 24px 0; }
        .panel {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }
        .panel-head {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-color);
        }
        .panel-head h3 { margin: 0 0 4px 0; font-size: 16px; display: flex; align-items: center; gap: 8px; }
        .panel-head p { margin: 0; font-size: 13px; color: var(--text-muted); }
        .panel-body { padding: 24px; }
        .search-row {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }
        .search-row input {
            width: 240px;
            padding: 11px 16px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            background: var(--bg-card);
            color: var(--text-main);
            font-size: 15px;
            letter-spacing: 1px;
        }
        .search-row input:focus { outline: none; border-color: var(--accent); }
        .search-row button {
            background-color: var(--accent);
            color: #fff;
            border: none;
            padding: 11px 20px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .search-row button:hover { background-color: var(--accent-hover); }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }
        @media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
        .info-box {
            border: 1px solid var(--border-color);
            background-color: var(--bg-box);
            border-radius: 12px;
            padding: 14px 18px;
        }
        .info-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
        .info-val { font-size: 15px; font-weight: 700; text-transform: uppercase; }
        .info-val.lower { text-transform: none; }
        .badges {
            margin-top: 20px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .badge {
            padding: 5px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            background-color: var(--pill-bg);
            color: var(--text-main);
        }
        .badge.accent {
            background-color: var(--accent);
            color: #ffffff;
        }
        .status-msg {
            margin-bottom: 16px;
            font-size: 13px;
            color: #ef4444;
            display: none;
        }
    </style>
</head>
<body>
    <div class="topbar">
        <div class="breadcrumb">Workspace &nbsp;&gt;&nbsp; <strong>BIN Sorgu</strong></div>
        <button class="theme-btn" onclick="document.body.classList.toggle('dark')">🌓 Tema Değiştir</button>
    </div>

    <div class="container">
        <h1 class="header-title">BIN Sorgu</h1>
        <p class="header-sub">6–8 haneli BIN ile banka / ülke / seviye bilgisi (Visa, Mastercard, Troy & TR destekli)</p>

        <div class="panel">
            <div class="panel-head">
                <h3>💳 BIN Sorgu</h3>
                <p>Sonuçlar kutularda gösterilir</p>
            </div>
            <div class="panel-body">
                <div class="search-row">
                    <input type="text" id="binInput" maxlength="8" placeholder="Örn: 540045" value="400001">
                    <button onclick="sorgula()">🔍 Sorgula</button>
                </div>

                <div id="statusMsg" class="status-msg"></div>

                <div class="grid">
                    <div class="info-box">
                        <div class="info-label">Banka</div>
                        <div class="info-val" id="resBank">-</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Seviye / Marka</div>
                        <div class="info-val" id="resBrand">-</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Ülke</div>
                        <div class="info-val" id="resCountry">-</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Ülke kodu</div>
                        <div class="info-val" id="resCountryCode">-</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Tür</div>
                        <div class="info-val lower" id="resType">-</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Şema</div>
                        <div class="info-val lower" id="resScheme">-</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Segment</div>
                        <div class="info-val lower" id="resSegment">-</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Prepaid</div>
                        <div class="info-val lower" id="resPrepaid">-</div>
                    </div>
                </div>

                <div class="badges" id="badgeRow"></div>
            </div>
        </div>
    </div>

    <script>
        async function sorgula() {
            const binVal = document.getElementById("binInput").value.trim();
            const statusMsg = document.getElementById("statusMsg");
            statusMsg.style.display = "none";

            if (binVal.length < 6) {
                statusMsg.innerText = "Lütfen en az 6 haneli bir BIN numarası girin.";
                statusMsg.style.display = "block";
                return;
            }

            try {
                const res = await fetch("/api/lookup", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ bin: binVal })
                });
                const data = await res.json();

                if (!data.found) {
                    statusMsg.innerText = data.message || "Bu BIN için kayıt bulunamadı.";
                    statusMsg.style.display = "block";
                    return;
                }

                const d = data.details;
                document.getElementById("resBank").innerText = d.bank;
                document.getElementById("resBrand").innerText = d.brand;
                document.getElementById("resCountry").innerText = d.country;
                document.getElementById("resCountryCode").innerText = d.country_code;
                document.getElementById("resType").innerText = d.type;
                document.getElementById("resScheme").innerText = d.scheme;
                document.getElementById("resSegment").innerText = d.segment;
                document.getElementById("resPrepaid").innerText = d.prepaid;

                document.getElementById("badgeRow").innerHTML = `
                    <span class="badge">${d.scheme.toUpperCase()}</span>
                    <span class="badge">${d.brand.toUpperCase()}</span>
                    <span class="badge accent">${d.type}</span>
                `;
            } catch (e) {
                statusMsg.innerText = "Sorgu sırasında bağlantı hatası oluştu.";
                statusMsg.style.display = "block";
            }
        }
        window.onload = sorgula;
    </script>
</body>
</html>
"""

class BinPayload(BaseModel):
    bin: str

def detect_scheme_offline(bin_str: str) -> str:
    if bin_str.startswith("4"):
        return "visa"
    if bin_str.startswith(("51", "52", "53", "54", "55")) or (2221 <= int(bin_str[:4]) <= 2720):
        return "mastercard"
    if bin_str.startswith("9792"):
        return "troy"
    if bin_str.startswith(("34", "37")):
        return "amex"
    return "bilinmiyor"

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PAGE

@app.post("/api/lookup")
def lookup_bin(payload: BinPayload):
    cleaned = "".join(ch for ch in payload.bin if ch.isdigit())[:8]
    if len(cleaned) < 6:
        return {"found": False, "message": "En az 6 rakam girmelisiniz."}

    prefix6 = cleaned[:6]

    try:
        resp = requests.get(
            f"https://lookup.binlist.net/{cleaned}",
            headers={"Accept-Version": "3", "User-Agent": "BinLookupPanel/1.0"},
            timeout=4,
        )
        if resp.status_code == 200:
            raw = resp.json()
            bank_name = (raw.get("bank") or {}).get("name") or "BİLİNMEYEN BANKA"
            brand = raw.get("brand") or "STANDARD"
            country_obj = raw.get("country") or {}
            country_name = country_obj.get("name") or "-"
            country_code = country_obj.get("alpha2") or "-"
            raw_type = (raw.get("type") or "").lower()
            card_type = "Kredi" if raw_type == "credit" else ("Banka (Debit)" if raw_type == "debit" else "Bilinmiyor")
            scheme = (raw.get("scheme") or detect_scheme_offline(cleaned)).lower()
            prepaid = "Evet" if raw.get("prepaid") is True else "Hayır"
            segment = "commercial" if "CORP" in brand.upper() or "BUSINESS" in brand.upper() else "consumer"

            return {
                "found": True,
                "details": {
                    "bank": bank_name,
                    "brand": brand,
                    "country": country_name,
                    "country_code": country_code,
                    "type": card_type,
                    "scheme": scheme,
                    "segment": segment,
                    "prepaid": prepaid,
                },
            }
    except Exception:
        pass

    if prefix6 in LOCAL_BIN_FALLBACK:
        return {"found": True, "details": LOCAL_BIN_FALLBACK[prefix6]}

    detected = detect_scheme_offline(cleaned)
    if detected != "bilinmiyor":
        return {
            "found": True,
            "details": {
                "bank": "KAYIT BULUNAMADI (YEREL TEST)",
                "brand": "STANDARD",
                "country": "TÜRKİYE" if detected == "troy" else "-",
                "country_code": "TR" if detected == "troy" else "-",
                "type": "Kredi",
                "scheme": detected,
                "segment": "consumer",
                "prepaid": "Hayır",
            },
        }

    return {"found": False, "message": "Bu BIN numarası için kayıt bulunamadı."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
