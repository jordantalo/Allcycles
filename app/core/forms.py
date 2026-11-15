from django import forms
from .models import OrderItem, Order

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ["last_name", "first_name", "email"]


    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            return first_name.strip().capitalize()
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            return last_name.strip().upper()
        return last_name

class OrderItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        self.fields["size"].required = False

    class Meta:
        model = OrderItem
        fields = ["quantity", "size"]

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        size = cleaned_data.get('size')

        if quantity is not None:

            if (quantity < 0):
                self.add_error('quantity', "Une quantité ne peut pas être négative")

            if (quantity > 0 and not size):
                self.add_error('size', "La taille doit obligatoirement être renseignée")

        else:
            self.add_error('quantity', "Une quantité doit obligatoirement être renseignée (Mettre 0 si vous ne souhaitez pas pré commander cet article)")

        return cleaned_data
