import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "pb.sledge.94@gmail.com"  # Enter your address
receiver_email = "pb.sledge.94@gmail.com"  # Enter receiver address
password = '42Ez8MrK6Ycc'
message = """\
Subject: Hi there

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)