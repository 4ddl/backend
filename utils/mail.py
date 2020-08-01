from django.core.mail import EmailMultiAlternatives


def send_email_check_mail(username, to_email, activate_url):
    subject = '[DDL]确认电子邮件地址'
    text_content = f"""
欢迎 {username} ：

感谢您注册DDL
请您将下面链接复制到浏览器以激活你的账号：
{activate_url}
"""
    html_content = f"""
<div>
<p>欢迎 {username} ：</p>
<br/>
<p>感谢您注册DDL</p>
<p>请您点击下面链接激活你的账号：</p>
<a href='{activate_url}' target='_blank'>{activate_url}</a>
</div>
    """
    email_msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[to_email])
    email_msg.attach_alternative(html_content, "text/html")
    email_msg.send()
