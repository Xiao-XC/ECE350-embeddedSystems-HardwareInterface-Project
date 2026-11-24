import smtplib
from email.message import EmailMessage

email_user = "mvidiacode@gmail.com"
email_password = "nryx lxdy mjdh fget"
email_send = "mvidiacode@gmail.com" 

subject = "subject" 
body = "body" 

msg = EmailMessage()
msg["From"] = email_user
msg["To"] = email_send
msg["Subject"] = subject
msg.set_content(body)

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(email_user, email_password)
    server.send_message(msg)

print("Email sent!")
