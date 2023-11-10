__all__ = (
    "Product",
    "ProductProblem",
    "Ticket",
    "TicketMessage",
    "TicketMedia",
    # "ProductDetail",
)

from django.db import models

from .validators import product_name_lte_64_bytes


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
    name = models.CharField(
        max_length=64, unique=True, null=False, validators=[product_name_lte_64_bytes],
        help_text='Имя продукта, не более 64 байт (примерно 32 символа кириллицы)'
    )
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=False, blank=False)
    attachment = models.URLField(verbose_name="attachment link", null=True, blank=True)

    is_subproduct_of = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='subproduct'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['id', ]

    def __str__(self):
        return f'{self.pk}. {self.name}'


class ProductDetail(CreateUpdateProxy):
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=255, blank=False, null=False)
    attachment = models.URLField(verbose_name="attachment link", null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class ProductProblem(CreateUpdateProxy):
    title = models.CharField(max_length=255, null=False)
    solution = models.TextField(blank=False, null=False)

    attachment = models.URLField(verbose_name="file link attachment", null=True, blank=True)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey("content_type", "object_id")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['id']

    def __str__(self):
        return f'{self.pk}. {self.product.name} {self.title}'


class Ticket(CreateUpdateProxy):
    customer = models.PositiveIntegerField(editable=False)
    question = models.TextField(blank=False, null=False)

    is_solved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'
        ordering = ['id']

    def __str__(self):
        return f"{self.pk}. {self.question[:30]}..."


class TicketMedia(CreateUpdateProxy):
    telegram_id = models.CharField(max_length=150, null=False, blank=False, editable=False)
    media_type = models.SmallIntegerField(
        choices=MediaTypeChoices.choices,
        default=MediaTypeChoices.photo,
    )

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return f"{self.pk}. {self.telegram_id[:10]}"


class TicketMessage(CreateUpdateProxy):
    message_id = models.PositiveBigIntegerField(null=False, blank=False)

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return f"{self.pk}. {self.ticket}"

#
# class Visitor(CreateUpdateProxy):
#     user_id = models.IntegerField(null=False, blank=False)
#     username = models.CharField(max_length=255, null=True, blank=True)
#     firstname = models.CharField(max_length=255, null=True, blank=True)
#     lastname = models.CharField(max_length=255, null=True, blank=True)


