import os
import requests
import jinja2
from dotenv import load_dotenv

load_dotenv()

DOMAIN = os.getenv("MAILGUN_DOMAIN")

template_loader = jinja2.FileSystemLoader("templates")
template_env = jinja2.Environment(loader=template_loader)


def render_template(template_filename, **context):
    return template_env.get_template(template_filename).render(**context)

def send_simple_message(receiver, subject, body, html):
    api_key = os.getenv("MAILGUN_API_KEY")

    return requests.post(
  		"https://api.mailgun.net/v3/sandbox4d193923a5af433aa1eb9e2ff0fba2f3.mailgun.org/messages",
  		auth=("api", api_key),
  		data={
            "from": "FLASK API <mailgun@sandbox4d193923a5af433aa1eb9e2ff0fba2f3.mailgun.org>",
            "to": [receiver],
            "subject": subject,
            "text": body,
            "html": html
        }
    )

def send_user_registration_email(email, username):
    return send_simple_message(
        email,
        "Successfully signed up",
        f"Hi {username}! You have successfully signed up to the Stores REST API.",
        render_template("emails/registration.html", username=username)
    )