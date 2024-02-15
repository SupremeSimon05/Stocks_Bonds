from redmail import EmailSender
from datetime import datetime as dt
import imaplib, email

def send_update(message):
    email = EmailSender(
        host='smtp-mail.outlook.com',  # Update host
        port=587,                      # Update port
        username='stock_market_scheme@outlook.com',
        password='P@55W0rd!!'
    )
    email.send(
        subject="",
        sender="stock_market_scheme@outlook.com",
        receivers=['6037314818@txt.att.net'],
        text=message,
        html="<p>"+message+"</p>"
    )

def get_text(part):
    if part.is_multipart():
        return ''.join([get_text(subpart) for subpart in part.get_payload()])
    elif part.get_content_type() == 'text/plain':
        return part.get_payload()
    else:
        return ''  # Return an empty string for non-text content types

def readLatest():
    username, password = 'stock_market_scheme@outlook.com', 'P@55W0rd!!'
    mail = imaplib.IMAP4_SSL('imap-mail.outlook.com')
    mail.login(username, password)
    mail.select('inbox')
    _, data = mail.search(None, 'ALL')
    _, email_data = mail.fetch(data[0].split()[-1], '(RFC822)')
    msg = email.message_from_bytes(email_data[0][1])

    print("Subject:", msg['Subject'])
    print("Body:", get_text(msg))
    mail.close()
    mail.logout()