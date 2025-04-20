from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CustomUser, Grievance, Category, Status, GrievanceAttachment, ForumDiscussion, ForumReply

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone_number", "address", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data.get("phone_number", "")
        user.address = self.cleaned_data.get("address", "")
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class GrievanceForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        help_text='You can upload multiple images (JPG, PNG, GIF)'
    )
    location = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter location or click on the map',
            'class': 'form-control'
        })
    )
    latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )
    is_anonymous = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Submit anonymously'
    )

    class Meta:
        model = Grievance
        fields = ['title', 'description', 'location', 'image', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_anonymous': 'Submit anonymously',
        }

class GrievanceSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search grievances...',
            'class': 'form-control'
        })
    )

class UserRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
        return user

class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search grievances by title...',
            'aria-label': 'Search',
            'name': 'query'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'query' in self.data:
            self.fields['query'].initial = self.data['query']

class ForumDiscussionForm(forms.ModelForm):
    class Meta:
        model = ForumDiscussion
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discussion title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your discussion content',
                'rows': 5
            })
        }

class ForumReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your reply',
                'rows': 3
            })
        } 