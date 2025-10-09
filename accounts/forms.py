from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import formset_factory, modelformset_factory
from django_summernote.widgets import SummernoteWidget
from .models import User, Receipt, ReceiptEditRequest, ReceiptEditRequestItem, ReceiptItem


class LoginForm(AuthenticationForm):
    """Custom login form with Thai ID validation"""
    
    username = forms.CharField(
        max_length=50,  # เพิ่มขนาดให้รองรับ admin users
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'ldap_uid',
            'placeholder': 'กรอกรหัสบัตรประชาชน 13 หลัก หรือ username สำหรับ admin',
            'required': True,
        }),
        label='รหัสบัตรประชาชน / Username'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'password',
            'placeholder': 'กรอกรหัสผ่าน',
            'required': True,
        }),
        label='รหัสผ่าน'
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        
        # Skip validation for admin users (allow alphanumeric)
        admin_usernames = ['admin', 'superuser', 'admin_e', 'administrator']
        if username in admin_usernames or username.startswith('admin'):
            return username
        
        # Validate Thai ID format (13 digits) for regular users
        if not username.isdigit():
            raise forms.ValidationError('รหัสบัตรประชาชนต้องเป็นตัวเลข 13 หลัก และรหัสผ่านของคุณ')
        
        if len(username) != 13:
            raise forms.ValidationError('รหัสบัตรประชาชนต้องเป็นตัวเลข 13 หลัก และรหัสผ่านของคุณ')
        
        return username


# ===== EDIT REQUEST FORMS =====

class ReceiptEditRequestForm(forms.ModelForm):
    """ฟอร์มสำหรับส่งคำร้องขอแก้ไขใบสำคัญรับเงิน"""
    
    class Meta:
        model = ReceiptEditRequest
        fields = [
            'reason', 'description',
            'new_recipient_name', 'new_recipient_address', 
            'new_recipient_postal_code', 'new_recipient_id_card',
            'new_receipt_date', 'new_total_amount_text'
        ]
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'กรุณาระบุเหตุผลในการขอแก้ไขใบสำคัญรับเงิน',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'อธิบายรายละเอียดการแก้ไขที่ต้องการ (ถ้ามี)'
            }),
            'new_recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อผู้รับเงินใหม่ (หากต้องการแก้ไข)'
            }),
            'new_recipient_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ที่อยู่ผู้รับเงินใหม่ (หากต้องการแก้ไข)'
            }),
            'new_recipient_postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'รหัสไปรษณีย์ใหม่ (หากต้องการแก้ไข)'
            }),
            'new_recipient_id_card': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'เลขบัตรประชาชนใหม่ (หากต้องการแก้ไข)'
            }),
            'new_receipt_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'new_total_amount_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'จำนวนเงินตัวหนังสือใหม่ (หากต้องการแก้ไข)'
            })
        }
        labels = {
            'reason': 'เหตุผลในการขอแก้ไข *',
            'description': 'รายละเอียดการแก้ไข',
            'new_recipient_name': 'ชื่อผู้รับเงินใหม่',
            'new_recipient_address': 'ที่อยู่ผู้รับเงินใหม่',
            'new_recipient_postal_code': 'รหัสไปรษณีย์ใหม่',
            'new_recipient_id_card': 'เลขบัตรประชาชนใหม่',
            'new_receipt_date': 'วันที่ในใบสำคัญใหม่',
            'new_total_amount_text': 'จำนวนเงินตัวหนังสือใหม่'
        }
    
    def __init__(self, *args, **kwargs):
        self.receipt = kwargs.pop('receipt', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill current values as placeholders
        if self.receipt:
            self.fields['new_recipient_name'].widget.attrs['placeholder'] = f"ปัจจุบัน: {self.receipt.recipient_name}"
            self.fields['new_recipient_address'].widget.attrs['placeholder'] = f"ปัจจุบัน: {self.receipt.recipient_address}"
            self.fields['new_recipient_postal_code'].widget.attrs['placeholder'] = f"ปัจจุบัน: {self.receipt.recipient_postal_code}"
            self.fields['new_recipient_id_card'].widget.attrs['placeholder'] = f"ปัจจุบัน: {self.receipt.recipient_id_card}"
            self.fields['new_total_amount_text'].widget.attrs['placeholder'] = f"ปัจจุบัน: {self.receipt.total_amount_text}"
    
    def clean(self):
        cleaned_data = super().clean()
        
        # ตรวจสอบว่ามีการแก้ไขอย่างน้อย 1 field
        fields_to_check = [
            'new_recipient_name', 'new_recipient_address', 
            'new_recipient_postal_code', 'new_recipient_id_card',
            'new_receipt_date', 'new_total_amount_text'
        ]
        
        has_changes = any(cleaned_data.get(field) for field in fields_to_check)
        
        if not has_changes:
            raise forms.ValidationError(
                'กรุณาระบุข้อมูลที่ต้องการแก้ไขอย่างน้อย 1 รายการ'
            )
        
        return cleaned_data


class ReceiptEditRequestItemForm(forms.ModelForm):
    """ฟอร์มสำหรับแก้ไขรายการใบสำคัญรับเงิน"""
    
    class Meta:
        model = ReceiptEditRequestItem
        fields = ['action', 'new_description', 'new_amount', 'new_order']
        widgets = {
            'action': forms.Select(attrs={
                'class': 'form-select'
            }),
            'new_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'รายการใหม่'
            }),
            'new_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'new_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '1'
            })
        }
        labels = {
            'action': 'การดำเนินการ',
            'new_description': 'รายการ',
            'new_amount': 'จำนวนเงิน',
            'new_order': 'ลำดับ'
        }
    
    def clean_new_amount(self):
        amount = self.cleaned_data.get('new_amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError('จำนวนเงินต้องมากกว่าหรือเท่ากับ 0')
        return amount


class EditRequestApprovalForm(forms.Form):
    """ฟอร์มสำหรับอนุมัติ/ปฏิเสธคำร้องขอแก้ไข"""
    
    APPROVAL_CHOICES = [
        ('approve', 'อนุมัติ'),
        ('reject', 'ปฏิเสธ'),
    ]
    
    action = forms.ChoiceField(
        choices=APPROVAL_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='การตัดสินใจ'
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'หมายเหตุ (ถ้ามี)'
        }),
        label='หมายเหตุ',
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        notes = cleaned_data.get('notes')
        
        # ถ้าปฏิเสธต้องมีหมายเหตุ
        if action == 'reject' and not notes:
            raise forms.ValidationError('กรุณาระบุเหตุผลในการปฏิเสธ')
        
        return cleaned_data


# ===== FORMSETS FOR MULTIPLE ITEMS =====

# Formset for editing receipt items
class ReceiptItemEditForm(forms.ModelForm):
    """ฟอร์มสำหรับแก้ไขรายการสินค้าในใบสำคัญ"""
    
    # Add quantity field manually since original model doesn't have it
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control item-quantity',
            'min': '1',
            'step': '1'
        })
    )
    
    unit_price = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control item-unit-price',
            'min': '0',
            'step': '0.01'
        })
    )
    
    class Meta:
        model = ReceiptItem
        fields = ['description']
        widgets = {
            'description': SummernoteWidget(attrs={
                'summernote': {
                    'width': '100%',
                    'height': '200',
                    'toolbar': [
                        ['style', ['bold', 'italic', 'underline', 'clear']],
                        ['font', ['strikethrough']],
                        ['fontsize', ['fontsize']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['height', ['height']],
                    ],
                }
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing item, pre-fill quantity and unit_price from amount
        if self.instance and self.instance.pk:
            # Assume quantity = 1 and unit_price = amount for existing items
            self.fields['quantity'].initial = 1
            self.fields['unit_price'].initial = self.instance.amount

ReceiptEditRequestItemFormSet = modelformset_factory(
    ReceiptItem,
    form=ReceiptItemEditForm,
    extra=0,
    can_delete=True
)