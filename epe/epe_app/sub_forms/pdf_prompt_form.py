from django import forms

class PDFPromptForm(forms.Form):
    pdf_file = forms.FileField(label='Upload PDF')
    prompt = forms.CharField(label='Your Prompt', max_length=500)
