from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from datetime import datetime
from jnius import cast
from jnius import autoclass
import csv
import os
from database import Database
from components.popup import RecordPopup,MonthlyPopup


class MainLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=8, padding=8, **kwargs)
        self.db = Database()
        self.selected_date = datetime.now().strftime("%d/%m/%Y")
        self.day = datetime.now().strftime("%A")


        # ===== TITLE =====
        self.title=Label(
            text=f"[{str(self.day)}]                              TEMPE PASARAYA                     [{str(self.selected_date)}]",
            font_size=34,
            size_hint_y=None,
            height=50
        )
        
        self.add_widget(
            self.title
        )

        # ===== ADD BUTTON =====
        self.add_btn = Button(
            text="ADD RECORD",
            size_hint_y=None,
            height=80
        )
        self.add_btn.bind(
            on_press=self.open_add_record
        )
        self.add_widget(self.add_btn)
        
        
        self.customer_btn = Button(
            text="CUSTOMERS",
            size_hint_y=None,
            height=50
        )
        self.customer_btn.bind(
            on_press=self.show_customers
        )
        self.add_widget(self.customer_btn)


        # ===== TABLE HEADER =====
        header = GridLayout(
            cols=6,
            size_hint_y=None,
            height=60
        )

        header.add_widget(Label(text="Customer"))
        header. add_widget(Label(text="Invoice"))
        header.add_widget(Label(text="Sedia Ada"))
        header.add_widget(Label(text="Masuk"))
        header.add_widget(Label(text="Rosak"))
      
        header.add_widget(Label(text="Total"))

        self.add_widget(header)

        # ===== TABLE =====
        self.table = GridLayout(
            cols=6,
            spacing=25,
            size_hint_y=None
        )

        self.table.bind(minimum_height=self.table.setter("height"))
        

        scroll = ScrollView()
        scroll.add_widget(self.table)

        self.add_widget(scroll)

        # ===== SUMMARY =====
       
        summary_layout = GridLayout(
            cols=3,
            size_hint_y= 1.5, 
            height=50
        )

        self.total_records = Label(
            text="Records: 0",
            font_size=50
        )
        self.total_qty_in = Label(
            text="Masuk: 0",
            font_size=50
        )
        self.total_qty_damaged = Label(
            text="Rosak: 0",
            font_size=50
        )

        summary_layout.add_widget(
            self.total_records
        )
        summary_layout.add_widget(
            self.total_qty_in
        )
        summary_layout.add_widget(
            self.total_qty_damaged
        )
        self.add_widget(summary_layout)

        # ===== BUTTONS =====
        
        bottom = BoxLayout(
            size_hint_y=None,
            height=100,
            spacing=2
        )

        self.undo_btn = Button(text="Undo Delete")
        self.history_btn = Button(text="History")
        self.send_btn = Button(text="Send Report")
        self.monthly_btn = Button(text="Monthly")
        bottom.add_widget(self.undo_btn)
        bottom.add_widget(self.history_btn)
        bottom.add_widget(self.send_btn)
        bottom.add_widget(self.monthly_btn)
        
        self.undo_btn.bind(on_press=lambda instance: self.undo_delete())
        self.history_btn.bind(on_press=self.show_history)
        self.send_btn.bind(on_press=self.open_report_date_picker)
        self.monthly_btn.bind(on_press=self.open_monthly)
        
        self.add_widget(bottom)
        self.refresh_table()
            
            
     # ======================================
    # REFRESH TABLE
    # ======================================

    def refresh_table(self):

        self.table.clear_widgets()

        rows = self.db.get_by_date(
            self.selected_date
        )
        
        self.day=datetime.strptime(self.selected_date,"%d/%m/%Y").strftime("%A")
        
        self.title.text=(
            f"[{str(self.day)}]                              TEMPE PASARAYA                     [{str(self.selected_date)}]"
        )

        for row in rows:

            record_id = row[0]
            customer = row[3]
            item = row[4]
            sedia_ada = row[5]
            qty_in = row[6]
            qty_damaged = row[7]
            unit_price = row[8]
            total = row[9]
            invoice_no = row[10]

            values = [

                str(customer),

                str(invoice_no),
                
                str(int(sedia_ada)),

                str(int(qty_in)),

                (
                    str(int(qty_damaged))
                    if float(qty_damaged) != 0
                    else "-"
                ),

                f"RM{float(total):.2f}"

            ]

            for value in values:

                btn = Button(
                    text=value,
                    size_hint_y=None,
                    height=45,
                    background_normal="",
                    background_color=(0, 0, 0, 0)
                )

                btn.bind(
                    on_press=lambda instance,
                    record_id=record_id:
                    self.edit_record(record_id)
                )

                self.table.add_widget(btn)
                

        # ======================================
        # DAILY SUMMARY
        # ======================================

        summary = (
            self.db.get_daily_quantity_summary(
                self.selected_date
            )
        )

        self.total_records.text = (
            f"Records: {len(rows)}"
        )

        self.total_qty_in.text = (
            f"Masuk: {int(summary['qty_in'])}"
        )

        self.total_qty_damaged.text = (
            f"Rosak: {int(summary['qty_damaged'])}"
        )


#      FUNCTION RECORDS

    def edit_record(self, record_id):

        row = self.db.get_record(record_id)

        if row is None:
            return

        customers = self.db.get_customers()

        customer_names = [
            customer[1]
            for customer in customers
        ]

        # Pastikan customer lama masih ada
        if row[3] not in customer_names:
            customer_names.append(row[3])

        popup = RecordPopup(
            save_callback=lambda data:
            self.update_record(record_id, data),

            customers=customer_names,

            delete_callback=lambda:
            self.delete_record(record_id),
            db=self.db
        )

        popup.set_data(
            row[1],  # date
            row[2],  # day
            row[3],  # customer
            row[4],  # item
            row[5],  # sedia ada
            row[6],  # qty masuk
            row[7],  # qty rosak
            row[8],  # harga
            row[9],  # total
            row[10]   # invoice no
        )

        popup.open()   
        
                
    def update_record(self, record_id, data):

        self.db.update_record(
            record_id,
            data["date"],
            data["day"],
            data["customer"],
            data["item"],
            data["sedia_ada"],
            data["qty_in"],
            data["qty_damaged"],
            data["unit_price"],
            data["total"],
            data["invoice_no"]
        )

        self.refresh_table()

                
    def delete_record(self, record_id):

        confirm = ModalView(
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )

        layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=15
        )

        layout.add_widget(
            Label(
                text="Delete this record?"
            )
        )

        buttons = BoxLayout(
            spacing=10,
            size_hint_y=None,
            height=50
        )

        yes_btn = Button(text="YES")
        no_btn = Button(text="NO")

        yes_btn.bind(
            on_press=lambda instance:
                self.confirm_delete_record(
                    record_id,
                    confirm
                )
        )

        no_btn.bind(
            on_press=confirm.dismiss
        )

        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)

        layout.add_widget(buttons)

        confirm.add_widget(layout)

        confirm.open()    
        
        
    def confirm_delete_record(
        self,
        record_id,
        confirm
    ):

        confirm.dismiss()

        row = self.db.get_record(record_id)

        if row is None:
            return

        self.deleted_record = row

        self.db.delete_record(record_id)

        self.refresh_table()
     
           
    def undo_delete(self):

        if self.deleted_record is None:
            return

        row = self.deleted_record
        self.db.restore_record(row)
        self.deleted_record = None
        
        self.refresh_table()
        
        # CUSTOMER #
        
    def show_customers(self, instance):

        popup = ModalView(
            size_hint=(0.9, 0.85),
            auto_dismiss=False
        )

        root = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=15
        )

        root.add_widget(
            Label(
                text="CUSTOMERS",
                font_size=22,
                size_hint_y=None,
                height=45
            )
        )

        # ===== ADD CUSTOMER =====

        add_layout = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=5
        )

        customer_input = TextInput(
            hint_text="Customer name",
            multiline=False
        )

        add_btn = Button(
            text="ADD",
            size_hint_x=None,
            width=100
        )

        add_layout.add_widget(customer_input)
        add_layout.add_widget(add_btn)

        root.add_widget(add_layout)

        # ===== CUSTOMER LIST =====

        scroll = ScrollView()

        customer_list = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )

        customer_list.bind(
            minimum_height=customer_list.setter("height")
        )

        scroll.add_widget(customer_list)

        root.add_widget(scroll)

        # ===== CLOSE =====

        close_btn = Button(
            text="CLOSE",
            size_hint_y=None,
            height=50
        )

        close_btn.bind(
            on_press=popup.dismiss
        )

        root.add_widget(close_btn)

        popup.add_widget(root)

        # ======================================
        # REFRESH CUSTOMER LIST
        # ======================================

        def refresh_customers():

            customer_list.clear_widgets()

            customers = self.db.get_customers()

            for customer in customers:

                customer_id = customer[0]
                customer_name = customer[1]

                row = BoxLayout(
                    size_hint_y=None,
                    height=50,
                    spacing=5
                )

                row.add_widget(
                    Label(
                        text=customer_name
                    )
                )

                delete_btn = Button(
                    text="DELETE",
                    size_hint_x=None,
                    width=100
                )

                delete_btn.bind(
                    on_press=lambda btn,
                    customer_id=customer_id:
                    delete_customer(customer_id)
                )

                row.add_widget(delete_btn)

                customer_list.add_widget(row)


        # ======================================
        # ADD CUSTOMER
        # ======================================

        def add_customer(instance):

            name = customer_input.text.strip()

            if not name:
                return

            success = self.db.add_customer(name)

            if success:

                customer_input.text = ""

                refresh_customers()


        # ======================================
        # DELETE CUSTOMER
        # ======================================

        def delete_customer(customer_id):

            self.db.delete_customer(customer_id)

            refresh_customers()


        add_btn.bind(
            on_press=add_customer
        )

        refresh_customers()

        popup.open()
        
        
       
       #       HISTORY     #
       
       
       
    def show_history(self, instance):

        dates = self.db.get_dates()

        history = ModalView(
            size_hint=(0.9, 0.85),
            auto_dismiss=False
        )

        root = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=15
        )

        root.add_widget(
            Label(
                text="HISTORY",
                font_size=22,
                size_hint_y=None,
                height=45
            )
        )

        # ======================================
        # HEADER
        # ======================================

        header = GridLayout(
            cols=3,
            size_hint_y=None,
            height=40
        )

        header.add_widget(
            Label(text="Date")
        )

        header.add_widget(
            Label(text="Total Masuk")
        )

        header.add_widget(
            Label(text="Total Rosak")
        )

        root.add_widget(header)

        # ======================================
        # DATE LIST
        # ======================================

        scroll = ScrollView()

        history_list = GridLayout(
            cols=3,
            size_hint_y=None
        )

        history_list.bind(
            minimum_height=
            history_list.setter("height")
        )

        for date_row in dates:

            record_date = date_row[0]

            summary = (
                self.db.get_daily_quantity_summary(
                    record_date
                )
            )

            # Date button
            date_btn = Button(
                text=str(record_date),
                size_hint_y=None,
                height=50
            )

            date_btn.bind(
                on_press=lambda instance,
                selected_date=record_date:
                self.load_history_date(
                    selected_date,
                    history
                )
            )

            history_list.add_widget(
                date_btn
            )

            history_list.add_widget(
                Label(
                    text=str(int(summary["qty_in"])),
                    size_hint_y=None,
                    height=50
                )
            )

            history_list.add_widget(
                Label(
                    text=str(int(summary["qty_damaged"])),
                    size_hint_y=None,
                    height=50
                )
            )

        scroll.add_widget(history_list)

        root.add_widget(scroll)

        # ======================================
        # CLOSE
        # ======================================

        close_btn = Button(
            text="CLOSE",
            size_hint_y=None,
            height=50
        )

        close_btn.bind(
            on_press=history.dismiss
        )

        root.add_widget(close_btn)

        history.add_widget(root)

        history.open()
        
        
    def load_history_date(
        self,
        selected_date,
        history_popup
    ):

        self.selected_date = selected_date

        self.refresh_table()

        history_popup.dismiss()
                

     #     REPORTING   #
     
    def open_report_date_picker(self, instance):
    	
        today = datetime.now().strftime("%d/%m/%Y")

        dates = self.db.get_dates()

        popup = ModalView(
            size_hint=(0.85, 0.75),
            auto_dismiss=False
        )

        root = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=15
        )

        root.add_widget(
            Label(
                text="SELECT REPORT DATE",
                font_size=20,
                size_hint_y=None,
                height=45
            )
        )

        # ===== TODAY BUTTON =====

        today_btn = Button(
            text=f"TODAY - {today}",
            size_hint_y=None,
            height=50
        )

        today_btn.bind(
            on_press=lambda instance:
                self.send_report_by_date(
                    today,
                    popup
                )
        )

        root.add_widget(today_btn)

        # ===== DATE LIST =====

        scroll = ScrollView()

        date_list = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )

        date_list.bind(
            minimum_height=date_list.setter("height")
        )

        for date_row in dates:

            selected_date = date_row[0]

            # Jangan duplicate today
            if selected_date == today:
                continue

            date_btn = Button(
                text=str(selected_date),
                size_hint_y=None,
                height=50
            )

            date_btn.bind(
                on_press=lambda instance,
                selected_date=selected_date:
                    self.send_report_by_date(
                        selected_date,
                        popup
                    )
            )

            date_list.add_widget(date_btn)

        scroll.add_widget(date_list)

        root.add_widget(scroll)

        close_btn = Button(
            text="CANCEL",
            size_hint_y=None,
            height=50
        )

        close_btn.bind(
            on_press=popup.dismiss
        )

        root.add_widget(close_btn)

        popup.add_widget(root)

        popup.open()
        
        
    def send_report_by_date(
        self,
        selected_date,
        popup
    ):

        rows = self.db.get_by_date(
            selected_date
        )

        if not rows:

            print(
                "No records for:",
                selected_date
            )

            return

        popup.dismiss()

        record_date = rows[0][1]
        day = rows[0][2]

        report = (
            "TEMPE DAILY REPORT\n"
            "====================\n\n"
            f"Date: {record_date}\n"
            f"Day: {day}\n\n"
        )

        for row in rows:

            customer = row[3]
            item = row[4]
            qty_in = row[6]
            qty_damaged = row[7]
            total = row[9]
            invoice_no = row[10]

            report += (
                f"Customer: {customer}\n"
                f"Invoice No: {invoice_no}\n"
                f"Item: {item}\n"
                f"Masuk: {int(qty_in)}\n"
            )

            if float(qty_damaged) != 0:

                report += (
                    f"Rosak: "
                    f"{int(qty_damaged)}\n"
                )

            report += (
                f"Total: "
                f"RM{float(total):.2f}\n"
                "--------------------\n"
            )

        # ===== DAILY SUMMARY =====

        summary = (
            self.db.get_daily_quantity_summary(
                selected_date
            )
        )

        report += "\n====================\n"

        report += (
            f"TOTAL MASUK: "
            f"{int(summary['qty_in'])}\n"
        )

        if float(
            summary["qty_damaged"]
        ) != 0:

            report += (
                f"TOTAL ROSAK: "
                f"{int(summary['qty_damaged'])}\n"
            )

        # ===== SHARE =====

        try:

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            Intent = autoclass(
                "android.content.Intent"
            )

            String = autoclass(
                "java.lang.String"
            )

            activity = PythonActivity.mActivity

            share = Intent()

            share.setAction(
                Intent.ACTION_SEND
            )

            share.setType(
                "text/plain"
            )

            share.putExtra(
                Intent.EXTRA_TEXT,
                cast(
                    "java.lang.CharSequence",
                    String(report)
                )
            )

            chooser = Intent.createChooser(
                share,
                String("Send Tempe Report")
            )

            activity.startActivity(chooser)

        except Exception as e:

            print(
                "SHARE ERROR:",
                e
            )
        
        
        
    def open_monthly(self, instance):

        data = self.db.get_monthly_customer_summary(
            self.selected_date
        )

        month = self.selected_date[3:5]
        year = self.selected_date[6:10]

        month_names = [
            "",
            "JANUARY",
            "FEBRUARY",
            "MARCH",
            "APRIL",
            "MAY",
            "JUNE",
            "JULY",
            "AUGUST",
            "SEPTEMBER",
            "OCTOBER",
            "NOVEMBER",
            "DECEMBER"
        ]

        month_name = (
            f"{month_names[int(month)]} {year}"
        )

        popup = MonthlyPopup(
            monthly_data=data,
            month_name=month_name
        )

        popup.open()
            
            
    def open_add_record(self, instance):

        customers = self.db.get_customers()

        customer_names = [
            row[1]
            for row in customers
        ]

        popup = RecordPopup(
            save_callback=self.save_record,
            customers=customer_names,
            db=self.db
        )

        popup.open()
        
        
    def save_record(self, data):

        self.db.add_record(
            data["date"],
            data["day"],
            data["customer"],
            data["item"],
            data["sedia_ada"],
            data["qty_in"],
            data["qty_damaged"],
            data["unit_price"],
            data["total"],
            data["invoice_no"]
        )

        self.selected_date = data["date"]

        self.refresh_table()
            
class TempeScannerApp(App):

    def build(self):
        self.title = "Tempe Scanner"
        return MainLayout()


if __name__ == "__main__":
    TempeScannerApp().run()