import sqlite3
from config import DATABASE


class Database:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

        self.cursor = self.conn.cursor()
        
        self.create_tables()
        
        

    # ======================================
    # CREATE TABLES
    # ======================================

    def create_tables(self):

        # ===== RECORDS =====

        self.cursor.execute("""

            CREATE TABLE IF NOT EXISTS records (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                record_date TEXT,

                day TEXT,

                customer TEXT,

                item TEXT,
                
                sedia_ada REAL,

                qty_in REAL,

                qty_damaged REAL DEFAULT 0,

                unit_price REAL DEFAULT 1.00,

                total REAL,

                invoice_no TEXT,

                created_at TEXT

            )

        """)


        # ===== CUSTOMERS =====

        self.cursor.execute("""

            CREATE TABLE IF NOT EXISTS customers (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT UNIQUE

            )

        """)
        
        self.cursor.execute("""
            PRAGMA table_info(records)
        """)

        columns = [
            row[1]
            for row in self.cursor.fetchall()
        ]

        if "sedia_ada" not in columns:

            self.cursor.execute("""
                ALTER TABLE records
                ADD COLUMN sedia_ada REAL DEFAULT 0
            """)

            self.conn.commit()

        


    # ======================================
    # ADD RECORD
    # ======================================

    def add_record(
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

        self.cursor.execute(
            """

            INSERT INTO records (

                record_date,
                day,
                customer,
                item,
                sedia_ada,
                qty_in,
                qty_damaged,
                unit_price,
                total,
                invoice_no,
                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))

            """,

            (
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
            )
        )

        self.conn.commit()


    # ======================================
    # GET ALL RECORDS
    # ======================================

    def get_all(self):

        self.cursor.execute("""

            SELECT *

            FROM records

            ORDER BY id DESC

        """)

        return self.cursor.fetchall()


    # ======================================
    # GET ONE RECORD
    # ======================================

    def get_record(self, record_id):

        self.cursor.execute(
            """

            SELECT *

            FROM records

            WHERE id = ?

            """,

            (record_id,)
        )

        return self.cursor.fetchone()


    # ======================================
    # UPDATE RECORD
    # ======================================

    def update_record(
        self,
        record_id,
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

        self.cursor.execute(
            """

            UPDATE records

            SET

                record_date = ?,
                day = ?,
                customer = ?,
                item = ?,
                sedia_ada = ?,
                qty_in = ?,
                qty_damaged = ?,
                unit_price = ?,
                total = ?,
                invoice_no = ?

            WHERE id = ?

            """,

            (
                record_date,
                day,
                customer,
                item,
                sedia_ada,
                qty_in,
                qty_damaged,
                unit_price,
                total,
                invoice_no,
                record_id
            )
        )

        self.conn.commit()


    # ======================================
    # DELETE RECORD
    # ======================================

    def delete_record(self, record_id):

        self.cursor.execute(
            """

            DELETE FROM records

            WHERE id = ?

            """,

            (record_id,)
        )

        self.conn.commit()


    # ======================================
    # RESTORE RECORD
    # ======================================

    def restore_record(self, row):

        self.cursor.execute(
            """

            INSERT INTO records (

                id,
                record_date,
                day,
                customer,
                item,
                sedia_ada,
                qty_in,
                qty_damaged,
                unit_price,
                total,
                invoice_no,
                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            row
        )

        self.conn.commit()


    # ======================================
    # CUSTOMER FUNCTIONS
    # ======================================

    def get_customers(self):

        self.cursor.execute("""

            SELECT *

            FROM customers

            ORDER BY name

        """)

        return self.cursor.fetchall()


    def add_customer(self, name):

        try:

            self.cursor.execute(
                """

                INSERT INTO customers (name)

                VALUES (?)

                """,

                (name.strip(),)
            )

            self.conn.commit()

            return True

        except sqlite3.IntegrityError:

            return False


    def delete_customer(self, customer_id):

        self.cursor.execute(
            """

            DELETE FROM customers

            WHERE id = ?

            """,

            (customer_id,)
        )

        self.conn.commit()


    # ======================================
    # GRAND TOTAL
    # ======================================

    def get_total(self):

        self.cursor.execute("""

            SELECT SUM(total)

            FROM records

        """)

        result = self.cursor.fetchone()[0]

        return result if result is not None else 0


    # ======================================
    # TOTAL RECORDS
    # ======================================

    def get_count(self):

        self.cursor.execute("""

            SELECT COUNT(*)

            FROM records

        """)

        return self.cursor.fetchone()[0]


    # ======================================
    # GET RECORDS BY DATE
    # ======================================

    def get_by_date(self, record_date):

        self.cursor.execute(
            """

            SELECT *

            FROM records

            WHERE record_date = ?

            ORDER BY id

            """,

            (record_date,)
        )

        return self.cursor.fetchall()


    # ======================================
    # GET DATES
    # ======================================

    def get_dates(self):

        self.cursor.execute("""

            SELECT DISTINCT record_date

            FROM records

            ORDER BY 
    substr(record_date, 7, 4) DESC,
    substr(record_date, 4, 2) DESC,
    substr(record_date, 1, 2) DESC

        """)

        return self.cursor.fetchall()



    # ======================================
    # DAILY QUANTITY SUMMARY
    # ======================================

    def get_daily_quantity_summary(self, record_date):

        self.cursor.execute(
            """

            SELECT

                COALESCE(SUM(qty_in), 0),

                COALESCE(SUM(qty_damaged), 0)

            FROM records

            WHERE record_date = ?

            """,
            (record_date,)
        )

        result = self.cursor.fetchone()

        return {

            "qty_in": result[0],
            "qty_damaged": result[1]

        }


   # MONTHLY DATABASE 
    
    def get_monthly_customer_summary(self, record_date):

    # Ambil bulan dan tahun daripada tarikh yang dipilih
        month = record_date[3:5]
        year = record_date[6:10]

        self.cursor.execute("""
            SELECT
                customer,
                COALESCE(SUM(qty_in), 0),
                COALESCE(SUM(qty_damaged), 0)
            FROM records
            WHERE substr(record_date, 4, 2) = ?
            AND substr(record_date, 7, 4) = ?
            GROUP BY customer
            ORDER BY customer
        """, (month, year))

        rows = self.cursor.fetchall()

        result = []

        for row in rows:

            customer = row[0]
            total_in = row[1]
            total_damaged = row[2]

            total_net = total_in - total_damaged

            result.append({
                "customer": customer,
                "total_in": total_in,
                "total_damaged": total_damaged,
                "total_net": total_net,
            })

        return result

# AUTOFILL INOVOICE NUMBER    
        
            
    def get_last_invoice_no(self, customer):

        self.cursor.execute("""
            SELECT invoice_no
            FROM records
            WHERE customer = ?
            AND invoice_no IS NOT NULL
            AND invoice_no != ''
            ORDER BY id DESC
            LIMIT 1
        """, (customer,))

        result = self.cursor.fetchone()

        if result is None:
            return ""
  
        return result[0]   
        
            
    # ======================================
    # CLOSE DATABASE
    # ======================================

    def close(self):

        self.conn.close()