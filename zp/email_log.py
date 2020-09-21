import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender = '1009137312@qq.com'
receivers = ['fanzhijun@ibeifeng.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

mail_host = "smtp.qq.com"  # 设置服务器
mail_user = "1009137312"  # 用户名
mail_pass = "FanTan879425"  # 口令

# 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
message = MIMEMultipart()
message['From'] = Header("服务器", 'utf-8')
message['To'] = Header("子沐", 'utf-8')
subject = '爬虫Zp Log日志'
message['Subject'] = Header(subject, 'utf-8')
data_log = open('zhaopin.log', 'r').read()
message.attach(MIMEText('爬虫Zp Log日志请见附件\n\r' + data_log, 'plain', 'utf-8'))
att1 = MIMEText(open('zhaopin.log', 'rb').read(), 'base64', 'utf-8')
att1["Content-Type"] = 'application/octet-stream'
# 这里的filename可以任意写，写什么名字，邮件中显示什么名字
att1["Content-Disposition"] = 'attachment; filename="zhaopin.log"'
message.attach(att1)

try:
    smtpObj = smtplib.SMTP_SSL(mail_host, 465)
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    smtpObj.close()
    data_log = open('zhaopin.log', 'w').write('')
    print("邮件发送成功")
except smtplib.SMTPException:
    print("Error: 无法发送邮件")
