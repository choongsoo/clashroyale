import smtplib
import ssl
from os.path import dirname


# A collection of globally-shared helper functions


def email_admin(status_code, message):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "tom.zhang.dev@gmail.com"
    receiver_email = "tom.zhang.dev@gmail.com"
    pass_file = open(
        '{}/credentials/dev-gmail-pass.txt'.format(dirname(__file__)))
    password = pass_file.readline()
    pass_file.close()

    msg_template = """Subject: {}

    {}"""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email,
                        msg_template.format(status_code, message))
