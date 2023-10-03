__all__ = (
    "Product",
    "ProductProblem",
    "Ticket",
    "TicketMessage",
    "TicketMedia",
)

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class CreateUpdateProxy(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MediaTypeChoices(models.IntegerChoices):
    photo = (1, 'Photo')
    video = (2, 'Video')
    audio = (3, 'Audio')
    document = (4, 'Document')
    animation = (5, 'Animation')


class Product(CreateUpdateProxy):
    name = models.CharField(max_length=150, unique=True, null=False)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=False, blank=False)

    def __str__(self):
        return f'{self.pk}. {self.name}'


class SubProduct(CreateUpdateProxy):
    name = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=False, blank=False)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, limit_choices_to={"is_active": True})


class ProductProblem(CreateUpdateProxy):
    title = models.CharField(max_length=255, null=False)
    solution = models.TextField(blank=False, null=False)

    attachment = models.URLField(verbose_name="file link attachment", null=True, blank=True)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey("content_type", "object_id")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.name} {self.title}'


class Ticket(CreateUpdateProxy):
    customer = models.PositiveIntegerField(editable=False)
    question = models.TextField(blank=False, null=False)

    is_solved = models.BooleanField(default=False)


class TicketMedia(CreateUpdateProxy):
    telegram_id = models.CharField(max_length=150, null=False, blank=False, editable=False)
    media_type = models.SmallIntegerField(
        choices=MediaTypeChoices.choices,
        default=MediaTypeChoices.photo,
    )

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, editable=False)


class TicketMessage(CreateUpdateProxy):
    message_id = models.PositiveBigIntegerField(null=False, blank=False)

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, editable=False)


class Visitor(CreateUpdateProxy):
    user_id = models.IntegerField(null=False, blank=False)
    username = models.CharField(max_length=255, null=True, blank=True)
    firstname = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
