from django.contrib import admin

from .models import Product, ProductProblem, Ticket, TicketMedia, TicketMessage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "description", 'created_at', 'is_active', 'attachment', 'is_subproduct_of']
    list_display_links = ["pk", "name"]
    readonly_fields = ["created_at", "updated_at"]

    search_fields = ["name"]
    ordering = ['pk']

    list_select_related = ["is_subproduct_of"]


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
    list_display = ['id', 'question', 'customer', 'is_solved', 'telegram_message_id', 'created_at', 'updated_at']
    list_display_links = ["id", 'question']


@admin.register(TicketMedia)
class TicketMediaAdmin(admin.ModelAdmin):
    list_display = ["id", "telegram_id", "media_type", "ticket_id", "created_at", "updated_at"]


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "message_id", "ticket_id", "ticket"]

    list_select_related = ["ticket"]
