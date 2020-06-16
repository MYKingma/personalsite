from application import app
from flask_mail import Mail, Message
mail = Mail(app)

app.app_context().push()

def send_mail(msg):
    mail.send(msg)
