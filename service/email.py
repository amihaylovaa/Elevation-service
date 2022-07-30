from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

SENDER = ''
SENDER_PASSWORD = ''

def send_gpx_to_email(recipient, file_name, file_content):
        msg = MIMEMultipart()
        part = MIMEApplication(file_content)
        msg['From'] = SENDER
        msg['To'] = recipient
        msg['Subject'] = 'Elevation service'
        message = 'Generated file'
        part['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        msg.attach(MIMEText(message))
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

def send_error_email(recipient, reason):
        msg = MIMEMultipart()
        msg['From'] = SENDER
        msg['To'] = recipient
        msg['Subject'] = 'Elevation service'
        msg.attach(MIMEText(reason))

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
