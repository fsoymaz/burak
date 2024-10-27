from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError, NotFound
from .serializers import UserSerializer
from django.http import JsonResponse
from django.http import HttpResponse
import jwt, datetime
from .models import User, Friend
import qrcode, pyotp, string, random, requests, json
from django.core.files import File
from django.http import JsonResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from .mail_content import welcome_content, resetpass_content, qr_code_mailf
import os.path
from os import path
import pyotp
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from io import BytesIO
from django.db.models import Q
from rest_framework import status

class Uploadpp(APIView):
    def post(self, request):
        username = request.data.get('username')
        is_uploadpp = request.data.get('is_uploadpp')
        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        if is_uploadpp == False:
            user.is_uploadpp = True
            user.save()
        else:
            user.is_uploadpp = False
            user.save()
        payload = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
			'username': user.username,
            'twofactoractive': user.twofactoractive,
            'is_uploadpp': user.is_uploadpp,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
            }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=False)
        response.data = {
            'token': token,
        }
        return response

class UpdateUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        flag = request.data.get('flag')
        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        if(flag == 1):
            password = request.data.get('password')
            user.set_password(str(password))
            user.save()
            return Response({'OK'}, status=200)
        elif(flag == 2):
            totp = pyotp.TOTP(user.twofactorkey)
            user.resetpass = totp.now()
            user.save()
            try:
                smtp_server = "smtp.gmail.com"
                smtp_port = 587

                msg = MIMEMultipart('alternative')
                msg['From'] = "beyildir42@gmail.com"
                msg['To'] = user.email
                msg['Subject'] = totp.now()

                part = MIMEText(resetpass_content, 'html')
                msg.attach(part)

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login("beyildir42@gmail.com", "fxyg milk xjho fauq")
                server.sendmail("beyildir42@gmail.com", user.email, msg.as_string())
                server.quit()
            
                print("E-posta başarıyla gönderildi.")
                return Response({'OK'}, status=200)
            except Exception as e:
                return Response({'error': 'Mail gönderilemedi.'}, status=400)
        elif (flag == 3):
            usname = request.data.get('name')
            user.name = usname
            user.save()

            payload = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
			'username': user.username,
            'twofactoractive': user.twofactoractive,
            'is_uploadpp': user.is_uploadpp,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
            }

            token = jwt.encode(payload, 'secret', algorithm='HS256')
            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=False)
            response.data = {
                'token': token,
            }
            return response
            
        else:
            otp = request.data.get('otpInput')
            if user.resetpass == str(otp):
                password = request.data.get('password')
                user.set_password(str(password))
                user.save()
                return Response({'OK'}, status=200)
            else:
                return Response({'error': 'Invalid TOTP code'}, status=400)
        return Response({'OK'}, status=200)
    

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            try:
                smtp_server = "smtp.gmail.com"
                smtp_port = 587

                msg = MIMEMultipart('alternative')
                msg['From'] = "ardatan383@gmail.com"
                msg['To'] = user.email
                msg['Subject'] = "Web Sitemize Hoş Geldiniz!"

                part = MIMEText(welcome_content, 'html')
                msg.attach(part)

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login("ardatan383@gmail.com", "embj boip vamy xdym")
                server.sendmail("ardatan383@gmail.com", user.email, msg.as_string())
                server.quit()
            
                print("E-posta başarıyla gönderildi.")
            except Exception as e:
                print(f"E-posta gönderilemedi: {e}")
            return Response({'message': 'User created successfully'}, status=201)
        return Response(serializer.errors, status=400)

class TwoFactorActive(APIView):
    def post(self, request):
        username = request.data.get('username')
        _bool = request.data.get('twofactoractive')

        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        if(bool(_bool) == 1):
            # if(path.exists("/qrdata/" + user.username + ".png")):
            #     user.twofactoractive = bool(_bool)
            #     user.save()
            # else:
            user.twofactoractive = bool(_bool)
            totps = pyotp.TOTP(user.twofactorkey)
            print(totps.now())


            uri = pyotp.totp.TOTP(user.twofactorkey).provisioning_uri(name=user.username, issuer_name="2FA Transcendence")
            user.qrcode_url = uri
            user.save()
            qr_image = qrcode.make(uri)
            qr_image.save("/qrdata/" + user.username + ".png")
            print("QR Code başarıyla oluşturuldu.")
            qr_code_mailf("/qrdata/" + user.username + ".png", user.email, user.qrcode_url)
        else:
            user.twofactoractive = bool(_bool)
            user.save()
        # qr_image_io = BytesIO()
        # qr_image.save(qr_image_io, format='PNG')

        payload = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
			'username': user.username,
            'twofactoractive': user.twofactoractive,
            'is_uploadpp': user.is_uploadpp,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=False)
        response.data = {
            'token': token,
        }
        return response



class QRCodeURL(APIView):
    def get(self, request, username):
        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        return JsonResponse({'qrcode_url': user.twofactorqr.url})

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=400)

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")
        
        user.status = True
        user.save()
        if (user.twofactoractive == 1):
            payload = {
			'username': user.username,
            'twofactoractive': user.twofactoractive,
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            response = Response()
            response.set_cookie(key='2fa', value=token, httponly=False)
            response.data = {
            'token': token,
            }
            return response

        payload = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
			'username': user.username,
            'twofactoractive': user.twofactoractive,
            'is_uploadpp': user.is_uploadpp,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=False)
        response.data = {
            'token': token,
        }
        return response

class Login42View(APIView):
    def post(self, request):
        code = request.data.get('code')
        url1 = 'https://api.intra.42.fr/oauth/token'
        url2 = 'https://api.intra.42.fr/v2/me'

        data = {
            'client_id': 'u-s4t2ud-466f8ff9df025fc510352c0b2b970477cd8618f031b1e7e196e8f573b492ae53',
            'code': code,
            'client_secret': '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',
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://10.11.4.10',
        }

        response = requests.post(url1, json=data)
        access_token = response.json().get('access_token')

        Bearer = "Bearer " + access_token
        headers = {
        'Authorization': Bearer,
        }
        response = requests.get(url2, headers=headers)
        username = response.json().get('login')
        email = response.json().get('email')
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 25))
        if((User.objects.filter(email=email).exists()) == False):
            serializer = UserSerializer(data={'email': email, 'username': username, 'password': password})
            if serializer.is_valid():
                user = serializer.save()
        if(User.objects.filter(email=email).exists()):
            user = User.objects.filter(email=email).first()
        payload = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
			'username': user.username,
            'twofactoractive': user.twofactoractive,
            'is_uploadpp': user.is_uploadpp,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        if user.twofactoractive:
            response.set_cookie(key='jwt42', value=token, httponly=False)
        else:
            response.set_cookie(key='jwt', value=token, httponly=False)
        response.data = {
            'token': token
        }
        return response

class TwoFactor(APIView):
    def post(self, request):
        userCode = request.data.get('userCode')
        username = request.data.get('username')
        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        totp = pyotp.TOTP(user.twofactorkey)
        if totp.verify(userCode):
            response = Response()
            response.set_cookie(key='2fa', value='', expires=0)
            payload = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'username': user.username,
                'twofactoractive': user.twofactoractive,
                'is_uploadpp': user.is_uploadpp,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            response.set_cookie(key='jwt', value=token, httponly=False)
            response.data = {
                'token': token
            }
            return response
        else:
            return Response({'error': 'Invalid TOTP code'}, status=400)


class LogoutView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            # Kullanıcıyı bulduysa status'u false yap
            user.status = False
            user.save()

        # Çerezleri sil
        response = Response()
        response.delete_cookie('jwt')
        response.delete_cookie('2fa')
        response.data = {
            'message': 'success'
        }
        return response


def home(request):
    return HttpResponse("Welcome to the homeasdasdasd page!")

class SendFriendRequestView(APIView):
    def post(self, request):
        sender_username = request.data.get('sender_username')
        receiver_username = request.data.get('username')

        if not sender_username or not receiver_username:
            return Response({'error': 'Both sender and receiver usernames are required'}, status=400)

        sender = User.objects.filter(username=sender_username).first()
        if not sender:
            return Response({'error': 'Sender not found'}, status=404)

        if sender.username == receiver_username:
            raise ValidationError("You cannot send a friend request to yourself.")

        receiver = User.objects.filter(username=receiver_username).first()
        if not receiver:
            raise NotFound("User not found.")

        friend_request, created = Friend.objects.get_or_create(sender=sender, receiver=receiver)
        if not created:
            raise ValidationError("Friend request already sent.")

        return Response({'message': 'Friend request sent successfully'}, status=201)

class AcceptFriendRequestView(APIView):
    def post(self, request):
        sender_username = request.data.get('sender_username')
        receiver_username = request.data.get('receiver_username')

        if not sender_username or not receiver_username:
            return Response({'error': 'Both sender and receiver usernames are required'}, status=400)

        # Fetch the sender and receiver users
        sender = User.objects.filter(username=sender_username).first()
        receiver = User.objects.filter(username=receiver_username).first()

        if not sender or not receiver:
            return Response({'error': 'Sender or receiver not found'}, status=404)

        # Find the pending friend request
        friend_request = Friend.objects.filter(sender=sender, receiver=receiver, status='pending').first()

        if not friend_request:
            raise NotFound("Friend request not found.")

        # Accept the friend request
        friend_request.status = 'accepted'
        friend_request.save()

        return Response({'message': 'Friend request accepted'}, status=200)

class DeclineFriendRequestView(APIView):
    def post(self, request):
        sender_username = request.data.get('sender_username')
        receiver_username = request.data.get('receiver_username')

        if not sender_username or not receiver_username:
            return Response({'error': 'Both sender and receiver usernames are required'}, status=400)

        # Fetch the sender and receiver users
        sender = User.objects.filter(username=sender_username).first()
        receiver = User.objects.filter(username=receiver_username).first()

        if not sender or not receiver:
            return Response({'error': 'Sender or receiver not found'}, status=404)

        # Find the pending friend request
        friend_request = Friend.objects.filter(sender=sender, receiver=receiver, status='pending').first()

        if not friend_request:
            return Response({'error': 'Friend request not found'}, status=404)

        # Silinecek arkadaşlık isteği (isteği reddetmek yerine)
        friend_request.delete()

        return Response({'message': 'Friend request declined and deleted'}, status=200)

class BlockedFriendRequestView(APIView):
    def post(self, request):
        sender_username = request.data.get('sender_username')
        receiver_username = request.data.get('receiver_username')

        if not sender_username or not receiver_username:
            return Response({'error': 'Both sender and receiver usernames are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        sender = User.objects.filter(username=sender_username).first()
        receiver = User.objects.filter(username=receiver_username).first()
        
        if not sender or not receiver:
            return Response({'error': 'Sender or receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        # Accepted durumundaki arkadaşlık isteğini bul (her iki yönde de kontrol)
        friend_request = Friend.objects.filter(
            Q(sender=sender, receiver=receiver, status='accepted') |
            Q(sender=receiver, receiver=sender, status='accepted')
        ).first()

        if not friend_request:
            return Response({'error': 'Friend request not found or it is not in accepted status'}, status=status.HTTP_404_NOT_FOUND)

        # Arkadaşlık isteğini blocked olarak güncelle ve bloklayan kişiyi kaydet
        friend_request.status = 'blocked'
        friend_request.blocked_by = sender  # Burada bloklayan kişinin kim olduğunu saklıyoruz
        friend_request.save()

        return Response({'message': 'Friend request blocked successfully'}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from .models import User, Friend

class UnblockFriendView(APIView):
    def post(self, request):
        sender_username = request.data.get('sender_username')
        receiver_username = request.data.get('receiver_username')

        if not sender_username or not receiver_username:
            return Response({'error': 'Both sender and receiver usernames are required'}, status=status.HTTP_400_BAD_REQUEST)

        sender = User.objects.filter(username=sender_username).first()
        receiver = User.objects.filter(username=receiver_username).first()

        if not sender or not receiver:
            return Response({'error': 'Sender or receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the sender is the one who blocked the receiver
        friend_request = Friend.objects.filter(
            (models.Q(sender=sender) & models.Q(receiver=receiver) & models.Q(status='blocked') & models.Q(blocked_by=sender)) |
            (models.Q(sender=receiver) & models.Q(receiver=sender) & models.Q(status='blocked') & models.Q(blocked_by=sender))
        ).first()

        if not friend_request:
            return Response({'error': 'Friend request not found or it is not blocked by you'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the sender was the one who blocked the receiver
        if friend_request.blocked_by != sender:
            return Response({'error': 'You do not have permission to unblock this user'}, status=status.HTTP_403_FORBIDDEN)

        # Unblock the friend request by changing the status back to 'accepted'
        friend_request.status = 'accepted'
        friend_request.blocked_by = None  # Reset the blocked_by field
        friend_request.save()

        return Response({'message': 'Friend unblocked successfully'}, status=status.HTTP_200_OK)

class BlockedListView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        user = User.objects.filter(username=username).first()

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Tek bir sorgu ile hem sender hem de receiver kontrolü
        blocked_users = Friend.objects.filter(
    		Q(sender=user, status='blocked') | Q(receiver=user, status='blocked')
		).values('receiver__username', 'sender__username', 'blocked_by_id')

        blocked_list = [
            {
        		'username': friend['receiver__username'] if friend['sender__username'] == username else friend['sender__username'],
        		'blocked_by': friend['blocked_by_id']  # blocked_by_id bilgisini ekliyoruz
    		}
    	for friend in blocked_users
		]

        return Response(blocked_list, status=status.HTTP_200_OK)




class InvitationsView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        invitations = Friend.objects.filter(receiver=user, status='pending').values('sender__username')
        return Response(list(invitations), status=200)

class FriendsListView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        friends = Friend.objects.filter(sender=user, status='accepted').values('receiver__username')
        friends = list(friends) + list(Friend.objects.filter(receiver=user, status='accepted').values('sender__username'))
        return Response(friends, status=200)
    
    
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import User  # Modelinizin doğru yolunu ekleyin

class UserStatus(APIView):
    def get(self, request, username):
        try:
            user = User.objects.filter(username=username).first()
            if user is None:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Kullanıcının `status` alanını alın
            status_value = user.status  # status değerinin doğru bir şekilde alındığını kontrol edin
            
            # Yanıt döndürün
            return Response({'status': status_value}, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Hata durumunda daha ayrıntılı bilgi döndürün
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
