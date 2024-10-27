welcome_content = """
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .email-container {
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .email-header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #dddddd;
        }
        .email-header h1 {
            margin: 0;
            color: #333333;
        }
        .email-body {
            padding: 20px;
            text-align: left;
            color: #333333;
            line-height: 1.5;
        }
        .email-footer {
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #dddddd;
            color: #777777;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>Hoş Geldiniz!</h1>
        </div>
        <div class="email-body">
            <p>Merhaba,</p>
            <p>Web sitemize kayıt olduğunuz için teşekkür ederiz. Sizi aramızda görmekten mutluluk duyuyoruz.</p>
            <p>Teşekkürler,<br>10.11.4.10</p>
        </div>
        <div class="email-footer">
            <p>&copy; 2024 Web Siteniz. Tüm hakları saklıdır.</p>
        </div>
    </div>
</body>
</html>
"""

resetpass_content = """
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .email-container {
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .email-header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #dddddd;
        }
        .email-header h1 {
            margin: 0;
            color: #333333;
        }
        .email-body {
            padding: 20px;
            text-align: left;
            color: #333333;
            line-height: 1.5;
        }
        .email-footer {
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #dddddd;
            color: #777777;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>Şifre Sıfırlama Maili</h1>
        </div>
        <div class="email-body">
            <p>Merhabalar,</p>
            <p>Doğrulama şifreniz mail konusundadır. Doğrulama şifrenizi girerek hesap şifrenizi değiştirebilirsiniz.</p>
            <p>Teşekkürler,<br>10.11.4.10</p>
        </div>
        <div class="email-footer">
            <p>&copy; 2024 Web Siteniz. Tüm hakları saklıdır.</p>
        </div>
    </div>
</body>
</html>
"""

import base64
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def qr_code_mailf(path_to_qr, recipient_email, qr_code_url):
    if not os.path.exists(path_to_qr):
        raise FileNotFoundError(f"QR kodu dosyası bulunamadı: {path_to_qr}")
    
    msg = MIMEMultipart('related')
    msg['Subject'] = '2FA Doğrulama, QR ve QR url'
    msg['From'] = 'beyildir42@gmail.com'
    msg['To'] = recipient_email

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                padding-bottom: 20px;
                border-bottom: 1px solid #dddddd;
            }}
            .email-header h1 {{
                margin: 0;
                color: #333333;
            }}
            .email-body {{
                padding: 20px;
                text-align: left;
                color: #333333;
                line-height: 1.5;
            }}
            .email-body img {{
                display: block;
                margin: 20px auto;
                max-width: 150px;
                height: auto;
            }}
            .email-footer {{
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid #dddddd;
                color: #777777;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>QR ve QR url</h1>
            </div>
            <div class="email-body">
                <p>Merhabalar,</p>
                <p>2FA (İki Faktörlü Kimlik Doğrulama) özelliğini aktif ettiğiniz ve hesabınıza girişinizde 2FA kodu isteyecektir, aşağıdaki QR kodunu kullanarak kimlik doğrulama uygulamanıza ekleyebilirsiniz.</p>
                
                <img src="cid:qrcode">
                <p>{qr_code_url}</p>
                <p>Teşekkürler,<br>10.11.4.10</p>
            </div>
            <div class="email-footer">
                <p>&copy; 2024 Web Siteniz. Tüm hakları saklıdır.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # HTML kısmını ekle
    msg.attach(MIMEText(html, 'html'))

    # QR kodu resmini ekle
    with open(path_to_qr, 'rb') as img_file:
        img_data = img_file.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<qrcode>')
        image.add_header('Content-Disposition', 'inline', filename=os.path.basename(path_to_qr))
        msg.attach(image)

    # SMTP sunucusu üzerinden e-postayı gönder
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('beyildir42@gmail.com', 'fxyg milk xjho fauq')
        server.send_message(msg)

    print(f"E-posta {recipient_email} adresine başarıyla gönderildi.")