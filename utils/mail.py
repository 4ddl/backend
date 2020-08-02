from django.core.mail import EmailMultiAlternatives


def send_activated_email(username, to_email, activate_code):
    subject = f'[DDL]确认电子邮件地址，验证码是：[{activate_code}]'
    text_content = f"""
欢迎 {username} ：

感谢您注册DDL
您的账号激活码是：{activate_code}
"""
    html_content = f"""
<div>
<p>欢迎 {username} ：</p>
<br/>
<p>感谢您注册DDL</p>
<p>您的账号激活码是：<code>{activate_code}</code></p>
</div>
"""
    email_msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[to_email])
    email_msg.attach_alternative(html_content, "text/html")
    email_msg.send()
