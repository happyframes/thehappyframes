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
    sub = "Happy Frames loginApp passcode."
    msg = f"Thank you for signing up with Happy frames. {otp} is the OTP for your loginApp. This OTP will expire within " \
          f"10 min.\n\nThank you, \nHappy frames"
    user_ob = UserDetails.objects.get(email=email)
    user_ob.otp = otp
    user_ob.save()
    # send_mail(sub, msg, settings.EMAIL_HOST_USER, [email])
    return requests.post(
        "https://api.mailgun.net/v3/thehappyframes.com/messages",
        auth=("api", os.getenv("mg_api_key")),
        data={"from": "Happy Frames <noreply@thehappyframes.com>",
              "to": [email],
              "bcc": os.getenv("mg_bcc_email"),
              "subject": sub,
              "text": msg})


def send_order_successful_email(email, order_id):
    sub = "Order Successful"
    msg = f"Thank you for shopping with Happy frames. Your order({order_id}) was successfully placed and we will " \
          f"deliver your order shortly.\n\nThank you, \nHappy frames"
    return requests.post(
        "https://api.mailgun.net/v3/thehappyframes.com/messages",
        auth=("api", os.getenv("mg_api_key")),
        data={"from": "Happy Frames <noreply@thehappyframes.com>",
              "to": [email],
              "bcc": os.getenv("mg_bcc_email"),
              "subject": sub,
              "text": msg})
