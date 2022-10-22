from django.contrib.admin import AdminSite

from main_app.models import User, Session, Metric, MetricValue, Prediction

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

AdminSite.index_title = 'Aviahackathon (RealityX) administration'
AdminSite.site_title = 'RealityX'
AdminSite.site_header = 'RealityX'


class UserCreationForm(forms.ModelForm):
    """
        A form for creating new users.
        Includes all the required fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
        A form for updating users.
        Includes all the fields of the user, but replaces the password field with password's hash readonly field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_superuser')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'id', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_superuser', 'is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class PredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'flight_phase', 'flight_datetime', 'engine_id', 'session')
    list_filter = ('flight_phase',)
    search_fields = ['id', 'engine_id']


class MetricValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'metric_name', 'prediction')
    list_filter = ('metric_name',)
    search_fields = ['id', 'value']


admin.site.register(User, UserAdmin)
admin.site.register(Session)
admin.site.register(Prediction, PredictionAdmin)
admin.site.register(Metric)
admin.site.register(MetricValue, MetricValueAdmin)
admin.site.unregister(Group)
