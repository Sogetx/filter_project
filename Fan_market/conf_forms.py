from django import forms
from .models import Dust

class ConfForm(forms.Form):
    particle_size = forms.ChoiceField(
        label="Розмір часток, мкм:",
        choices=[
            ("40-999", "40 ÷ 1000"),
            ("20-999", "20 ÷ 1000"),
            ("5-999",  "5 ÷ 1000"),
            ("0.01-10",  "0.01 ÷ 10"),
            # Додайте інші опції за потребою
        ]
    )

    cleaning_efficiency = forms.ChoiceField(
        label="Ефективність очищення, %:",
        choices=[
            ("50", "50"),
            ("60", "60"),
            ("70", "70"),
            ("80", "80"),
            ("95", "95"),
            # Додайте інші опції за потребою
        ]
    )

    temperature = forms.ChoiceField(
        label="Температура, С:",
        choices=[
            ("50", "50 С"),
            ("100", "100 С"),
            ("200", "200 С"),
            ("500", "500 С"),
            # Додайте інші опції за потребою
        ]
    )

    concentration = forms.ChoiceField(
        label="Концентрація пилу на вході, г/м3:",
        choices=[
            ("15", "15"),
            ("50", "50"),
            ("200", "200"),
            ("300", "300"),
            # Додайте інші опції за потребою
        ]
    )

    dusts = forms.MultipleChoiceField(
        label="Тип пилу:",
        choices=[(dust.id, dust.name) for dust in Dust.objects.all()],
        widget=forms.CheckboxSelectMultiple
    )
