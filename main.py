import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

class InventoryPOSApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=8, **kwargs)

        # قاعدة بيانات مصغرة داخل الذاكرة للمخزون
        self.inventory = {
            "سكر": {"qty": 50, "price": 10.0},
            "أرز": {"qty": 30, "price": 25.0},
            "زيت": {"qty": 20, "price": 15.0}
        }
        self.cart = {}

        # 1. شريط العنوان
        self.add_widget(Label(
            text="نظام إدارة المخازن والفواتير",
            font_size="20sp",
            size_hint_y=None,
            height=40
        ))

        # 2. منطقة الإدخال لإضافة/تحديث صنف
        input_layout = BoxLayout(size_hint_y=None, height=45, spacing=5)
        self.name_input = TextInput(hint_text="اسم المنتج", multiline=False)
        self.qty_input = TextInput(hint_text="الكمية", multiline=False, input_filter='int')
        self.price_input = TextInput(hint_text="السعر", multiline=False, input_filter='float')
        add_btn = Button(text="حفظ بالصنف", size_hint_x=0.8, on_press=self.add_or_update_product)

        input_layout.add_widget(self.name_input)
        input_layout.add_widget(self.qty_input)
        input_layout.add_widget(self.price_input)
        input_layout.add_widget(add_btn)
        self.add_widget(input_layout)

        # 3. شاشة عرض المخزون والسلة
        scroll = ScrollView(size_hint=(1, 1))
        self.display_label = Label(
            text="",
            size_hint_y=None,
            font_size="14sp",
            halign="left",
            valign="top"
        )
        self.display_label.bind(texture_size=self.display_label.setter('size'))
        scroll.add_widget(self.display_label)
        self.add_widget(scroll)

        # 4. أزرار البيع وإصدار الفاتورة
        action_layout = BoxLayout(size_hint_y=None, height=45, spacing=5)
        sell_btn = Button(text="إضافة للسلة", on_press=self.add_to_cart)
        invoice_btn = Button(text="طباعة الفاتورة وحفظها", on_press=self.generate_invoice)
        clear_btn = Button(text="تفريغ السلة", on_press=self.clear_cart)

        action_layout.add_widget(sell_btn)
        action_layout.add_widget(invoice_btn)
        action_layout.add_widget(clear_btn)
        self.add_widget(action_layout)

        # رسالة التنبيهات
        self.status_label = Label(
            text="جاهز للعمل",
            size_hint_y=None,
            height=30,
            color=(0.3, 0.9, 0.3, 1)
        )
        self.add_widget(self.status_label)

        self.update_display()

    def update_display(self):
        content = "=== المخزون الحالي ===\n"
        for item, data in self.inventory.items():
            content += f"• {item} | الكمية: {data['qty']} | السعر: {data['price']}\n"
        
        content += "\n=== السلة الحالية ===\n"
        total = 0.0
        if not self.cart:
            content += "(السلة فارغة)\n"
        else:
            for item, info in self.cart.items():
                subtotal = info['qty'] * info['price']
                total += subtotal
                content += f"• {item} × {info['qty']} = {subtotal}\n"
            content += f"الإجمالي الكلي: {total}\n"

        self.display_label.text = content

    def add_or_update_product(self, instance):
        name = self.name_input.text.strip()
        qty = self.qty_input.text.strip()
        price = self.price_input.text.strip()

        if not name or not qty or not price:
            self.status_label.text = "يرجى ملء كافة حقول الصنف"
            return

        self.inventory[name] = {"qty": int(qty), "price": float(price)}
        self.status_label.text = f"تم حفظ الصنف: {name}"
        self.name_input.text = ""
        self.qty_input.text = ""
        self.price_input.text = ""
        self.update_display()

    def add_to_cart(self, instance):
        name = self.name_input.text.strip()
        qty_str = self.qty_input.text.strip()

        if not name or not qty_str:
            self.status_label.text = "اكتب اسم المنتج والكمية لإضافته للسلة"
            return

        qty = int(qty_str)
        if name not in self.inventory:
            self.status_label.text = "المنتج غير موجود في المخزن"
            return

        if self.inventory[name]["qty"] < qty:
            self.status_label.text = "الكمية المطلوبة أكبر من المتوفر بالمخزن"
            return

        # إضافة إلى السلة
        if name in self.cart:
            self.cart[name]["qty"] += qty
        else:
            self.cart[name] = {"qty": qty, "price": self.inventory[name]["price"]}

        self.status_label.text = f"تمت إضافة {name} إلى السلة"
        self.update_display()

    def clear_cart(self, instance):
        self.cart.clear()
        self.status_label.text = "تم تفريغ السلة"
        self.update_display()

    def generate_invoice(self, instance):
        if not self.cart:
            self.status_label.text = "السلة فارغة، لا يمكن إصدار فاتورة"
            return

        # خصم الكميات من المخزون
        for item, data in self.cart.items():
            self.inventory[item]["qty"] -= data["qty"]

        # إعداد نص الفاتورة للطباعة
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        invoice_lines = [
            "--------------------------------",
            "         فاتورة مبيعات          ",
            f"التاريخ: {now}",
            "--------------------------------",
            "الصنف         الكمية    السعر    الإجمالي"
        ]

        total = 0.0
        for item, data in self.cart.items():
            subtotal = data["qty"] * data["price"]
            total += subtotal
            invoice_lines.append(f"{item:<12} {data['qty']:<8} {data['price']:<8} {subtotal:<8}")

        invoice_lines.extend([
            "--------------------------------",
            f"المبلغ الإجمالي: {total}",
            "--------------------------------",
            "شكراً لتعاملكم معنا!\n"
        ])

        invoice_text = "\n".join(invoice_lines)

        # حفظ الفاتورة كملف نصي
        filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(invoice_text)

        self.cart.clear()
        self.update_display()
        self.status_label.text = f"تم إصدار الفاتورة وحفظها: {filename}"

class MainApp(App):
    def build(self):
        self.title = "نظام إدارة المخازن"
        return InventoryPOSApp()

if __name__ == "__main__":
    MainApp().run()
