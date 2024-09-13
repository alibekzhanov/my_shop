from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, null=True, blank=True)  # Убираем unique и добавляем null=True, blank=True
    parent = models.ForeignKey('self', null=True, blank=True, related_name="children", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/products/')
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def get_discounted_price(self):
        """Возвращает цену со скидкой, если она есть, иначе стандартную цену."""
        if self.discount_price:
            return self.discount_price
        return self.price

    def get_display_price(self):
        """Возвращает строку для отображения цены, учитывая скидку."""
        if self.discount_price:
            return f'{self.discount_price} <s>{self.price}</s>'
        return f'{self.price}'


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user.username}"

    def get_total_price(self):
        """Возвращает общую стоимость всех товаров в корзине без учета скидок."""
        return sum(item.get_total_item_price() for item in self.cart_item.all())

    def get_discounted_price(self):
        """Возвращает общую стоимость всех товаров в корзине с учетом скидок."""
        total = self.get_total_price()
        if self.user.groups.exists():
            group_discount = self.user.groups.first().groupdiscount.discount
            total *= (1 - group_discount / 100)
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Товары в корзине"
        verbose_name_plural = "Товары в корзинах"

    def __str__(self):
        return f"{self.quantity}: {self.product.name}"

    def get_total_item_price(self):
        """Возвращает общую стоимость текущего элемента корзины."""
        return self.quantity * self.product.get_discounted_price()

class OrderManager(models.Manager):
    def get_revenue(self):
        return self.all().aggregate(revenue=models.Sum('total_price'))['revenue']

class Order(models.Model):
    STATUS_CHOICES = [
        ('ordered', 'Заказан'),
        ('shipped', 'Отправлен'),
        ('received', 'Получен'),
        ('canceled', 'Отменен'),
        ('returned', 'Возвращен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ordered')
    payment_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f'Заказ номер {self.id} пользователя {self.user.username}'

    def get_total_price(self):
        """Возвращает общую стоимость всех товаров в заказе."""
        return sum(item.get_total_item_price() for item in self.items.all())

    def get_status_display(self):
        """Возвращает статус заказа для отображения."""
        return dict(Order.STATUS_CHOICES).get(self.status, 'Неизвестно')
    

class OrderItemManager(models.Manager):
    def get_count_products_sold(self):
        return self.all().aggregate(total_sold=models.Sum('quantity'))['total_sold']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    objects = OrderItemManager()
    class Meta:
        verbose_name = "Запись заказов"
        verbose_name_plural = "Записи заказов"

    def __str__(self):
        return f"{self.quantity}: {self.product.name}"

    def get_total_item_price(self):
        """Возвращает общую стоимость текущего элемента заказа."""
        return self.quantity * self.product.get_discounted_price()


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_until = models.DateTimeField()

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code

    def is_valid(self):
        """Проверяет, действителен ли промокод."""
        return self.valid_until >= timezone.now()


class GroupDiscount(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Группа клиента"
        verbose_name_plural = "Группы клиентов"

    def __str__(self):
        return f'{self.group.name}: {self.discount}%'
    
class АvailabilityAlert(models.Model):
    user = models.ForeignKey(User, related_name='alert', on_delete = models.CASCADE, null=True)
    product = models.ForeignKey(Product, related_name='alert', on_delete = models.CASCADE,  null=True)

    class Meta:
        verbose_name = "Оповещение"
        verbose_name_plural = "Оповещения"

    def __str__(self):
        return f'{self.user} {self.product}'