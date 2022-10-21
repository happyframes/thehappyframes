from .models import UserDetails
import requests
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()


def send_otp(email):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret, digits=4, interval=600)
    otp = totp.now()
    if otp.startswith('0'):
        otp = otp.replace("0", "1", 1)
    sub = "The Happy Frames loginApp passcode."
    msg = f"Thank you for signing up with The Happy frames. {otp} is the OTP for your loginApp. This OTP will expire" \
          f" within 10 min.\n\nThank you, \nThe Happy frames"
    user_ob = UserDetails.objects.get(email=email)
    user_ob.otp = otp
    user_ob.save()
    # send_mail(sub, msg, settings.EMAIL_HOST_USER, [email])
    return requests.post(
        "https://api.mailgun.net/v3/thehappyframes.com/messages",
        auth=("api", os.getenv("mg_api_key")),
        data={"from": "The Happy Frames <hi@thehappyframes.com>",
              "to": [email],
              "bcc": os.getenv("mg_bcc_email"),
              "subject": sub,
              "text": msg})


def send_order_status_email(email, sub, msg):
    return requests.post(
        "https://api.mailgun.net/v3/thehappyframes.com/messages",
        auth=("api", os.getenv("mg_api_key")),
        data={"from": "The Happy Frames <hi@thehappyframes.com>",
              "to": [email],
              "bcc": os.getenv("mg_bcc_email"),
              "subject": sub,
              "text": msg})
