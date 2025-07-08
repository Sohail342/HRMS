from django import forms
from django.utils.html import format_html

class RequiredOptionalFieldsModelForm(forms.ModelForm):
    """
    A custom ModelForm that adds visual indicators for required and optional fields.
    This form automatically adds appropriate CSS classes and help text to fields
    based on their required status.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Process each field to add required/optional indicators
        for field_name, field in self.fields.items():
            # Get the original label
            original_label = field.label or field_name.replace('_', ' ').capitalize()
            
            # Add visual indicators based on required status
            if field.required:
                # Add required indicator
                field.label = format_html(
                    '<span class="required-field-label">{} <span class="required-indicator">*</span></span>',
                    original_label
                )
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' required-field'
                field.widget.attrs['data-required'] = 'true'
            else:
                # Add optional indicator
                field.label = format_html(
                    '<span class="optional-field-label">{} <span class="optional-indicator">(optional)</span></span>',
                    original_label
                )
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' optional-field'
                field.widget.attrs['data-required'] = 'false'
            
            # Add description as data attribute if help_text is available
            if field.help_text:
                field.widget.attrs['data-description'] = field.help_text