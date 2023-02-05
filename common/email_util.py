import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging

from .config import MAIL_HOST,MAIL_USER,MAIL_PASS,SENDER,RECEIVERS,MAIL_PORT

logger = logging.getLogger("recallApp.common")
 
class EmailUtil(object):

    smtpObj = smtplib.SMTP() 
    smtpObj.connect(MAIL_HOST, MAIL_PORT)    # 25 为 SMTP 端口号
    smtpObj.login(MAIL_USER,MAIL_PASS) 
    

    def __init__(self,message,from_name,to_name,subject) -> None:
        self.message = MIMEText(message, 'plain', 'utf-8')
        self.message['From'] = Header(from_name, 'utf-8')
        self.message['To'] =  Header(to_name, 'utf-8')
        self.message['Subject'] = Header(subject, 'utf-8')


    def send_email(self) -> None:
        try:
            self.smtpObj.sendmail(SENDER, RECEIVERS, self.message.as_string())
            logger.info("Success: email send ") 
        except Exception as e:
            logger.error(e)
            logger.error("Error: cannot send email") 

 
if __name__ == "__main__":
    EmailUtil("test","aminer","**","主体").send_email()

 

 
 
