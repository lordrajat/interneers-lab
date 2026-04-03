from django import forms

from products.category_repository import CategoryRepository

class ProductAdminForm(forms.Form):
    name = forms.CharField(max_length=120)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))
    category_id = forms.ChoiceField()
    price = forms.DecimalField(min_value=0, decimal_places=2, max_digits=12)
    brand = forms.CharField(max_length=80)
    quantity = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = CategoryRepository().list_all()
        self.fields["category_id"].choices = [
            (str(category.id), category.title) for category in categories
        ]
