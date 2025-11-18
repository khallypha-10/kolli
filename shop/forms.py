from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . models import BecomeAVendor, Product, Colour, ContactVendor, ProductRating, Address, VendorRating



class SignupForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'First Name *'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Last Name *'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email *'}))
    phone_number = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number *'}))
    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'phone_number', 'username', 'email', 'password1', 'password2']


    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class']= 'form-control'
        self.fields['password1'].widget.attrs['class']= 'form-control'
        self.fields['password2'].widget.attrs['class']= 'form-control'
        self.fields['username'].widget.attrs['placeholder']= 'Username *'
        self.fields['password1'].widget.attrs['placeholder']= 'Password *'
        self.fields['password2'].widget.attrs['placeholder']= 'Password Again *'


class BecomeAVendorForm(ModelForm):
    class Meta:
        model = BecomeAVendor
        exclude = ['approved', 'user', 'sub_account_ID']

    def __init__(self, *args, **kwargs):
        super(BecomeAVendorForm, self).__init__(*args, **kwargs)

        self.fields['company_name'].widget.attrs['class']= 'form-control'
        self.fields['company_email'].widget.attrs['class']= 'form-control'
        self.fields['company_phone_number'].widget.attrs['class']= 'form-control'
        self.fields['company_state'].widget.attrs.update({
            'class': 'form-control',
            'aria-label': 'Select state'
        })
        self.fields['company_address'].widget.attrs['class']= 'form-control'
        self.fields['company_cac'].widget.attrs['class']= 'form-control'
        self.fields['company_logo'].widget.attrs['class']= 'form-control'
        self.fields['company_category'].widget.attrs['class']= 'form-control'
        self.fields['company_description'].widget.attrs['class']= 'form-control'
        self.fields['company_account_name'].widget.attrs['class']= 'form-control'
        self.fields['company_bank'].widget.attrs['class']= 'form-control'
        self.fields['company_account_number'].widget.attrs['class']= 'form-control'

        self.fields['company_name'].widget.attrs['placeholder']= 'Company Name *'
        self.fields['company_email'].widget.attrs['placeholder']= 'Company Email *'
        self.fields['company_phone_number'].widget.attrs['placeholder']= 'Company Phone Number *'
        self.fields['company_state'].widget.attrs['placeholder']=  'State Located *'
        self.fields['company_address'].widget.attrs['placeholder']= 'Company Address *'
        self.fields['company_cac'].widget.attrs['placeholder']= 'Company CAC Certificate *'
        self.fields['company_logo'].widget.attrs['placeholder']= 'Company Logo *'
        self.fields['company_category'].widget.attrs['placeholder']= 'Company Category *'
        self.fields['company_description'].widget.attrs['placeholder']= 'Company Description *'
        self.fields['company_account_name'].widget.attrs['placeholder']= 'Company Bank Account Name *'
        self.fields['company_bank'].widget.attrs['placeholder']= 'Company Bank *'
        self.fields['company_account_number'].widget.attrs['placeholder']= 'Company Account Number *'


class ProductForm(ModelForm):
    
    class Meta:
        model = Product
        exclude = ['vendor', 'slug']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        self.fields['colours'].queryset = Colour.objects.all()  # Ensure queryset is populated

        self.fields['name'].widget.attrs['class']= 'form-control'
        self.fields['price'].widget.attrs['class']= 'form-control'
        self.fields['discount'].widget.attrs['class']= 'form-control'
        self.fields['stock'].widget.attrs['class']= 'form-control'
        self.fields['image'].widget.attrs['class']= 'form-control'
        self.fields['image_2'].widget.attrs['class']= 'form-control'
        self.fields['image_3'].widget.attrs['class']= 'form-control'
        self.fields['image_4'].widget.attrs['class']= 'form-control'
        self.fields['sizes'].widget.attrs.update({'class': 'form-select', 'multiple': 'multiple'})
        self.fields['description'].widget.attrs['class']= 'form-control'
        self.fields['colours'].widget.attrs.update({'class': 'form-select','multiple': 'multiple'})


        
        self.fields['discount'].widget.attrs['placeholder']= 'if None, leave blank '
        self.fields['stock'].widget.attrs['placeholder']= 'Amount available '

    def save(self, commit=True):
        product = super(ProductForm, self).save(commit=False)
        if commit:
            product.save()  # Save the main product object
            self.save_m2m()  # Save the many-to-many data (colours)
        return product
        

class ContactVendorForm(ModelForm):
    class Meta:
        model = ContactVendor
        exclude = ['vendor']

    def __init__(self, *args, **kwargs):
        super(ContactVendorForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class']= 'form-control'
        self.fields['email'].widget.attrs['class']= 'form-control'
        self.fields['message'].widget.attrs['class']= 'form-control'

        self.fields['name'].widget.attrs['placeholder']= 'Your Name'
        self.fields['email'].widget.attrs['placeholder']= 'Your Email '
        self.fields['message'].widget.attrs['placeholder']= 'Your Message '

class ProductRatingForm(ModelForm):
    class Meta:
        model = ProductRating
        exclude = ['product']

    def __init__(self, *args, **kwargs):
        super(ProductRatingForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class']= 'form-control'
        self.fields['email'].widget.attrs['class']= 'form-control'
        self.fields['review'].widget.attrs['class']= 'form-control'
        self.fields['review_stars'].widget.attrs.update({'class' : 'visually-hidden', 'type': 'hidden','id': 'rating'})

        self.fields['name'].widget.attrs['placeholder']= 'Your Name *'
        self.fields['email'].widget.attrs['placeholder']= 'Your Email *'
        self.fields['review'].widget.attrs['placeholder']= 'Write Your Review Here... *'

class VendorRatingForm(ModelForm):
    class Meta:
        model = VendorRating
        exclude = ['vendor']

    def __init__(self, *args, **kwargs):
        super(VendorRatingForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class']= 'form-control'
        self.fields['email'].widget.attrs['class']= 'form-control'
        self.fields['review'].widget.attrs['class']= 'form-control'
        self.fields['review_stars'].widget.attrs.update({'class' : 'visually-hidden', 'type': 'hidden','id': 'rating'})

        self.fields['name'].widget.attrs['placeholder']= 'Your Name *'
        self.fields['email'].widget.attrs['placeholder']= 'Your Email *'
        self.fields['review'].widget.attrs['placeholder']= 'Write Your Review Here... *'


class AddressForm(ModelForm):

    class Meta:
        model = Address 
        exclude = ['user']

    def __init__(self, *args, **kwargs):
            super(AddressForm, self).__init__(*args, **kwargs)

            self.fields['state'].widget.attrs['class']= 'form-control form-control-md'
            self.fields['address'].widget.attrs['class']= 'form-control form-control-md mb-2'
            self.fields['city'].widget.attrs['class']= 'form-control form-control-md'
            self.fields['phone_number'].widget.attrs['class']= 'form-control form-control-md'
            self.fields['email'].widget.attrs['class']= 'form-control form-control-md'
            self.fields['first_name'].widget.attrs['class']= 'form-control form-control-md'
            self.fields['last_name'].widget.attrs['class']= 'form-control form-control-md'
            self.fields['order_notes'].widget.attrs['class']= 'form-control mb-0'

            self.fields['address'].widget.attrs['placeholder']= 'House number and street name*'
            self.fields['state'].widget.attrs['placeholder']= 'FCT-Abuja '
            self.fields['city'].widget.attrs['placeholder']= 'Abuja '
            self.fields['email'].widget.attrs['placeholder']= 'user@email.com '
            self.fields['first_name'].widget.attrs['placeholder']= 'John '
            self.fields['last_name'].widget.attrs['placeholder']= 'Doe '
            self.fields['phone_number'].widget.attrs['placeholder']= '+234 80 2345678 '
            self.fields['order_notes'].widget.attrs['placeholder']= 'Notes about your order, e.g special notes for delivery '