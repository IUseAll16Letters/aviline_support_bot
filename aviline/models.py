from django.db import models


class CreateUpdateProxy(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(CreateUpdateProxy):
    name = models.CharField(max_length=150, unique=True, null=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'id: {self.pk} name: {self.name}'


class ProductProblem(CreateUpdateProxy):
    title = models.CharField(max_length=255, null=False)
    solution = models.TextField(blank=False, null=False)

    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.product.name} {self.title}'
