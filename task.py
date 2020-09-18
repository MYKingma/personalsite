from application import app, app_tree
from flask_mail import Mail, Message
mail = Mail(app)


app.app_context().push()

def send_mail(msg):
    mail.send(msg)

def send_mail_tree(msg):
    mail_tree = Mail(app_tree)
    mail_tree.send(msg)
