from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from datetime import datetime
import calendar



class CalendarPopup(ModalView):

    def __init__(self, parent_popup, **kwargs):

        super().__init__(
            size_hint=(0.9, 0.75),
            auto_dismiss=False,
            **kwargs
        )

        self.parent_popup = parent_popup

        current = datetime.strptime(
            parent_popup.record_date,
            "%d/%m/%Y"
        )

        self.year = current.year
        self.month = current.month

        self.build_calendar()


    def build_calendar(self):

        self.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            spacing=5,
            padding=10
        )

        # ======================================
        # MONTH / YEAR
        # ======================================

        top = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=5
        )

        prev_btn = Button(text="<")

        month_label = Label(
            text=(
                f"{calendar.month_name[self.month]} "
                f"{self.year}"
            )
        )

        next_btn = Button(text=">")

        prev_btn.bind(
            on_press=self.previous_month
        )

        next_btn.bind(
            on_press=self.next_month
        )

        top.add_widget(prev_btn)
        top.add_widget(month_label)
        top.add_widget(next_btn)

        root.add_widget(top)

        # ======================================
        # DAYS
        # ======================================

        days = GridLayout(
            cols=7,
            spacing=3
        )

        for day_name in [
            "Mon", "Tue", "Wed",
            "Thu", "Fri", "Sat", "Sun"
        ]:

            days.add_widget(
                Label(text=day_name)
            )

        month_calendar = calendar.monthcalendar(
            self.year,
            self.month
        )

        for week in month_calendar:

            for day in week:

                if day == 0:

                    days.add_widget(
                        Label(text="")
                    )

                else:

                    btn = Button(
                        text=str(day)
                    )

                # Highlight hari ini
                    today = datetime.now()

                    if (
                        day == today.day
                        and self.month == today.month
                        and self.year == today.year
                    ):
                        btn.background_color = (0.2, 0.6, 1, 1)

                    btn.bind(
                        on_press=lambda instance,
                        d=day:
                        self.select_date(d)
                    )

                    days.add_widget(btn)

        root.add_widget(days)

        # ======================================
        # CANCEL
        # ======================================

        cancel_btn = Button(
            text="CANCEL",
            size_hint_y=None,
            height=50
        )

        cancel_btn.bind(
            on_press=self.dismiss
        )

        root.add_widget(cancel_btn)

        self.add_widget(root)


    def previous_month(self, instance):

        self.month -= 1

        if self.month == 0:

            self.month = 12
            self.year -= 1

        self.build_calendar()


    def next_month(self, instance):

        self.month += 1

        if self.month == 13:

            self.month = 1
            self.year += 1

        self.build_calendar()


    def select_date(self, day):

        selected = datetime(
            self.year,
            self.month,
            day
        )

        self.parent_popup.record_date = (
            selected.strftime("%d/%m/%Y")
        )

        self.parent_popup.day = (
            selected.strftime("%A")
        )

        self.parent_popup.date_btn.text = (
            f"Date: {self.parent_popup.record_date}"
        )

        self.parent_popup.day_label.text = (
            f"Day: {self.parent_popup.day}"
        )

        self.dismiss()


class MonthlyPopup(ModalView):

    def __init__(self, monthly_data, month_name, **kwargs):

        super().__init__(
            size_hint=(0.95, 0.85),
            auto_dismiss=True,
            **kwargs
        )

        root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=5
        )

        # TITLE
        root.add_widget(
            Label(
                text=f"MONTHLY - {month_name}",
                size_hint_y=None,
                height=45,
                font_size=20
            )
        )

        # TABLE HEADER
        header = GridLayout(
            cols=4,
            size_hint_y=None,
            height=45
        )

        header.add_widget(Label(text="Customer"))
        header.add_widget(Label(text="Masuk"))
        header.add_widget(Label(text="Rosak"))
        header.add_widget(Label(text="Bersih"))

        root.add_widget(header)

        # TABLE
        table = GridLayout(
            cols=4,
            spacing=30,
            padding =30,
            size_hint_y=None
        )

        # Set row height
        table.bind(minimum_height=table.setter("height"))

        for data in monthly_data:

            customer = data["customer"]
            total_in = data["total_in"]
            total_damaged = data["total_damaged"]
            total_net = data["total_net"]
            

            table.add_widget(
                Label(
                    text=str(customer),
                    size_hint_y=None,
                    height=40
                )
            )

            table.add_widget(
                Label(
                    text=str(int(total_in)),
                    size_hint_y=None,
                    height=40
                )
            )

            table.add_widget(
                Label(
                    text=str(int(total_damaged)),
                    size_hint_y=None,
                    height=40
                )
            )

            table.add_widget(
                Label(
                    text=str(int(total_net)),
                    size_hint_y=None,
                    height=40
                )
            )
        
        scroll = ScrollView(
            size_hint=(1,1)
        )
        scroll.add_widget(table)  
        
        root.add_widget(scroll)
        
        total_mon=sum(
            data["total_net"]
            for data in monthly_data
        )
        table.add_widget(
            Label(
                text=f"\n\n\n                Total Monthly: {int(total_mon)}",
                size_hint_y=None,
                height=40,
                bold=True
            )
        )
    
#        root.add_widget(table)

        # CLOSE BUTTON
        close_btn = Button(
            text="CLOSE",
            size_hint_y=None,
            height=50
        )

        close_btn.bind(
            on_press=lambda instance: self.dismiss()
        )

        root.add_widget(close_btn)

        self.add_widget(root)

        
class RecordPopup(ModalView):

    def __init__(
        self,
        save_callback,
        customers=None,
        delete_callback=None,
        db=None,
        **kwargs
    ):

        super().__init__(
            size_hint=(0.9, 0.9),
            auto_dismiss=False,
            **kwargs
        )

        self.save_callback = save_callback
        self.delete_callback = delete_callback
        self.db=db
        self.is_editing=False

        if customers is None:
            customers = []

        root = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=15
        )

        # ======================================
        # TITLE
        # ======================================

        root.add_widget(
            Label(
                text="ADD TEMPE RECORD",
                font_size=22,
                size_hint_y=None,
                height=45
            )
        )

        # ======================================
        # DATE + DAY
        # ======================================

        now = datetime.now()

        self.record_date = now.strftime("%d/%m/%Y")
        self.day = now.strftime("%A")
        

        self.date_btn = Button(
            text=f"Date: {self.record_date}",
            size_hint_y=None,
            height=45
        )

        self.date_btn.bind(
            on_press=self.open_date_picker
        )

        root.add_widget(
            self.date_btn
        )


        self.day_label = Label(
            text=f"Day: {self.day}",
            size_hint_y=None,
            height=30
        )

        root.add_widget(
            self.day_label
        )

        # ======================================
        # FORM
        # ======================================

        form = GridLayout(
            cols=2,
            spacing=8,
            size_hint_y=None,
            height=650
        )

        # CUSTOMER

        form.add_widget(
            Label(text="Customer")
        )

        self.customer = Spinner(
            text="Select Customer",
            values=customers
        )
        
        self.customer.bind(
            text=self.customer_changed
        )

        form.add_widget(
            self.customer
        )

        # ITEM

        form.add_widget(
            Label(text="Item")
        )

        self.item = TextInput(
            text="Tempe",
            multiline=False
        )

        form.add_widget(
            self.item
        )

        # SEDIA ADA

        form.add_widget(
            Label(text="Qty Sedia Ada")
        )

        self.sedia_ada = TextInput(
            multiline=False,
            input_filter="int"
        )

        form.add_widget(
            self.sedia_ada
        )

        # QTY IN

        form.add_widget(
            Label(text="Qty Masuk")
        )

        self.qty_in = TextInput(
            multiline=False,
            input_filter="int"
        )

        form.add_widget(
            self.qty_in
        )

        # QTY DAMAGED

        form.add_widget(
            Label(text="Qty Rosak")
        )

        self.qty_damaged = TextInput(
            multiline=False,
            input_filter="int"
        )

        form.add_widget(
            self.qty_damaged
        )

        # INVOICE NO

        form.add_widget(
            Label(text="Invoice No")
        )

        self.invoice_no = TextInput(
            multiline=False
        )

        form.add_widget(
            self.invoice_no
        )

        # UNIT PRICE

        form.add_widget(
            Label(text="Harga / Unit RM")
        )

        self.unit_price = TextInput(
            text="1.00",
            multiline=False,
            input_filter="float"
        )

        form.add_widget(
            self.unit_price
        )

        # TOTAL

        form.add_widget(
            Label(text="Total RM")
        )

        self.total = TextInput(
            text="0.00",
            multiline=False,
            readonly=True
        )

        form.add_widget(
            self.total
        )

        root.add_widget(form)

        # SPACER

        root.add_widget(
            Label(
                text="",
                size_hint_y=1
            )
        )

        # ======================================
        # LIVE CALCULATION
        # ======================================

        self.qty_in.bind(
            text=self.calculate_total
        )

        self.qty_damaged.bind(
            text=self.calculate_total
        )

        self.unit_price.bind(
            text=self.calculate_total
        )

        # ======================================
        # BUTTONS
        # ======================================

        buttons = BoxLayout(
            spacing=10,
            size_hint_y=None,
            height=50
        )

        save_btn = Button(
            text="SAVE"
        )

        cancel_btn = Button(
            text="CANCEL"
        )

        save_btn.bind(
            on_press=self.save_record
        )

        cancel_btn.bind(
            on_press=self.dismiss
        )

        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)

        # DELETE BUTTON UNTUK EDIT

        if self.delete_callback is not None:

            delete_btn = Button(
                text="DELETE"
            )

            delete_btn.bind(
                on_press=self.delete_record
            )

            buttons.add_widget(delete_btn)

        root.add_widget(buttons)

        self.add_widget(root)


# LAST NUMBER INVOICE 

    def customer_changed(self, spinner, customer):

        if self.is_editing:
            return

        if customer == "Select Customer":
            return

        if self.db is None:
            return

        last_invoice = self.db.get_last_invoice_no(customer)

        if last_invoice:
            try:
                next_invoice = str(int(last_invoice) + 1)
            except (ValueError, TypeError):
                next_invoice = ""
        else:
            next_invoice = ""

        self.invoice_no.text = next_invoice

# ======================================
# DATE PICKER
# ======================================

    def open_date_picker(self, instance):

        calendar_popup = CalendarPopup(self)

        calendar_popup.open()
     #======================================
    # CALCULATE TOTAL
    # ======================================

    def calculate_total(self, instance, value):

        try:

            qty_in = int(
                self.qty_in.text or 0
            )

            qty_damaged = int(
                self.qty_damaged.text or 0
            )

            unit_price = float(
                self.unit_price.text or 0
            )

            net_qty = qty_in - qty_damaged

            total = net_qty * unit_price

            self.total.text = f"{total:.2f}"

        except ValueError:

            self.total.text = "0.00"


    # ======================================
    # SAVE
    # ======================================

    def save_record(self, instance):

        try:

            sedia_ada = int(
                self.sedia_ada.text or 0
            )

            qty_in = int(
                self.qty_in.text or 0
            )

            qty_damaged = int(
                self.qty_damaged.text or 0
            )

            unit_price = float(
                self.unit_price.text or 0
            )

            total = float(
                self.total.text or 0
            )

        except ValueError:

            return

        data = {

            "date": self.record_date,

            "day": self.day,

            "customer": self.customer.text,

            "item": self.item.text,

            "sedia_ada": sedia_ada,

            "qty_in": qty_in,

            "qty_damaged": qty_damaged,

            "unit_price": unit_price,

            "total": total,

            "invoice_no": self.invoice_no.text

        }

        self.save_callback(data)

        self.dismiss()


    # ======================================
    # SET DATA FOR EDIT
    # ======================================

    def set_data(
        self,
        record_date,
        day,
        customer,
        item,
        sedia_ada,
        qty_in,
        qty_damaged,
        unit_price,
        total,
        invoice_no
    ):

        self.record_date = str(record_date)

        self.day = str(day)
        
        self.date_btn.text = (f"Date: {self.record_date}")

        self.day_label.text = (f"Day: {self.day}")

        self.customer.text = str(customer)

        self.item.text = str(item)

        self.sedia_ada.text = str(
            int(float(sedia_ada or 0))
        )

        self.qty_in.text = str(
            int(float(qty_in or 0))
        )

        self.qty_damaged.text = str(
            int(float(qty_damaged or 0))
        )

        self.unit_price.text = str(unit_price)

        self.total.text = f"{float(total or 0):.2f}"

        self.invoice_no.text = str(invoice_no)


    # ======================================
    # DELETE
    # ======================================

    def delete_record(self, instance):

        if self.delete_callback:

            self.delete_callback()

        self.dismiss()