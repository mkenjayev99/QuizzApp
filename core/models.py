from django.conf import settings
from ckeditor.fields import RichTextField
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.safestring import mark_safe
from rest_framework_simplejwt.tokens import RefreshToken


class TimeStamp(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# Subjects
class Category(TimeStamp):
    title = models.CharField(max_length=218)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'


# Questions
class Question(TimeStamp):
    LEVEL = (
        (0, 'Easy'),
        (1, 'Medium'),
        (2, 'Hard'),
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Category', db_index=True)
    question = models.CharField(max_length=218)
    level = models.IntegerField(choices=LEVEL)

    def __str__(self):
        return self.question


# Answers
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Question', db_index=True)
    title = models.CharField(max_length=218, verbose_name='answer')
    is_true = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class AccountManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        if username is None:
            raise TypeError('You should have an username!')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        if password is None:
            raise TypeError("Password should not be None!")
        user = self.create_user(
            username=username,
            password=password,
            **extra_fields
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


def file_path(instance, filename):
    return f"courses/{instance.title}/{instance.title}/{filename}"


# ROLES = (teacher, student)
class Account(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=218, unique=True, verbose_name='Username', db_index=True)
    first_name = models.CharField(max_length=218)
    last_name = models.CharField(max_length=218)
    image = models.ImageField(upload_to=file_path, null=True, blank=True)
    location = models.CharField(max_length=218)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    bio = RichTextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def image_tag(self):
        if self.image:
            return mark_safe(f'<a href="{self.image.url}"><img src="{self.image.url}" style="height:30px;"/></a>')
        else:
            return "-"

    @property
    def image_url(self):
        if self.image:
            if settings.DEBUG:
                return f'{settings.LOCAL_BASE_URL}{self.image.url}'
            return f'{settings.PROD_BASE_URL}{self.image.url}'
        return None

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return data


class Result(TimeStamp):  # by_Student,, Quizz renamed to Result
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    questions = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    result = models.DecimalField(decimal_places=2, max_digits=5)

    def __str__(self):
        return f"{self.author} - {self.result}"


class Statistics(TimeStamp):
    average_student = models.ManyToManyField(Result)
    average_category = models.ManyToManyField(Category)




