from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django_resized import ResizedImageField
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .paystack  import  Paystack
import secrets
# Create your models here.

class BecomeAVendor(models.Model):

    furniture = 'Furniture'
    fashion = 'Fashion'
    electronics = 'Electronics'
    accessories = 'Accessories'
    cosmetics = 'Cosmetics'
    health = 'Health'
    kitchen = 'Kitchen'
    toys_games = 'Toys & Games'
    clothes = 'Clothes'
    others = 'Others'
    category_choices = [
        (furniture , 'Furniture'), (fashion ,'Fashion'), (electronics, 'Electronics'), (accessories, 'Accessories'), (cosmetics, 'Cosmetics'), (health , 'Health'), (kitchen , 'Kitchen'), (clothes , 'Clothes'),(kitchen , 'Kitchen'), (toys_games , 'Toys & Games'), (others , 'Others')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_account_ID = models.CharField(max_length=50, blank=True, null=True)
    company_name = models.CharField(max_length=100)
    company_email = models.EmailField(max_length=254)
    company_phone_number = PhoneNumberField()
    company_state_choices = models.TextChoices("company_state_choices", "Abia Adamawa Akwa Ibom Anambra Bauchi Bayelsa Benue Borno Cross River Delta Ebonyi Edo Ekiti Enugu FCT-Abuja Gombe Imo Jigawa Kaduna Kano Katsina Kebbi Kogi Kwara Lagos Nasarawa Niger Ogun Ondo Osun Oyo Plateau Rivers Sokoto Taraba Yobe Zamfara"
    )
    company_state = models.CharField(choices=company_state_choices, max_length=150)
    company_address = models.CharField(max_length=200)
    company_cac = models.FileField(upload_to='become-a-vendor', max_length=100)
    company_logo = models.ImageField( upload_to='vendors')
    company_description = models.TextField()
    company_category = models.CharField(max_length=50, choices=category_choices, help_text="Choose Category *")
    company_account_number = models.CharField(max_length=10)
    company_bank = models.CharField(max_length=75)
    company_account_name = models.CharField(max_length=105)
    approved = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Save the product instance first to generate a primary key
        if not self.pk:  # Check if the instance is new
            self.slug = slugify(f"{self.user}-{self.company_name}")
            super().save(*args, **kwargs)

        # Now calculate the avg_rating only if there are ratings
        vendor_ratings = self.vendor_ratings.aggregate(avg_rating=Avg('review_stars'))
        self.avg_rating = vendor_ratings['avg_rating'] if vendor_ratings['avg_rating'] is not None else 0

        # Save the instance again with the updated avg_rating
        super().save(*args, **kwargs)



    class Meta:
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return f"{self.company_name}"

class Colour(models.Model):
    Color_content = models.TextChoices("Color_content", "BLACK BLUE BRONZE GRAY GREEN ORANGE PINK PURPLE RED SILVER WHITE")
    color = models.CharField(choices=Color_content, max_length=10)

    def __str__(self):
        return f"{self.color}"

class Size(models.Model):
    SIZES = {
        "XS": "Extra Small",
        "S": "Small",
        "M": "Medium",
        "L": "Large",
        "XL": "Extra Large",
        "XXL": "Extra Extra Large",
        "XXXL": "Extra Extra Extra Large",
        "30": "30",
        "31": "31",
        "32": "32",
        "33": "33",
        "34": "34",
        "35": "35",
        "36": "36",
        "37": "37",
        "38": "38",
        "39": "39",
        "40": "40",
        "41": "41",
        "42": "42",
        "43": "43",
        "44": "44",
        "45": "45",
        "46": "46",
        "47": "47",
        "48": "48",
        "49": "49",
        "50": "50",

    }
    sizes = models.CharField(max_length=30, choices=SIZES, blank=True, null=True)

    def __str__(self):
        return f"{self.sizes}"

    
class Product(models.Model):

    

    vendor = models.ForeignKey(BecomeAVendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    price = models.IntegerField()
    discount = models.IntegerField(help_text="in %", blank=True, null=True)
    stock = models.PositiveIntegerField()
    image = ResizedImageField(size=[600, 500], quality=100, crop=['middle', 'center'], upload_to='products') 
    image_2 = ResizedImageField(size=[600, 500], quality=100, crop=['middle', 'center'], upload_to='products', blank=True, null=True) 
    image_3 = ResizedImageField(size=[600, 500], quality=100, crop=['middle', 'center'], upload_to='products', blank=True, null=True) 
    image_4 = ResizedImageField(size=[600, 500], quality=100, crop=['middle', 'center'], upload_to='products', blank=True, null=True) 
    sizes = models.ManyToManyField(Size)
    colours = models.ManyToManyField(Colour)
    description = models.TextField()  
    return_policy = models.TextField()
    refund_policy = models.TextField()
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    slug = models.SlugField(null=True, blank=True)
    

    def save(self, *args, **kwargs):
        # Save the product instance first to generate a primary key
        if not self.pk:  # Check if the instance is new
            self.slug = slugify(f"{self.vendor}-{self.name}")
            super().save(*args, **kwargs)

        # Now calculate the avg_rating only if there are ratings
        ratings = self.ratings.aggregate(avg_rating=Avg('review_stars'))
        self.avg_rating = ratings['avg_rating'] if ratings['avg_rating'] is not None else 0

        # Save the instance again with the updated avg_rating
        super().save(*args, **kwargs)


    def discounted_price(self):
        # Ensure self.discount is not None, set it to 0 if it is
        discount = self.discount if self.discount is not None else 0
        return self.price - ((discount / 100) * self.price)

    def avg_rating_percentage(self):
        ratings = ProductRating.objects.filter(product=self)
        total_reviews = ratings.count()
        if total_reviews > 0:
            avg_rating = ratings.aggregate(avg_stars=Avg('review_stars'))['avg_stars']
            avg_rating_percentage = (avg_rating / 5) * 100
            return avg_rating_percentage
        return 0  # Return 0 if no reviews

    def total_reviews(self):
        return self.ratings.count()

    def __str__(self):
        return self.name
    


class VendorRating(models.Model):
    vendor = models.ForeignKey(BecomeAVendor, on_delete=models.CASCADE, related_name='vendor_ratings')
    review_stars = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    review = models.TextField()
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    avg_rating_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.review_stars:
            ratings = VendorRating.objects.filter(vendor=self.vendor)
            total_reviews = ratings.count()
            total_stars = ratings.aggregate(total=models.Sum('review_stars'))['total'] or 0
            total_reviews = ratings.count()

            if total_reviews > 0:
                avg_rating = total_stars / total_reviews
                avg_rating_percentage = (avg_rating / 5) * 100
            else:
                avg_rating = 0
                avg_rating_percentage = 0

            self.total_reviews = total_reviews
            self.avg_rating = avg_rating
            self.avg_rating_percentage = avg_rating_percentage
        super().save(*args, **kwargs)

    def percentage(self):
        percentage = (self.review_stars / 5) * 100
        return percentage

@receiver(post_save, sender=VendorRating)
@receiver(post_delete, sender=VendorRating)
def update_vendor_avg_rating(sender, instance, **kwargs):
    vendor = instance.vendor
    avg_rating = vendor.vendor_ratings.aggregate(avg=Avg('review_stars'))['avg'] or 0
    vendor.avg_rating = avg_rating
    vendor.save()

class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    review_stars = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    review = models.TextField()
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    avg_rating_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)


    def stars(self):
        stars = (self.review_stars / 5) * 100
        stars = int(stars)
        return stars

    def save(self, *args, **kwargs):
        if self.review_stars:
            ratings = ProductRating.objects.filter(product=self.product)
            total_reviews = ratings.count()
            total_stars = ratings.aggregate(total=models.Sum('review_stars'))['total'] or 0
            total_reviews = ratings.count()

            if total_reviews > 0:
                avg_rating = total_stars / total_reviews
                avg_rating_percentage = (avg_rating / 5) * 100
            else:
                avg_rating = 0
                avg_rating_percentage = 0

            self.total_reviews = total_reviews
            self.avg_rating = avg_rating
            self.avg_rating_percentage = avg_rating_percentage
        super().save(*args, **kwargs)

@receiver(post_save, sender=ProductRating)
@receiver(post_delete, sender=ProductRating)
def update_product_avg_rating(sender, instance, **kwargs):
    product = instance.product
    avg_rating = product.ratings.aggregate(avg=Avg('review_stars'))['avg'] or 0
    product.avg_rating = avg_rating
    product.save()

class ContactVendor(models.Model):
    vendor = models.ForeignKey(BecomeAVendor, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254)
    name = models.CharField(max_length=150)
    message = models.TextField()


class OrderItem(models.Model):
    vendor = models.ForeignKey(BecomeAVendor, verbose_name=("vendor"), on_delete=models.SET_NULL, blank=True, null=True )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    colour = models.ForeignKey(Colour, on_delete=models.SET_NULL, blank=True, null=True )
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, blank=True, null=True )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} | {self.user.username} | quantity : {self.quantity} | {self.colour.color} | {self.size}"

    def prod(self):
        if self.product.discount:
            discount = self.product.price - ((self.product.discount / 100) * self.product.price)
            prod = discount * self.quantity
        else:
            prod = self.product.price * self.quantity 
        return prod



class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} | {self.user.username} | quantity : {self.quantity}"

    def prod(self):
        if self.product.discount:
            discount = self.product.price - ((self.product.discount / 100) * self.product.price)
            prod = discount * self.quantity
        else:
            prod = self.product.price * self.quantity 
        return prod

class Address(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone_number = PhoneNumberField()
    email = models.EmailField(max_length=254)
    order_notes = models.TextField(null=True, blank=True)

 

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.user}| {self.address} | {self.state}"
    


class Orders(models.Model):
    vendor = models.ForeignKey(BecomeAVendor, verbose_name="vendor", on_delete=models.SET_NULL, blank=True, null=True)
    slug = models.SlugField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_number = models.CharField(max_length=50)
    order_item = models.ManyToManyField("OrderItem")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    vendor_accepted = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    delivered_on = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=False, auto_now=False)
    total = models.PositiveIntegerField(blank=True, null=True)
    canceled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Ensure the slug is generated only when ref_number exists
        if not self.slug and self.ref_number:
            self.slug = slugify(self.ref_number)

        # Save the instance first (needed for accessing many-to-many fields)
        super().save(*args, **kwargs)

        # Recalculate the total based on order items
        total = 0
        for order_item in self.order_item.all():
            total += order_item.prod()
        
        # Update the total only if it has changed (to avoid infinite save loop)
        if self.total != total:
            self.total = total
            super().save(update_fields=["total"])  # Save only the total field

    class Meta:
        verbose_name_plural = "Orders"

    def get_total(self):
        total = 0
        for order_item in self.order_item.all():
            total += order_item.prod()
        return total


class Payments(models.Model):
    order = models.ForeignKey("Orders", on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    sub_account_ID = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return f"Payment: ₦{self.amount}  "

    def amount_value(self):
        return int(self.amount) * 100

    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
            self.save()
        if self.verified:
            return True
        return False

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payments.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref

        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Payments'