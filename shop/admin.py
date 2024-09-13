from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, PromoCode, GroupDiscount, АvailabilityAlert

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ('product',)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('user__username', 'address')
    inlines = [OrderItemInline]

class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'valid_until')
    search_fields = ('code',)

class GroupDiscountAdmin(admin.ModelAdmin):
    list_display = ('group', 'discount')

# Регистрация моделей в админке
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PromoCode, PromoCodeAdmin)
admin.site.register(GroupDiscount, GroupDiscountAdmin)
admin.site.register(АvailabilityAlert)
