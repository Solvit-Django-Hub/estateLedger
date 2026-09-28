from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def send_activation_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_url = request.build_absolute_uri(
        reverse(
            "account-activate",
            kwargs={
                "uidb64": uid,
                "token": token,
            },
        )
    )

    # Clean URL for development/testing


    subject = "Activate your EstateLedger account"

    message = (
        "Hello,\n\n"
        "Please activate your account using the link below above"

        "EstateLedger,"
    )

    print("\n" + "=" * 80)
    print("ACCOUNT ACTIVATION LINK")
    print(activation_url)
    print("=" * 80 + "\n")

    send_mail(
        subject,
        message,
        None,
        [user.email],
    )
    return activation_url