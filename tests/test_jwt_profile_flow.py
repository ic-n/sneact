"""
End-to-end-ish test of a profile page built with sneact.modern:

1. GET /profile with no jwt cookie       -> registration form renders
2. POST /profile with form data          -> jwt is minted, page meta-refreshes
3. (the meta refresh is the "page refreshes" step, browser-side)
4. GET /profile with the jwt cookie      -> decoded claims render as profile
   GET /profile with a tampered jwt      -> error asking to resubmit the form

There's no JWT library in this project's dependencies, so step 2/4 use a
minimal stdlib-only HS256 codec -- good enough to prove the round trip.
"""

import base64
import hashlib
import hmac
import json

from sneact.modern import component, render, tag, text

SECRET = "super-secret-signing-key"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def encode_jwt(claims: dict, secret: str) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(json.dumps(claims).encode())
    signing_input = f"{header}.{payload}".encode()
    signature = _b64url_encode(
        hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{signature}"


def decode_jwt(token: str, secret: str) -> dict:
    try:
        header, payload, signature = token.split(".")
    except ValueError:
        raise ValueError("malformed jwt") from None

    expected_signature = _b64url_encode(
        hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("bad jwt signature")

    return json.loads(_b64url_decode(payload))


def hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


@component
def field_input(name: str, label: str, type_: str = "text"):
    with tag.div(class_="mb-4"):
        with tag.label(class_="mb-1 block text-sm font-medium text-slate-700", for_=name):
            text(label)
        tag.input(
            id=name,
            name=name,
            type=type_,
            class_="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
            "shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500",
        )


@component
def registration_form(error: str | None = None):
    with tag.div(class_="flex min-h-screen items-center justify-center bg-slate-100"):
        with tag.form(method="post", action="/profile",
                       class_="w-full max-w-sm rounded-2xl bg-white p-8 shadow-xl"):
            with tag.h1(class_="mb-6 text-2xl font-bold text-slate-900"):
                text("Create your profile")

            if error:
                with tag.div(class_="mb-4 rounded-lg border border-red-200 bg-red-50 "
                              "px-4 py-3 text-sm text-red-700"):
                    text(error)

            field_input("first_name", "First name")
            field_input("last_name", "Last name")
            field_input("email", "Email", type_="email")
            field_input("password", "Password", type_="password")

            with tag.button(type="submit",
                             class_="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm "
                             "font-semibold text-white shadow-sm hover:bg-indigo-500"):
                text("Sign up")


@component
def profile_field(label: str, value: str):
    with tag.div(class_="flex justify-between border-b border-slate-100 py-2 last:border-0"):
        with tag.span(class_="text-sm text-slate-500"):
            text(label)
        with tag.span(class_="text-sm font-medium text-slate-900"):
            text(value)


@component
def profile_card(claims: dict):
    with tag.div(class_="flex min-h-screen items-center justify-center bg-slate-100"):
        with tag.div(class_="w-full max-w-sm space-y-1 rounded-2xl bg-white p-8 shadow-xl"):
            with tag.h1(class_="mb-4 text-2xl font-bold text-slate-900"):
                text(f"{claims['first_name']} {claims['last_name']}")
            profile_field("Email", claims["email"])
            profile_field("Password hash", claims["password_hash"])
            profile_field("Issued at", str(claims["iat"]))


@component
def saving_redirect(redirect_url: str):
    with tag.html:
        with tag.head:
            tag.meta(http_equiv="refresh", content=f"0; url={redirect_url}")
        with tag.body(class_="flex min-h-screen items-center justify-center bg-slate-100"):
            with tag.p(class_="text-sm text-slate-500"):
                text("Saving your profile...")


def handle_profile_request(cookie_jwt: str | None = None, form: dict | None = None):
    """Returns (html, set_cookie_jwt_or_none), mimicking a tiny request handler."""
    if form is not None:
        claims = {**form, "iat": 1700000000}
        token = encode_jwt(claims, SECRET)
        return render(saving_redirect("/profile")), token

    if cookie_jwt is not None:
        try:
            claims = decode_jwt(cookie_jwt, SECRET)
        except ValueError:
            error = "Your session is invalid or expired. Please resubmit the form below."
            return render(registration_form(error=error)), None
        return render(profile_card(claims)), None

    return render(registration_form()), None


def test_full_jwt_profile_flow():
    html, set_cookie = handle_profile_request()
    assert set_cookie is None
    assert '<form method="post" action="/profile"' in html
    assert "Create your profile" in html
    assert 'name="password"' in html and 'type="password"' in html

    form_data = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "password_hash": hash_password("s3cr3t"),
    }
    html, jwt_token = handle_profile_request(form=form_data)
    assert jwt_token is not None and jwt_token.count(".") == 2
    assert '<meta http-equiv="refresh" content="0; url=/profile">' in html
    assert "Saving your profile..." in html

    html, set_cookie = handle_profile_request(cookie_jwt=jwt_token)
    assert set_cookie is None
    assert "Ada Lovelace" in html
    assert "ada@example.com" in html
    assert hash_password("s3cr3t") in html
    assert "1700000000" in html
    assert "<form" not in html

    html, _ = handle_profile_request(cookie_jwt=jwt_token + "tampered")
    assert "resubmit the form" in html.lower()
    assert '<form method="post" action="/profile"' in html
