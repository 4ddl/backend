from celery import shared_task
from django.core.mail import EmailMultiAlternatives

from ddl.settings import ACTIVATE_CODE_AGE


@shared_task(name='send_activated_email')
def send_activated_email(to_email, activate_code):
    subject = f'[DDL]确认电子邮件地址，验证码是：[{activate_code}]'
    text_content = f"""

感谢您注册DDL
您的邮箱验证码是：{activate_code}
验证码有效期：{ACTIVATE_CODE_AGE // 60}分钟
"""
    html_content = f"""
<div>
<p>感谢您注册DDL</p>
<p>您的邮箱验证码是：<code>{activate_code}</code></p>
<p>验证码有效期：{ACTIVATE_CODE_AGE // 60}分钟</p>
</div>
"""
    email_msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[to_email])
    email_msg.attach_alternative(html_content, "text/html")
    email_msg.send()
