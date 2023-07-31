from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def lav_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "p_%s.%s" % (uuid.uuid4().time, ext)
    return 'lav_photo/lav_{0}/{1}'.format(instance.lav_id.id, filename)

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "u_p_%s.%s" % (uuid.uuid4().time, ext)
    return 'user_photo/user_{0}/{1}'.format(instance.id, filename)

def compressImage(uploaded_image):
    image_temp = Image.open(uploaded_image)
    outputIoStream = BytesIO()
    image_temp.thumbnail( (1280,1280) )
    try:
        image_exif = image_temp._getexif()
        image_orientation = image_exif[274]

        if image_orientation == 3:
            image_temp = image_temp.rotate(180, expand=True)
        if image_orientation == 6:
            image_temp = image_temp.rotate(-90, expand=True)
        if image_orientation == 8:
            image_temp = image_temp.rotate(90, expand=True)
    except:
        pass
    image_temp.save(outputIoStream , format='JPEG', quality=80)
    outputIoStream.seek(0)
    uploaded_image = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.jpg" % uploaded_image.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
    return uploaded_image

class User(AbstractUser):

    email = models.EmailField(
    ("Email"),
    unique=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    photo = models.ImageField(
        verbose_name="Фото", 
        null=True,
        blank=True,
        upload_to=user_directory_path,
        default='user_photo/av.jpg'
    )
    
    name = models.CharField(
        verbose_name="Имя",
        max_length=15,
        blank=True
        )

    email_verify = models.BooleanField(
        verbose_name="Проверено",
        null=False,
        default=False
        )
    
    def save(self, *args, **kwargs):
        self.photo = compressImage(self.photo)
        super(User, self).save(*args, **kwargs)
    

class Lavochki(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete = models.CASCADE, 
        verbose_name="Пользователь",
        null=False
    )

    x = models.FloatField(
        verbose_name="Долгота",
        null=False
    )

    y = models.FloatField(
        verbose_name="Широта",
        null=False
    )

    description = models.TextField(
        verbose_name="Описание", 
        null=False
    )

    is_padik =  models.BooleanField(
        verbose_name="Возле подъезда", 
        null=True,
        blank=True,
        default=None
    ) 

    is_spinka =  models.BooleanField(
        verbose_name="Спинка", 
        null=True,
        blank=True,
        default=None
    ) 

    is_ten =  models.BooleanField(
        verbose_name="В тени", 
        null=True,
        blank=True,
        default=None, 
    ) 

    date_added = models.DateTimeField(
        verbose_name="Дата добавление", 
        null=False,
        auto_now=True
    )

    is_valid = models.BooleanField(
        verbose_name="Проверено",
        null=False,
        default=False
    )

    is_edit = models.BooleanField(
        verbose_name="На редактирование",
        null=False,
        default=False
    )

class RatingStar(models.Model):
    value = models.SmallIntegerField(
        verbose_name="Звезда рейтинга",
        default=0
    )

    def __str__(self):
        return f'{self.value}'

    class Meta:
        ordering = ['-value']


class Marks(models.Model):
    user_id = models.ForeignKey(
        User, 
        on_delete = models.CASCADE, 
        verbose_name="Пользователь",
        null=False
    )

    lavochka_id = models.ForeignKey(
        Lavochki, 
        on_delete = models.CASCADE, 
        verbose_name="Лавочка",
        null=False
    )

    rating = models.ForeignKey(
        RatingStar, 
        on_delete = models.CASCADE, 
        verbose_name="Оценка",
    )

    date_added = models.DateTimeField(
        verbose_name="Дата добавления",
        null=False,
        auto_now=True
    )

class PhotoLav(models.Model):
    image_path = models.ImageField(
        verbose_name="Фото", 
        null=False,
        upload_to=lav_directory_path 
    )

    alt = models.CharField(
        verbose_name="Описание",
        null=True,
        blank=True,
        max_length=250
    )

    lav_id = models.ForeignKey(
        Lavochki, 
        on_delete = models.CASCADE, 
        verbose_name="ID лавочки",
        null=False
    )


    is_valid = models.BooleanField(
        verbose_name="Проверено", 
        null=False,
        default=False
    )

    def save(self, *args, **kwargs):
        self.image_path = compressImage(self.image_path)
        super(PhotoLav, self).save(*args, **kwargs)


