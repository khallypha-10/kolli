from django.shortcuts import render, redirect, get_object_or_404
from . forms import SignupForm, BecomeAVendorForm, ProductForm, ContactVendorForm, ProductRatingForm, AddressForm, VendorRatingForm
from django.contrib import messages
from django.contrib.auth.models import User
from . models import BecomeAVendor, Product, ContactVendor, ProductRating, VendorRating, OrderItem, Orders, Wishlist, Address, Size, Colour, Payments
from django.contrib.auth.decorators import login_required
from mailjet_rest import Client
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from django.db.models import F, ExpressionWrapper, IntegerField, Case, When, FloatField
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
import random
import string
from django.utils import timezone
from django.conf import settings
# Create your views here.

def home(request):
    
    return render(request, "home.html")

def register(request):
    form = SignupForm()
    if request.method=='POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully! Please Login')
            return redirect("login")
    context = {"form": form}
    return render(request, "register.html", context)

@login_required(login_url='login')
def profile(request, user):
    user = User.objects.get(username=request.user)
    vendor = BecomeAVendor.objects.get(user=user)
    context = {'user': user, 'vendor': vendor}
    return render(request, "my-account.html", context)

@login_required(login_url='login')
def edit_user_address(request, user):
    address = Address.objects.get(user__username=user)
    form = AddressForm(instance=address)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect("profile", user=address.user.username)
    context = {'form': form}
    return render(request, "edit_user_address.html", context)

def become_a_vendor(request):
    form = BecomeAVendorForm()
    sk = '55a378d4030f416ff0caf91d25c2af1b'
    api_keyy = 'f3961dfd2343581023c855827d30a520'
    if request.method=='POST':
        form = BecomeAVendorForm(request.POST, request.FILES)
        api_key = api_keyy
        api_secret = sk
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, 'Your request has been received and is under review. We will contact you after the revision.')
            mailjet = Client(auth=(api_key, api_secret), version='v3.1')
            data = {
            'Messages': [
                            {
                                    "From": {
                                            "Email": "sulaiman.ibrahim.0998@gmail.com",
                                            "Name": "Me"
                                    },
                                    "To": [
                                            {
                                                    "Email": obj.company_email,
                                                    "Name": str(request.user.get_full_name())
                                            },
                                            {
                                                    "Email": "sulaiman.ibrahim.0998@gmail.com",
                                                    "Name": "Me"
                                            }
                                    ],
                                    "Subject": "Request to become a vendor",
                                    "TextPart": f"Becoming a vendor",
                                    "HTMLPart": f"""
                                        <h3>Dear {obj.company_name},</h3>
                                        <p>Email: {obj.company_email}</p>
                                        <p>Phone Number: {obj.company_phone_number}</p>
                                        <p>Category: {obj.company_category}</p>
                                        <p>State: {obj.company_state}</p>
                                        <p>Address: {obj.company_address}</p>
                                        {f'<img src="{request.build_absolute_uri(obj.company_cac.url)}" alt="CAC Document"><br>' if obj.company_cac.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else f'<p>CAC Document: {obj.company_cac}</p>'}
                                        <p>Your request to be a vendor is under review. We will notify you of the developments. Thank you for your patience.</p>
                                        """



                            }
                    ]
            }
            result = mailjet.send.create(data=data)
            return redirect("home")
    context = {"form": form}
    return render(request, "become-a-vendor.html", context)



def list_product(request):
    form = ProductForm()
    if request.method=='POST':
        form = ProductForm(request.POST, request.FILES)
        vendor = BecomeAVendor.objects.get(user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.vendor = vendor
            obj.save()
            form.save_m2m()
            messages.success(request, 'Product added successfully!')
            return redirect("vendor-profile", user=request.user)
    context = {"form": form}
    return render(request, "list-product.html", context)

def edit_list_product(request, slug):
    product = Product.objects.get(slug=slug)
    form = ProductForm(instance=product)
    if request.method=='POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        vendor = BecomeAVendor.objects.get(user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.vendor = vendor
            obj.save()
            # Manually set the Many-to-Many field
            colours = request.POST.getlist('colours')  # Get selected colours
            obj.colours.set(colours)  # Assign colours to product
            messages.success(request, 'Product updated successfully!')
            return redirect("vendor-profile", user=request.user)
    context = {"form": form}
    return render(request, "edit-list-product.html", context)

def vendor_profile_page(request, user):
    vendor = BecomeAVendor.objects.get(user=request.user)
    vendor_messages = ContactVendor.objects.filter(vendor=vendor).count()
    orders_total = Orders.objects.filter(vendor__company_name=vendor, delivered=False, vendor_accepted=False, canceled=False).count()
    context = {'vendor': vendor, 'vendor_messages': vendor_messages, 'orders_total': orders_total}
    return render(request, "vendor_profile_page.html", context)        

def vendor_all_products(request, user):
    vendor = BecomeAVendor.objects.get(user=request.user)
    products = Product.objects.filter(vendor=vendor).order_by('-id').annotate(
        effective_price=ExpressionWrapper(
            Case(
                When(discount__isnull=False, then=F('price') * (1 - F('discount') / 100.0)),  # Calculate effective price after discount
                default=F('price'),  # If no discount, use the original price
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    )

    sort_option = request.GET.get('sort', None)  # Default sort by price (low to high)
    # Use Coalesce to sort by discounted_price if available, otherwise use price
    if sort_option == 'price_asc':
        products = products.order_by('effective_price')
    elif sort_option == 'price_desc':
        products = products.order_by('-effective_price')
    elif sort_option == 'rating':
        products = products.order_by('-avg_rating')
        
    p = Paginator(products, 5)
    page = request.GET.get('page')
    products = p.get_page(page)
    products_total = Product.objects.filter(vendor=vendor).count()
    # Calculate product range for the current page
    start_index = products.start_index()  # 1-based index of first product
    end_index = products.end_index()  # 1-based index of last product
    context = {'vendor': vendor, 'products': products, 'products_total': products_total, 'page': page, 'start_index': start_index,'end_index': end_index, 'sort_option': sort_option}
    return render(request, "vendor-shop.html", context) 

def vendors(request):
    NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", 
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", 
    "FCT-Abuja", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", 
    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", 
    "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"
    ]

    vendors = BecomeAVendor.objects.all().order_by('-id')
    
    
    category = request.GET.get('category', '')  # Get the selected category from the query string
    state = request.GET.get('state', '')
    if category:
        vendors = BecomeAVendor.objects.filter(company_category=category)
        vendors_total = vendors.all().count()
        p = Paginator(vendors, 1)
        page = request.GET.get('page')
        vendors = p.get_page(page)
        # Calculate vendor range for the current page
        start_index = vendors.start_index()  # 1-based index of first vendor
        end_index = vendors.end_index()  # 1-based index of last vendor
        
    if state:
        vendors = vendors.filter(company_state=state)
        

    p = Paginator(vendors, 3)
    page = request.GET.get('page')
    vendors = p.get_page(page)
    # Calculate vendor range for the current page
    start_index = vendors.start_index()  # 1-based index of first vendor
    end_index = vendors.end_index()  # 1-based index of last vendor
    vendors_total = BecomeAVendor.objects.all().count()
    context = {'vendors': vendors, 'selected_category': category, 'selected_state': state, 'nigerian_states': NIGERIAN_STATES,'vendors_total': vendors_total, 'start_index': start_index,'end_index': end_index } # Pass the states list}
    return render(request, "vendor-wc-store-list.html", context)

def vendor_store(request, slug):
    vendor = BecomeAVendor.objects.get(slug=slug)
    products = Product.objects.filter(vendor=vendor).order_by('-id').annotate(
        effective_price=ExpressionWrapper(
            Case(
                When(discount__isnull=False, then=F('price') * (1 - F('discount') / 100.0)),  # Calculate effective price after discount
                default=F('price'),  # If no discount, use the original price
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    )
    top_rated_products = Product.objects.filter(vendor=vendor).order_by('-avg_rating')[:4]
    ratings = VendorRating.objects.filter(vendor=vendor).order_by('-id')
    ratings_count = VendorRating.objects.filter(vendor=vendor).count()
    sort_option = request.GET.get('sort', None)  # Default sort by price (low to high)
    # Use Coalesce to sort by discounted_price if available, otherwise use price
    if sort_option == 'price_asc':
        products = products.order_by('effective_price')
    elif sort_option == 'price_desc':
        products = products.order_by('-effective_price')
    elif sort_option == 'rating':
        products = products.order_by('-avg_rating')
    p = Paginator(products, 12)
    page = request.GET.get('page')
    products = p.get_page(page)
    form = ContactVendorForm()
    rating_form = VendorRatingForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # Handle Contact Vendor Form Submission
        if form_type == 'contact_vendor':
            form = ContactVendorForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.vendor = vendor
                obj.save()
                request.session['vendor_notification'] = 'You have received a new message.'
                messages.success(request, 'Your message to the vendor has been sent.')
                return redirect("vendor-store", slug=slug)

        # Handle Vendor Rating Form Submission
        elif form_type == 'vendor_rating':
            rating_form = VendorRatingForm(request.POST)
            if rating_form.is_valid():
                obj = rating_form.save(commit=False)
                obj.vendor = vendor
                obj.save()
                messages.success(request, 'Your vendor review has been received.')
                return redirect("vendor-store", slug=slug)
    
    reviews_total = VendorRating.objects.filter(vendor=vendor).count()
    review_avg = VendorRating.objects.filter(vendor=vendor)
    total_stars = 0
    for i in review_avg:
        total_stars += i.review_stars

    if reviews_total > 0:
        avg_rating = total_stars / reviews_total
        avg_rating_percentage = (avg_rating / 5) * 100
    else:
        avg_rating = 0
        avg_rating_percentage = 0

    context = {'vendor': vendor, 'ratings_count': ratings_count,  'sort_option': sort_option, 'products': products, 'ratings': ratings, 'avg_rating': avg_rating, 'avg_rating_percentage':avg_rating_percentage, 'reviews_total': reviews_total, 'form': form, 'rating_form': rating_form, 'top_rated_products': top_rated_products}
    return render(request, "vendor-dokan-store.html", context)




@require_POST
def clear_notification(request):
    request.session.pop('vendor_notification', None)
    return JsonResponse({'status': 'success'})

@require_POST
def clear_notification_order(request):
    request.session.pop('vendor_order', None)
    return JsonResponse({'status': 'success'})




def vendor_messages(request, slug):
    vendor = BecomeAVendor.objects.get(slug=slug)
    vendor_messages = ContactVendor.objects.filter(vendor=vendor).order_by('-id')
    vendor_messages_count = ContactVendor.objects.filter(vendor=vendor).count()
    orders_total = Orders.objects.filter(vendor__company_name=vendor, delivered=False, vendor_accepted=False, canceled=False).count()
    

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')  # Action parameter to differentiate

        if action == "delete_single":
            # Handle single message deletion
            message_id = request.POST.get('message')
            try:
                deleted_message = ContactVendor.objects.get(id=message_id, vendor=vendor)
                deleted_message.delete()
                return JsonResponse({'success': True, 'message': 'Message deleted successfully'})
            except ContactVendor.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Message not found'})

        elif action == "delete_all":
            # Handle delete all messages
            ContactVendor.objects.filter(vendor=vendor).delete()
            return JsonResponse({'success': True, 'message': 'All messages deleted successfully'})

        # Invalid action
        return JsonResponse({'success': False, 'message': 'Invalid action'})

    context = {'vendor_messages': vendor_messages, 'vendor_messages_count': vendor_messages_count, 'vendor': vendor, 'orders_total': orders_total}
    return render(request, "vendor_messages.html", context)





def single_product(request, slug):
    product = Product.objects.get(slug=slug)
    vendor = BecomeAVendor.objects.get(slug=product.vendor.slug)
    products = Product.objects.filter(vendor=vendor).order_by('-id')[:3]
    reviews = ProductRating.objects.filter(product=product).order_by('-id')
    reviews_all = ProductRating.objects.all()
    reviews_highest_rating = ProductRating.objects.filter(product=product).order_by('-review_stars')
    reviews_lowest_rating = ProductRating.objects.filter(product=product).order_by('review_stars')
    reviews_five_stars = ProductRating.objects.filter(product=product, review_stars=5).count()
    reviews_four_stars = ProductRating.objects.filter(product=product,review_stars=4).count()
    reviews_three_stars = ProductRating.objects.filter(product=product,review_stars=3).count()
    reviews_two_stars = ProductRating.objects.filter(product=product,review_stars=2).count()
    reviews_one_star = ProductRating.objects.filter(product=product,review_stars=1).count()
    reviews_total = ProductRating.objects.filter(product=product).count()
    if reviews_total > 0:
        # Example calculation
        five_stars_percentage = (reviews_five_stars / reviews_total) * 100
        four_stars_percentage = (reviews_four_stars / reviews_total) * 100
        three_stars_percentage = (reviews_three_stars / reviews_total) * 100
        two_stars_percentage = (reviews_two_stars / reviews_total) * 100
        one_star_percentage = (reviews_one_star / reviews_total) * 100
        five_stars_percentage = int(five_stars_percentage)
        four_stars_percentage = int(four_stars_percentage)
        three_stars_percentage = int(three_stars_percentage)
        two_stars_percentage = int(two_stars_percentage)
        one_star_percentage = int(one_star_percentage)
    else:
        five_stars_percentage = 0
        four_stars_percentage = 0
        three_stars_percentage = 0
        two_stars_percentage = 0
        one_star_percentage = 0
        
    
    
    review_avg = ProductRating.objects.filter(product=product)
    total_stars = 0
    for i in review_avg:
        total_stars += i.review_stars

    if reviews_total > 0:
        avg_rating = total_stars / reviews_total
        avg_rating_percentage = (avg_rating / 5) * 100
    else:
        avg_rating = 0
        avg_rating_percentage = 0
    highest_discount_product = Product.objects.annotate(
    discount_percentage=ExpressionWrapper(
        ((F('price') - F('discount')) / F('price')) * 100,
        output_field=FloatField()
    )).order_by('-discount_percentage').order_by('-discount').first()
    all_products = Product.objects.all().order_by('-id')[:5]
    form = ProductRatingForm()
    if request.method =='POST':
        form = ProductRatingForm(request.POST)
        if form.is_valid:
            obj = form.save(commit=False)
            obj.product = product
            obj.save()
            messages.success(request, 'Your review has been received')
            return redirect("product-detail", slug=slug)
    context = {'product': product, 'avg_rating': avg_rating, 'avg_rating_percentage': avg_rating_percentage, 'reviews': reviews, 'five_stars_percentage': five_stars_percentage, 'four_stars_percentage': four_stars_percentage, 'three_stars_percentage': three_stars_percentage, 'two_stars_percentage': two_stars_percentage, 'one_star_percentage': one_star_percentage, 'reviews_total': reviews_total, 'reviews_highest_rating': reviews_highest_rating, 'reviews_lowest_rating': reviews_lowest_rating, 'vendor': vendor, 'form':form, 'products': products, 'all_products':all_products, 'highest_discount_product':highest_discount_product}
    return render(request, "product-default.html", context)


@login_required(login_url='login')
def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)

    # Get the selected color and size from the form
    selected_color_id = request.POST.get('color')
    selected_size_id = request.POST.get('size')
    quantity = request.POST.get('quantity')
    quantity = request.POST.get('quantity')
    print(f"Received quantity: {quantity}")  # Debugging statementy
    if quantity == '':
        quantity = 1
        print(f"Received quantity: {quantity}") 

    # Ensure that color and size are selected
    if not selected_color_id or not selected_size_id:
        messages.warning(request, "Please select both color and size.")
        return redirect("product-detail", slug=slug)

    selected_color = get_object_or_404(Colour, id=selected_color_id)
    selected_size = get_object_or_404(Size, id=selected_size_id)

    # Check if there are any active orders for the user
    order_qs = Orders.objects.filter(user=request.user, ordered=False, vendor_accepted=False)

    if order_qs.exists():
        order = order_qs.first()

        # Check if the vendor of the current item matches the vendor of the active order
        if order.vendor != item.vendor:
            messages.warning(request, "You can only order from one vendor at a time.")
            return redirect("product-detail", slug=slug)

        # Check if the item with the selected color and size is already in the cart
        cart_qs = OrderItem.objects.filter(
            product=item, 
            user=request.user, 
            ordered=False, 
            colour=selected_color, 
            size=selected_size
        )

        if cart_qs.exists():
            cart_item = cart_qs.first()
            cart_item.quantity += int(quantity) 
            cart_item.save()
            messages.info(request, "This item quantity was updated.")
        else:
            # Add the new item to the cart with selected color and size
            cart_item = OrderItem.objects.create(
                product=item, 
                user=request.user, 
                ordered=False, 
                vendor=item.vendor,
                colour=selected_color,
                size=selected_size, 
                quantity=quantity 
            )
            order.order_item.add(cart_item)
            messages.info(request, "This item was added to your cart.")

    else:
        # Check if the user already has an order with a different vendor
        existing_order = Orders.objects.filter(user=request.user, ordered=False, vendor_accepted=False)
        if existing_order.exists():
            existing_order_vendor = existing_order.first().vendor
            if existing_order_vendor != item.vendor:
                messages.warning(request, "You can only order from one vendor at a time.")
                return redirect("product-detail", slug=slug)
        
        
        
        # Create a new order for the item if no active order exists
        order_date = timezone.now()
        order = Orders.objects.create(
            user=request.user, 
            order_date=order_date, 
            vendor=item.vendor,
        )

        # Create a new order item with the selected color and size
        cart_item = OrderItem.objects.create(
            product=item, 
            user=request.user, 
            ordered=False, 
            vendor=item.vendor,
            colour=selected_color,
            size=selected_size,
            quantity=quantity 
        )

        order.order_item.add(cart_item)
        messages.info(request, "This item was added to your cart.")

    return redirect("product-detail", slug=slug)



        
def add_quantity(request, slug, colour, size):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Orders.objects.filter(order_item__product=item, user=request.user, ordered=False)
    cart = OrderItem.objects.get(product=item, user=request.user, ordered=False, colour__color=colour, size__sizes=size)
    if order_qs.exists():
        cart.quantity += 1
        cart.save()
    messages.info(request, "The item quantity was updated.")
    return redirect("cart", user=request.user)


def reduce_quantity(request, slug, colour, size):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Orders.objects.filter(order_item__product=item, user=request.user, ordered=False)
    cart = OrderItem.objects.get(product=item, user=request.user, ordered=False, colour__color=colour, size__sizes=size)
    if order_qs.exists():
        cart.quantity -= 1
        cart.save()
        messages.info(request, "The item quantity was updated.")
    if cart.quantity <= 0:
        cart.delete()
        messages.info(request, "This item was removed from your cart.")
    
    return redirect("cart", user=request.user)


def remove_from_cart(request, slug, colour, size):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Orders.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs.first()  # Retrieve the single Orders object
        # Check if the order item is in the order
        if order.order_item.filter(product__slug=slug).exists():
            order_item = OrderItem.objects.filter(
                product=item,
                user=request.user,
                ordered=False,
                colour__color=colour,
                size__sizes=size
            ).first()  # Get the specific OrderItem object
            order.order_item.remove(order_item)
            order_item.delete()
            messages.info(request, "The item was removed from your cart.")
            return redirect("cart", user=request.user)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("cart", user=request.user)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("cart", user=request.user)


def cart(request, user):
    carts = OrderItem.objects.filter(user=request.user, ordered=False).order_by('-id')
    total = 0
    for i in carts:
        quantity = i.quantity
        price = i.product.price
        discount = i.product.discount
        if i.product.discount:
            discounted_price = price - ((discount / 100) * price)
            prant = quantity * discounted_price
        else:
            prant = quantity * price
        total = total + prant
    context ={"carts": carts, "total": total}
    return render(request, "cart.html", context)


def clear_cart(request):
    cart = OrderItem.objects.filter(user=request.user, ordered=False)
    if request.method == 'POST':
        cart.delete()
        messages.success(request, "Cart cleared!")
        return redirect("cart", user=request.user)

@login_required(login_url='login')
def add_to_wishlist(request, slug):
    item = get_object_or_404(Product, slug=slug)
    wish_qs = Wishlist.objects.filter(product=item, user=request.user, ordered=False)
    if wish_qs.exists():
        messages.info(request, "This item is already in your wishlist.")
    else:
        wishlist, created = Wishlist.objects.get_or_create(product=item, user=request.user, ordered=False)
        messages.success(request, "This item was added to your wishlist.")
    return redirect("product-detail", slug=slug)

def wishlist(request, user):
    wishlists = Wishlist.objects.filter(user=request.user, ordered=False)
    context = {'wishlists': wishlists}
    return render(request,"wishlist.html", context)

def remove_from_wishlist(request, slug):
    item = get_object_or_404(Product, slug=slug)
    wish_qs = Wishlist.objects.filter(product=item)
    wish_qs.delete()
    messages.success(request, "The item was removed from your wishlist.")
    order_qs = Orders.objects.filter(
        user=request.user,
        ordered=True,
        order_item__product=item
    )
    if order_qs.exists():
        wish_qs.delete()
        messages.success(request, "The item was removed from your wishlist.")
    return redirect("wishlist", user=request.user)

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

class CheckOutView(View):
    def get(self, request, *args, **kwargs):
        
        try:
            order = Orders.objects.get(user=self.request.user, ordered=False)
            orders = OrderItem.objects.filter(user=self.request.user, ordered=False)
            address_qs= Address.objects.filter(user=self.request.user)
            if not address_qs.exists():
                form = AddressForm()
            else:
                user_address=Address.objects.get(user=self.request.user)
                form = AddressForm(instance=user_address)
            subtotal = 0
            total = 0
            prant = 0
            for i in orders:
                quantity = i.quantity
                price = i.product.price
                discount = i.product.discount
                if discount:
                    discounted_price = price - ((discount / 100) * price)
                    prant = quantity * discounted_price
                else:
                    prant = quantity * price
                total = total + prant
            
            context= {"order": order, "prant": prant, "form": form, "orders": orders, "total": total}
            
            
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(request, "You don't have an active order.")
            return redirect("cart", user=request.user)
        
    def post(self, request, *args, **kwargs):
        try:
            address_qs = Address.objects.filter(user=self.request.user)
            order = Orders.objects.get(user=self.request.user, ordered=False)
            order_items = order.order_item.all()
            if request.method == 'POST':
                if not address_qs.exists():
                    form = AddressForm(self.request.POST)

                else:
                    user_address=Address.objects.get(user=self.request.user)
                    form = AddressForm(self.request.POST, instance=user_address)

                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.user = self.request.user
                    obj.save()
                    address = address_qs[0]
                    order.address = address
                    order_items.update(ordered=True)
                    order.ref_number = create_ref_code()
                    for item in order_items:
                        item.save()
                    order.save()
                    pk = settings.PAYSTACK_PUBLIC_KEY
                    payment = Payments.objects.create(amount=order.total, order=order, email=order.address.email, sub_account_ID=order.vendor.sub_account_ID)
                    payment.save()
                    return redirect("payment", slug=order.slug, ref=payment.ref)
        except Exception as e:
            print(e)
        except ObjectDoesNotExist:
            messages.info(request, "You don't have an active order.")
            return redirect("checkout")

        return redirect("home")


def make_payment(request, slug, ref):
    order = Orders.objects.get(slug=slug)
    
    pk = settings.PAYSTACK_PUBLIC_KEY
    payment = Payments.objects.get(ref=ref)
    context = {
        'payment': payment,
        'paystack_pub_key': pk,
        'amount_value': payment.amount_value(),
        'order': order
        }
    return render(request, 'make_payment.html', context)
    




def verify_payment(request, ref, slug):
    payment = Payments.objects.get(ref=ref)
    verified = payment.verify_payment()
    amount_paid = payment.order.total
    order = Orders.objects.get(slug=slug)
    
    if verified:
        payment.verified = True
        payment.save()
        order.ordered = True
        order.order_date = timezone.now()
        order.save()
        request.session['vendor_order'] = 'You have received a new order.'
        return redirect("thank-you")

    return render(request, "thank_you.html", {"payment": payment})

class PaymentView(View):
    def get(self, request, *args, **kwargs):
        order = Orders.objects.get(user=self.request.user, ordered=False)
        user = User.objects.get(username=request.user)
        context = {"order": order}
        return render(self.request, "payment.html", context)
   
    def post(self, request, *args, **kwargs):
        order = Orders.objects.get(user=self.request.user, ordered=False)
        order_items = order.order_item.all()
        try:
            if request.method == 'POST':
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.ref_number = create_ref_code()
                order.save()
                request.session['vendor_order'] = 'You have received a new order.'
                print(f"Session before redirect: {request.session.get('vendor_order')}")


            
                return redirect("thank-you")
        
        except Exception as e:
            print(f"Error in PaymentView: {e}")
        print(f"Vendor Order Message: {request.session.get('vendor_order')}")


def user_orders(request, user):
    user = User.objects.get(username=request.user)
    orders =  Orders.objects.filter(user=request.user, ordered=True).order_by('-id')
    order = OrderItem.objects.filter(user=request.user)
    vendor = BecomeAVendor.objects.get(user=user)
    context = {'orders': orders, "vendor":vendor}
    return render(request, "user-orders.html", context)

def order_details(request, slug, ref_number):
    orders =  Orders.objects.get(slug=slug, ref_number=ref_number)
    order = orders.order_item.filter(user=request.user)
    total = 0
    for i in order:
        price = i.product.price
        quantity = i.quantity
        discount = i.product.discount
        if discount:
            discounted_price = price - ((discount / 100) * price)
            prant = quantity * discounted_price
        else:
            prant = quantity * price
        total = total + prant
    context = {'orders': orders, 'order': order, 'total': total}
    return render(request, "user-orders-detail.html", context)



def thank_you(request):
    order_qs = Orders.objects.filter(user=request.user, ordered=True, delivered=False, vendor_accepted=False)
    total = 0
    prant=0
    if order_qs.exists():
        orders = order_qs.last()
        order_items = orders.order_item.filter(user=request.user, ordered=True)
        total = 0
        for i in order_items:
            price = i.product.price
            quantity = i.quantity
            discount = i.product.discount
            if discount:
                discounted_price = price - ((discount / 100) * price)
                prant = quantity * discounted_price
            else:
                prant = quantity * price
            total = total + prant
    else:
        total = o
        prant = 0
    context={'orders': orders, 'total': total, 'prant': prant, 'order_items': order_items}

    return render(request, "thank_you.html", context)

def orders_received(request, vendor):
    orders = Orders.objects.filter(vendor__company_name=vendor, ordered=True).order_by('-id')
    vendor = BecomeAVendor.objects.get(user=request.user)
    vendor_messages = ContactVendor.objects.filter(vendor=vendor).count()
    orders_total = Orders.objects.filter(vendor__company_name=vendor, delivered=False, vendor_accepted=False, canceled=False).count()
    context = {'orders': orders, 'vendor': vendor, 'vendor_messages': vendor_messages, 'orders_total': orders_total}
    return render(request, "orders_received.html", context)

def vendor_view_order_details(request, slug, ref_number):
    orders =  Orders.objects.get(slug=slug, ref_number=ref_number)
    order = orders.order_item.filter(user=request.user)
    vendor = BecomeAVendor.objects.get(user=request.user)
    vendor_messages = ContactVendor.objects.filter(vendor=vendor).count()
    orders_total = Orders.objects.filter(vendor__company_name=orders.vendor, delivered=False, vendor_accepted=False, canceled=False).count()
    total = 0
    for i in order:
        price = i.product.price
        quantity = i.quantity
        discount = i.product.discount
        if discount:
            discounted_price = price - ((discount / 100) * price)
            prant = quantity * discounted_price
        else:
            prant = quantity * price
        total = total + prant

    if request.method == 'POST':
        selected_option = request.POST.get('flexRadioDefault')
        delivered = request.POST.get('delivered')
        f"selected option = {selected_option}"
        if selected_option == 'Accept':
            orders.vendor_accepted = True
            orders.save()
            messages.success(request, "You have accepted the order.")
            return redirect("order-detail", slug=slug, ref_number=ref_number)
        elif selected_option == 'Reject':
            orders.vendor_accepted = False
            orders.canceled = True
            orders.save()
            messages.info(request, "You have rejected the order.")
            return redirect("order-detail", slug=slug, ref_number=ref_number)
        if delivered:
            orders.delivered = True
            orders.delivered_on = timezone.now()
            orders.save()
            messages.success(request, "The order was delivered.")
            return redirect("order-detail", slug=slug, ref_number=ref_number)
    context = {'orders': orders, 'order': order, 'vendor': vendor,'total': total, 'vendor_messages': vendor_messages, 'orders_total': orders_total}
    return render(request, "order_details_vendor.html", context)