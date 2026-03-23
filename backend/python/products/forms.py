from django import forms


class ProductAdminForm(forms.Form):
    name = forms.CharField(max_length=120)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))
    category = forms.CharField(max_length=80)
    price = forms.DecimalField(min_value=0, decimal_places=2, max_digits=12)
    brand = forms.CharField(max_length=80)
    quantity = forms.IntegerField(min_value=0)
