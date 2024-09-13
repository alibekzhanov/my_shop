from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from .models import CartItem, Category, Order, OrderItem, Product, Cart, АvailabilityAlert
from django.views.generic import ListView, DetailView, FormView, TemplateView, UpdateView, CreateView, DeleteView
from .forms import OrderForm, UserRegistrationForm, PaymentForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail

from .fake_payment_system import FakePaymentSystem
from .payment_gateaway import PaymentSystem


def gmail_mail(request):
    return HttpResponse("Вы отправили email")


class ManagerMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Менеджеры").exists()


class ManagerDashboardView(ManagerMixin, TemplateView):
    template_name = 'manager/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_count'] = len(User.objects.all())
        context['total_revenue'] = Order.objects.get_revenue()
        context['total_sold'] = OrderItem.objects.get_count_products_sold()

        return context


class ManagerOrdersView(ManagerMixin, ListView):
    model = Order
    template_name = 'manager/orders.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
    paginate_by = 3  # Количество заказов на одной странице


class ManagerProductsView(ManagerMixin, ListView):
    model = Product
    template_name = 'manager/products.html'
    context_object_name = 'products'
    ordering = ['-created_at']
    paginate_by = 3  # Количество товаров на одной странице


class ManagerProductsUpdateView(ManagerMixin, UpdateView):
    model = Product
    template_name = 'manager/product_update.html'
    context_object_name = 'product'
    ordering = ['-created_at']
    fields = ['description', 'price', 'discount_price', 'category', 'image', 'quantity']
    success_url = reverse_lazy('manager_products')


class ManagerProductsDeleteView(ManagerMixin, DeleteView):
    template_name = 'manager/product_confirm_delete.html'
    model = Product
    success_url = reverse_lazy('manager_products')


class ManagerProductsAddView(ManagerMixin, CreateView):
    model = Product
    template_name = 'manager/product_add.html'
    fields = ['name', 'description', 'price', 'discount_price', 'category', 'image', 'quantity']
    success_url = reverse_lazy('manager_products')

    def form_valid(self, form):
        print("Форма валидна")
        return super().form_valid(form)


class ManagerOrdersUpdateView(ManagerMixin, UpdateView):
    model = Order
    template_name = 'manager/orders_update.html'
    fields = ['status', 'payment_status', 'address']
    success_url = reverse_lazy('manager_orders')


class CartDetailView(TemplateView, LoginRequiredMixin):
    template_name = 'cart/cart_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_object_or_404(Cart, user = self.request.user)
        context['cart'] = cart
        return context


class AddToCartView(View, LoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug = self.kwargs['slug'])
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if product.quantity > (cart_item.quantity):
                cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')


class RemoveToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=self.request.user)
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()  # Сохраните изменения в базе данных
        else:
            cart_item.delete()
        return redirect('cart')


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('product_list')


class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html'
    success_url = reverse_lazy('product_list')
    

class SignUp(FormView):
    template_name = "accounts/signup.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        user = form.save()
        send_mail(
            "Добро пожаловать в магазин ItStepShop",
            "Держи промокод NEWUSER",
            "olzhas2201@gmail.com",
            [user.email],
            fail_silently=False,
        )
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)


class ProductListView(ListView):
    model = Product
    template_name = 'shop/product/list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        categoty_slug = self.kwargs.get("category_slug")
        if categoty_slug:
            category = get_object_or_404(Category, slug = categoty_slug)
            queryset = queryset.filter(category=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["category"] = None
        context["is_manager"] = self.request.user.groups.filter(name='Менеджеры').exists()
        if 'category_slug' in self.kwargs:
            context["category"] = get_object_or_404(Category, slug = self.kwargs['category_slug'])
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product/product_detail.html"
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(slug=self.kwargs['slug'])
    

class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user = self.request.user)
        if not cart.cart_item.exists():
            return redirect("product_list")

        form = OrderForm
        return render(request, 'order/order_create.html', {'form' : form, 'cart' : cart})

    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user = self.request.user)
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()

            for item in cart.cart_item.all():
                item.product.quantity = item.product.quantity - item.quantity
                item.product.save()

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            cart.cart_item.all().delete()

            return redirect('payment', order_id=order.id)
        return redirect(request, 'order/order_create.html', {'form': form, 'cart': cart})
    

class OrderConfirmationView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_cofirmation.html'
    context_object_name = 'order'

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['order_id'], user=self.request.user)
    

class AddAlertView(View):
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        АvailabilityAlert.objects.get_or_create(user=request.user, product=product)
        return redirect('product_list')


class PaymentView(LoginRequiredMixin, FormView):
    template_name = "payments/payment_form.html"
    form_class = PaymentForm
    success_url = reverse_lazy('payment')

    payment_system: PaymentSystem = FakePaymentSystem()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=self.request.user)

        context['order'] = order
        context['total_price'] = order.total_price

        return context

    def form_valid(self, form):
        card_number = form.cleaned_data['card_number']
        cvc = form.cleaned_data['cvc']
        expired_date = form.cleaned_data['expired_date']

        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        total_price = order.total_price

        result = self.payment_system.create_payment(total_price, card_number=card_number, cvc=cvc, expired_date=expired_date)

        if result['status'] == 'success':
            order.payment_status = True
            order.save()
            return redirect('order_confirmation', order_id=order.id)

        context = self.get_context_data(result=result)
        return self.render_to_response(context)
    

class UserOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/user_orders.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        # Получаем только заказы текущего пользователя
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
