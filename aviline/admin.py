from django.contrib import admin

from .models import Product, ProductProblem, Ticket, TicketMedia


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "description", 'created_at']
    list_display_links = ["pk", "name"]
    readonly_fields = ["created_at", "updated_at"]

    search_fields = ["name"]
    ordering = ['pk']


@admin.register(ProductProblem)
class ProductProblemAdmin(admin.ModelAdmin):
    list_display = ["pk", "title", "product", "created_at"]
    list_display_links = ["pk", "title", "product"]
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["title", "product__name"]

    list_select_related = ["product"]
    ordering = ["product__id", "pk"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    ...
