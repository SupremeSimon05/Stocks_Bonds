from redmail import EmailSender
from datetime import datetime as dt
import imaplib, email

def log_data(data):
    try:
        with open("log.txt", "a") as f:
            f.write(data)
    except:
        with open("log.txt", "w") as f:
            f.write(data)

def send_update(message, times_for_email):
    if(times_for_email>=30):
        try:
            email = EmailSender(
                host='smtp-mail.outlook.com',  # Update host
                port=587,                      # Update port
                username='stock_market_scheme@outlook.com',
                password='P@55W0rd!!'
            )
            email.send(
                subject="No Subject",
                sender="stock_market_scheme@outlook.com",
                receivers=['6037314818@txt.att.net'],
                text=message,
                html="<p>"+message+"</p>"
            )
            return 0
        except Exception as e:
            print("Emailing failed because "+str(e)+". Skipping update")
            log_data("Emailing failed because "+str(e)+" at "+dt.now()+". Update skipped")
            return times_for_email+1
    else:
        return times_for_email+1

def get_text(part):
    if part.is_multipart():
        return ''.join([get_text(subpart) for subpart in part.get_payload()])
    elif part.get_content_type() == 'text/plain':
        return part.get_payload()
    else:
        return ''  # Return an empty string for non-text content types

def readLatest():
    try:
        mail = imaplib.IMAP4_SSL('imap-mail.outlook.com')
        mail.login('stock_market_scheme@outlook.com', 'P@55W0rd!!')
        mail.select('inbox')
        _, data = mail.search(None, 'ALL')
        _, email_data = mail.fetch(data[0].split()[-1], '(RFC822)')
        msg = email.message_from_bytes(email_data[0][1])
        mail.close()
        mail.logout()
        return get_text(msg).split("\n")[0]
    except Exception as e:
        #This kinda a dangerous line, but I'm greedy so I want monies quick
        print("Remote failed because "+str(e)+". Skipping control") 
        log_data("Remote failed because "+str(e)+" at "+dt.now()+". Control skipped")
        return "Remote Failed"

