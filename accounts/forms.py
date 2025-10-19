from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import formset_factory, modelformset_factory
from django_summernote.widgets import SummernoteWidget
from .models import User, Receipt, ReceiptEditRequest, ReceiptEditRequestItem, ReceiptItem, Role, Department


class LoginForm(AuthenticationForm):
    """Custom login form with Thai ID validation"""
    
    username = forms.CharField(
        max_length=50,  # เพิ่มขนาดให้รองรับ admin users
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'ldap_uid',
            'placeholder': 'รหัสบัตรประชาชน 13 หลัก / รหัสนักศึกษา 12 หลัก',
            'required': True,
        }),
        label='รหัสบัตรประชาชน / รหัสนักศึกษา'
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

        # Validate format (must be digits)
        if not username.isdigit():
            raise forms.ValidationError('รหัสต้องเป็นตัวเลขเท่านั้น (12 หลักสำหรับนักศึกษา หรือ 13 หลักสำหรับเจ้าหน้าที่)')

        # Accept both 12 digits (student) and 13 digits (staff)
        if len(username) not in [12, 13]:
            raise forms.ValidationError('รหัสต้องเป็น 12 หลัก (นักศึกษา) หรือ 13 หลัก (เจ้าหน้าที่)')

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


# ===== MANUAL USER CREATION FORMS =====

class ManualStaffCreateForm(forms.ModelForm):
    """ฟอร์มสร้างเจ้าหน้าที่แบบ Manual (สำหรับ superuser เท่านั้น)"""

    username = forms.CharField(
        label='Username (ชื่อผู้ใช้)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'เช่น staff_somchai, admin_finance (ถ้าไม่มีรหัสบัตรประชาชน)',
        }),
        help_text='ระบุ Username ถ้าไม่มีรหัสบัตรประชาชน (ต้องไม่ซ้ำในระบบ)'
    )

    password1 = forms.CharField(
        label='รหัสผ่าน',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'ตั้งรหัสผ่านเริ่มต้น (อย่างน้อย 8 ตัวอักษร)',
            'required': True
        }),
        help_text='ตั้งรหัสผ่านเริ่มต้นให้ผู้ใช้ (ควรแจ้งให้ผู้ใช้เปลี่ยนรหัสผ่านทันทีหลังเข้าระบบครั้งแรก)'
    )

    password2 = forms.CharField(
        label='ยืนยันรหัสผ่าน',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'ยืนยันรหัสผ่านอีกครั้ง',
            'required': True
        })
    )

    department_select = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=True,
        empty_label='-- เลือกหน่วยงาน/คณะ --',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='หน่วยงาน/คณะ *',
        help_text='เลือกหน่วยงาน/คณะที่ผู้ใช้สังกัด'
    )

    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='บทบาท',
        help_text='เลือกบทบาทที่ต้องการกำหนดให้ผู้ใช้'
    )

    class Meta:
        model = User
        fields = [
            'ldap_uid', 'prefix_name', 'first_name_th', 'last_name_th',
            'full_name', 'birth_date', 'gender',
            'position_title', 'contact_email'
        ]
        widgets = {
            'ldap_uid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'รหัสบัตรประชาชน 13 หลัก (ไม่บังคับ)',
                'maxlength': '13'
            }),
            'prefix_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'นาย/นาง/นางสาว'
            }),
            'first_name_th': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อ (ภาษาไทย)',
                'required': True
            }),
            'last_name_th': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'นามสกุล (ภาษาไทย)',
                'required': True
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อ-นามสกุลเต็ม (เช่น นายสมชาย ใจดี)'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(
                choices=[('', 'เลือกเพศ'), ('ชาย', 'ชาย'), ('หญิง', 'หญิง')],
                attrs={'class': 'form-control'}
            ),
            'position_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ตำแหน่ง'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'อีเมล'
            })
        }
        labels = {
            'ldap_uid': 'รหัสบัตรประชาชน (ไม่บังคับ)',
            'prefix_name': 'คำนำหน้า',
            'first_name_th': 'ชื่อ (ภาษาไทย) *',
            'last_name_th': 'นามสกุล (ภาษาไทย) *',
            'full_name': 'ชื่อ-นามสกุลเต็ม',
            'birth_date': 'วันเกิด',
            'gender': 'เพศ',
            'position_title': 'ตำแหน่ง',
            'contact_email': 'อีเมล'
        }

    def clean_ldap_uid(self):
        ldap_uid = self.cleaned_data.get('ldap_uid')

        # Handle None or empty string
        if ldap_uid:
            ldap_uid = ldap_uid.strip()
        else:
            return ''  # Return empty string if None

        # If provided, validate format
        if ldap_uid:
            if not ldap_uid.isdigit():
                raise forms.ValidationError('รหัสบัตรประชาชนต้องเป็นตัวเลขเท่านั้น')

            if len(ldap_uid) != 13:
                raise forms.ValidationError('รหัสบัตรประชาชนต้องเป็น 13 หลัก')

            # Check uniqueness
            if User.objects.filter(ldap_uid=ldap_uid).exists():
                raise forms.ValidationError('รหัสบัตรประชาชนนี้มีอยู่ในระบบแล้ว')

        return ldap_uid

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Handle None or empty string
        if username:
            username = username.strip()
        else:
            return ''  # Return empty string if None

        if username:
            # Validate format (alphanumeric + underscore only)
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise forms.ValidationError('Username ต้องเป็นตัวอักษร ตัวเลข และ _ (underscore) เท่านั้น')

            # Check uniqueness
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Username นี้มีอยู่ในระบบแล้ว')

            # Minimum length
            if len(username) < 4:
                raise forms.ValidationError('Username ต้องมีอย่างน้อย 4 ตัวอักษร')

        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('รหัสผ่านไม่ตรงกัน')

        # Password strength validation
        if password1 and len(password1) < 8:
            raise forms.ValidationError('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร')

        return password2

    def clean(self):
        cleaned_data = super().clean()
        ldap_uid = cleaned_data.get('ldap_uid', '').strip() if cleaned_data.get('ldap_uid') else ''
        username = cleaned_data.get('username', '').strip() if cleaned_data.get('username') else ''

        # ต้องมี ldap_uid หรือ username อย่างน้อย 1 อย่าง
        if not ldap_uid and not username:
            raise forms.ValidationError('กรุณาระบุ รหัสบัตรประชาชน หรือ Username อย่างน้อย 1 อย่าง')

        # Auto-generate full_name if not provided
        if not cleaned_data.get('full_name'):
            prefix = cleaned_data.get('prefix_name', '')
            first_name = cleaned_data.get('first_name_th', '')
            last_name = cleaned_data.get('last_name_th', '')

            if prefix:
                cleaned_data['full_name'] = f"{prefix}{first_name} {last_name}"
            else:
                cleaned_data['full_name'] = f"{first_name} {last_name}"

        return cleaned_data


class ManualStudentCreateForm(forms.ModelForm):
    """ฟอร์มสร้างนักศึกษาแบบ Manual (สำหรับ superuser เท่านั้น)"""

    password1 = forms.CharField(
        label='รหัสผ่าน',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'ตั้งรหัสผ่านเริ่มต้น (อย่างน้อย 8 ตัวอักษร)',
            'required': True
        }),
        help_text='ตั้งรหัสผ่านเริ่มต้นให้นักศึกษา (ควรแจ้งให้นักศึกษาเปลี่ยนรหัสผ่านทันทีหลังเข้าระบบครั้งแรก)'
    )

    password2 = forms.CharField(
        label='ยืนยันรหัสผ่าน',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'ยืนยันรหัสผ่านอีกครั้ง',
            'required': True
        })
    )

    student_faculty_select = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=True,
        empty_label='-- เลือกคณะ --',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='คณะ *',
        help_text='เลือกคณะที่นักศึกษาสังกัด'
    )

    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='บทบาท',
        help_text='เลือกบทบาทที่ต้องการกำหนดให้นักศึกษา'
    )

    class Meta:
        model = User
        fields = [
            'student_code', 'prefix_name', 'first_name_th', 'last_name_th',
            'full_name', 'student_level', 'student_program',
            'student_degree', 'contact_email'
        ]
        widgets = {
            'student_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'รหัสนักศึกษา 12 หลัก',
                'maxlength': '12',
                'required': True
            }),
            'prefix_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'นาย/นาง/นางสาว'
            }),
            'first_name_th': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อ (ภาษาไทย)',
                'required': True
            }),
            'last_name_th': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'นามสกุล (ภาษาไทย)',
                'required': True
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อ-นามสกุลเต็ม (เช่น นายสมชาย ใจดี)'
            }),
            'student_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ระดับการศึกษา (เช่น ปริญญาตรี)'
            }),
            'student_program': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'สาขาวิชา'
            }),
            'student_degree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ระดับปริญญา (เช่น วิทยาศาสตรบัณฑิต)'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'อีเมล'
            })
        }
        labels = {
            'student_code': 'รหัสนักศึกษา *',
            'prefix_name': 'คำนำหน้า',
            'first_name_th': 'ชื่อ (ภาษาไทย) *',
            'last_name_th': 'นามสกุล (ภาษาไทย) *',
            'full_name': 'ชื่อ-นามสกุลเต็ม',
            'student_level': 'ระดับการศึกษา',
            'student_program': 'สาขาวิชา',
            'student_degree': 'ระดับปริญญา',
            'contact_email': 'อีเมล'
        }

    def clean_student_code(self):
        student_code = self.cleaned_data.get('student_code', '').strip()

        if not student_code:
            raise forms.ValidationError('กรุณาระบุรหัสนักศึกษา')

        if not student_code.isdigit():
            raise forms.ValidationError('รหัสนักศึกษาต้องเป็นตัวเลขเท่านั้น')

        if len(student_code) != 12:
            raise forms.ValidationError('รหัสนักศึกษาต้องเป็น 12 หลัก')

        # Check uniqueness
        if User.objects.filter(student_code=student_code).exists():
            raise forms.ValidationError('รหัสนักศึกษานี้มีอยู่ในระบบแล้ว')

        return student_code

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('รหัสผ่านไม่ตรงกัน')

        # Password strength validation
        if password1 and len(password1) < 8:
            raise forms.ValidationError('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร')

        return password2

    def clean(self):
        cleaned_data = super().clean()

        # Auto-generate full_name if not provided
        if not cleaned_data.get('full_name'):
            prefix = cleaned_data.get('prefix_name', '')
            first_name = cleaned_data.get('first_name_th', '')
            last_name = cleaned_data.get('last_name_th', '')

            if prefix:
                cleaned_data['full_name'] = f"{prefix}{first_name} {last_name}"
            else:
                cleaned_data['full_name'] = f"{first_name} {last_name}"

        return cleaned_data