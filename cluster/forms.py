from django import forms
from django.contrib.auth.forms import UserCreationForm

from dash.cluster.models import ClusterTemplate, Disk, AwsCredential
import dash.ec2utils

class ClusterTemplateForm(forms.ModelForm):
    class Meta:
        model = ClusterTemplate
        fields = [ 'name', 'number_of_nodes', 'type_of_nodes', 'is_demo' ]


class DiskForm(forms.ModelForm):
    class Meta:
        model = Disk
        fields = [ 'size', ]

class ClusterUserCreationForm(UserCreationForm):
    email_address = forms.EmailField()

class AwsCredentialForm(forms.ModelForm):
    class Meta:
        model = AwsCredential
        fields = [
                'aws_user_id',
                'aws_key_id',
                'aws_secret_key',
                ]
        widgets = {
                'aws_secret_key': forms.PasswordInput(),
                }

    def clean(self):
        """This tests to see if the AWS Credentials are valid"""
        super(AwsCredentialForm, self).clean()
        cleaned_data = self.cleaned_data
        if 'aws_key_id' in cleaned_data and 'aws_secret_key' in cleaned_data:
            aws_key_id = cleaned_data['aws_key_id']
            aws_secret_key = cleaned_data['aws_secret_key']

            if dash.ec2utils.valid_aws_credentials(
                    aws_key_id,
                    aws_secret_key
                    ):
                return self.cleaned_data
            else:
                raise forms.ValidationError("Invalid AWS Key ID or Secret Key.  Please check your AWS credentials.")
        else:
            raise forms.ValidationError("Missing AWS Key ID or Secret Key")
