from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

SENDER = ''
SENDER_PASSWORD = ''

def send_email(recipient, file_name, file_content):
        msg = MIMEMultipart()
        msg['From'] = SENDER
        msg['To'] = recipient
        msg['Subject'] = 'Elevation service'
        message = 'Generated file'
        msg.attach(MIMEText(message))
        part = MIMEApplication(file_content)
        part['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        msg.attach(part)

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        print(server.set_debuglevel(1))

        try:
                server.login(SENDER, SENDER_PASSWORD)
                server.sendmail(msg['From'], msg['To']  , msg.as_string())
                server.close()
                print ('Email sent')
        except:
                server.set_debuglevel(1)
                print ("Email sending failed")
