from django.db.models import Model, CharField, TextField, ImageField, BooleanField, DateTimeField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now


class Announcement(Model):
    """
    Модель оголошення на index-сторінці сайту.
    """
    name = CharField('Назва', max_length=80, unique=True)
    description = CharField('Опис оголошення', max_length=300)
    css_style = TextField('Стилі (CSS)', max_length=600, default='',
                          blank=True)
    image = ImageField('Зображення', upload_to='advertisement_images',
                       blank=True, null=True)
    created_date = DateTimeField('Дата', auto_now_add=True)
    disable_date = DateTimeField('Коли вимкнути', default=None,
                                 blank=True, null=True)
    is_active = BooleanField('Активне', default=False)

    class Meta:
        db_table = 'site_announcements'
        verbose_name = 'Оголошення'
        verbose_name_plural = 'Оголошення'
        ordering = ('-created_date',)

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Announcement)
def ensure_single_active_advertisement(sender, instance, **kwargs):

    if instance.pk is None:
        Announcement.objects.exclude(pk=instance.pk).update(is_active=False)
    else:
        if instance.is_active:
            Announcement.objects.exclude(
                pk=instance.pk).update(is_active=False)
