import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):#ho whom we are sending the mail
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('mounikamurikipudi333@gmail.com','wrsxlmvkddoazzmj')
    msg=EmailMessage()
    msg['From']='mounikamurikipudi333@gmail.com'
    msg['Subject']=subject
    msg['To']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit()



