'''
@Author: Dysin
@Date:   2026/3/17
@Desc:   发送文件至E-Mail
'''

import smtplib
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email_with_attachment(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    receiver_email: str,
    subject: str,
    body: str,
    attachment_path: str
):
    # 1. 创建带附件的邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # 邮件正文
    msg.attach(MIMEText(body, 'plain'))

    # 2. 添加附件
    if attachment_path and os.path.isfile(attachment_path):
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(attachment_path, 'rb') as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(attachment_path)
        part.add_header(
            'Content-Disposition',
            'attachment',
            filename=('utf-8', '', filename)
        )
        msg.attach(part)

    # 3. 发送邮件
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # TLS 加密
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print(f"✅ 邮件已发送到 {receiver_email}")
    except Exception as e:
        print(f"❌ 发送失败: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    send_email_with_attachment(
        smtp_server='smtp.gmail.com',  # 例如 Gmail SMTP
        smtp_port=587,
        sender_email='dysinqiu@gmail.com',
        sender_password='prso tdbd mvwi kvdh',  # Gmail 需开启 “应用专用密码”
        receiver_email='dysinqiu@163.com',
        subject='测试邮件',
        body='这是测试邮件正文',
        attachment_path=r'F:\2_Special\active\investment_system\reports\quantitative_trading_20260316\20260316_量化交易分析报告.pdf'
    )