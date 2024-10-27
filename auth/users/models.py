from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import string, random
from django.conf import settings

def key_generator(size=100, chars=string.ascii_uppercase + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            twofactorkey=key_generator(),
            **extra_fields
        )
        user.set_password(password)  # Şifreyi güvenli bir şekilde ayarlar
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=20, default='John Doe')
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=150, unique=True)
    twofactorkey = models.CharField(max_length=255)
    qrcode_url = models.CharField(max_length=255)
    twofactoractive = models.BooleanField(null=True, blank=True, default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    resetpass = models.CharField(max_length=255, blank=True)
    is_uploadpp = models.BooleanField(default=False)
    status = models.BooleanField(default=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()  # Burada "CustomUserManager" kullanıyoruz

    def is_friends_with(self, other_user):
        return Friend.objects.filter(
            (models.Q(sender=self) & models.Q(receiver=other_user) & models.Q(status='accepted')) |
            (models.Q(sender=other_user) & models.Q(receiver=self) & models.Q(status='accepted'))
        ).exists()

    def send_friend_request(self, receiver):
        if self == receiver:
            raise ValueError("You cannot send a friend request to yourself.")
        if self.is_friends_with(receiver):
            raise ValueError("You are already friends with this user.")
        friend_request, created = Friend.objects.get_or_create(sender=self, receiver=receiver)
        if not created:
            raise ValueError("Friend request already sent.")
        return friend_request

    def accept_friend_request(self, sender):
        friend_request = Friend.objects.filter(sender=sender, receiver=self, status='pending').first()
        if not friend_request:
            raise ValueError("Friend request not found.")
        friend_request.status = 'accepted'
        friend_request.save()
        return friend_request

    def decline_friend_request(self, sender):
        friend_request = Friend.objects.filter(sender=sender, receiver=self, status='pending').first()
        if not friend_request:
            raise ValueError("Friend request not found.")
        friend_request.status = 'declined'
        friend_request.save()
        return friend_request

class Friend(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('blocked', 'Blocked'),
    )

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    blocked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='blocked_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.status}"