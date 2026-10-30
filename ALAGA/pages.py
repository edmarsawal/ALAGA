import tkinter as tk
from datetime import date
from database import get_connection
from style import BG_COLOR, CARD_COLOR, PRIMARY_COLOR, TEXT_COLOR, MUTED_COLOR, FONT


def show_dashboard(parent, user=None):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent,
        text="Welcome to ALAGA!",
        font=(FONT, 22, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w")

    tk.Label(
        parent,
        text="Your livestock care overview",
        font=(FONT, 11),
        bg=BG_COLOR,
        fg=MUTED_COLOR
    ).pack(anchor="w", pady=(5, 25))

    stats_frame = tk.Frame(parent, bg=BG_COLOR)
    stats_frame.pack(fill="x")

    stats = [
        ("Total Animals", "SELECT COUNT(*) FROM animals"),
        (
            "Vaccinations Due",
            """
            SELECT COUNT(*) FROM vaccinations
            WHERE next_due_date BETWEEN %s AND %s
            """
        ),
        ("Health Records", "SELECT COUNT(*) FROM health_records"),
        ("Feeding Records", "SELECT COUNT(*) FROM feeding_records")
    ]

    today = date.today()
    first_day = today.replace(day=1)

    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)

    try:
        connection = get_connection()
        cursor = connection.cursor()

        for index, (title, query) in enumerate(stats):
            if title == "Vaccinations Due":
                cursor.execute(query, (first_day, next_month))
            else:
                cursor.execute(query)

            count = cursor.fetchone()[0]

            card = tk.Frame(
                stats_frame,
                bg=CARD_COLOR,
                padx=15,
                pady=20,
                highlightbackground="#DCE7DF",
                highlightthickness=1
            )
            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=5
            )

            tk.Label(
                card,
                text=title.upper(),
                font=(FONT, 9, "bold"),
                bg=CARD_COLOR,
                fg=MUTED_COLOR
            ).pack(anchor="w")

            tk.Label(
                card,
                text=str(count),
                font=(FONT, 27, "bold"),
                bg=CARD_COLOR,
                fg=PRIMARY_COLOR
            ).pack(anchor="w", pady=8)

        for index in range(4):
            stats_frame.columnconfigure(index, weight=1)

        cursor.close()
        connection.close()

    except Exception as error:
        tk.Label(
            parent,
            text=f"Unable to load dashboard: {error}",
            font=(FONT, 10),
            bg=BG_COLOR,
            fg="red",
            wraplength=700
        ).pack(anchor="w", pady=15)

    tk.Label(
        parent,
        text="Better Records, Better Animal Care.",
        font=(FONT, 16, "bold"),
        bg=BG_COLOR,
        fg=PRIMARY_COLOR
    ).pack(anchor="w", pady=30)

# animals.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from style import BG_COLOR, CARD_COLOR, PRIMARY_COLOR, TEXT_COLOR, FONT


def show_animals(parent, user=None):
    # Clear the current page
    for widget in parent.winfo_children():
        widget.destroy()

    # Page title
    tk.Label(
        parent,
        text="Livestock Management",
        font=(FONT, 21, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", pady=(0, 15))

    # Form container
    form = tk.Frame(parent, bg=CARD_COLOR, padx=12, pady=12)
    form.pack(fill="x")

    # Form fields (Condition removed; Status remains)
    fields = [
        ("Tag Number", "tag"),
        ("Animal Name", "name"),
        ("Species", "species"),
        ("Breed", "breed"),
        ("Sex (Male/Female)", "sex"),
        ("Birth Date (YYYY-MM-DD)", "birth"),
        ("Weight (kg)", "weight"),
        ("Status", "status")
    ]

    entries = {}

    for index, (label, key) in enumerate(fields):
        row, col = divmod(index, 4)

        tk.Label(
            form,
            text=label,
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=(FONT, 9)
        ).grid(
            row=row * 2,
            column=col,
            sticky="w",
            padx=5
        )

        if key == "status":
            entry = ttk.Combobox(
                form,
                values=[
                    "Active",
                    "Under Treatment",
                    "Sold",
                    "Deceased",
                    "Inactive"
                ],
                state="readonly",
                font=(FONT, 10),
                width=16
            )
            entry.set("Active")
        else:
            entry = tk.Entry(
                form,
                font=(FONT, 10),
                width=18
            )

        entry.grid(
            row=row * 2 + 1,
            column=col,
            sticky="ew",
            padx=5,
            pady=(3, 8)
        )

        entries[key] = entry

    for col in range(4):
        form.columnconfigure(col, weight=1)

    # Search controls
    search_frame = tk.Frame(parent, bg=BG_COLOR)
    search_frame.pack(fill="x", pady=(12, 0))

    tk.Label(
        search_frame,
        text="Search by Tag Number or Name:",
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=(FONT, 10)
    ).pack(side="left", padx=(0, 8))

    search_entry = tk.Entry(search_frame, font=(FONT, 10), width=25)
    search_entry.pack(side="left", padx=(0, 8))

    # Table container
    table_frame = tk.Frame(parent, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, pady=15)

    columns = (
        "id", "tag", "name", "species", "breed",
        "sex", "birth", "weight", "status"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=12
    )

    headings = {
        "id": "ID",
        "tag": "Tag Number",
        "name": "Name",
        "species": "Species",
        "breed": "Breed",
        "sex": "Sex",
        "birth": "Birth Date",
        "weight": "Weight (kg)",
        "status": "Status"
    }

    for column in columns:
        table.heading(column, text=headings[column])
        table.column(column, width=100, anchor="center")

    table.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )
    scrollbar.pack(side="right", fill="y")

    table.configure(yscrollcommand=scrollbar.set)

    # Load animals from database
    def load_animals(search=""):
        table.delete(*table.get_children())

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    animal_id,
                    tag_number,
                    animal_name,
                    species,
                    breed,
                    sex,
                    birth_date,
                    weight,
                    status
                FROM animals
                WHERE tag_number LIKE %s
                   OR animal_name LIKE %s
                ORDER BY animal_id DESC
            """, (f"%{search}%", f"%{search}%"))

            for record in cursor.fetchall():
                table.insert("", "end", values=record)

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error),
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Get and validate form values
    def get_form_values():
        tag = entries["tag"].get().strip()
        name = entries["name"].get().strip() or None
        species = entries["species"].get().strip()
        breed = entries["breed"].get().strip() or None
        sex = entries["sex"].get().strip() or None
        birth = entries["birth"].get().strip() or None
        weight_text = entries["weight"].get().strip()
        status = entries["status"].get().strip() or "Active"

        if not tag:
            messagebox.showwarning(
                "Required Field",
                "Please enter the Tag Number.",
                parent=parent
            )
            return None

        if not species:
            messagebox.showwarning(
                "Required Field",
                "Please enter the Species.",
                parent=parent
            )
            return None

        if sex and sex.lower() not in ("male", "female"):
            messagebox.showwarning(
                "Invalid Sex",
                "Sex must be Male or Female.",
                parent=parent
            )
            return None

        if status not in (
            "Active",
            "Under Treatment",
            "Sold",
            "Deceased",
            "Inactive"
        ):
            messagebox.showwarning(
                "Invalid Status",
                "Please select a valid animal status.",
                parent=parent
            )
            return None

        weight = None

        if weight_text:
            try:
                weight = float(weight_text)

                if weight < 0 or weight == float("inf") or weight != weight:
                    raise ValueError

            except ValueError:
                messagebox.showwarning(
                    "Invalid Weight",
                    "Please enter a valid, non-negative weight.",
                    parent=parent
                )
                return None

        # Validate date format when provided
        if birth:
            from datetime import datetime

            try:
                datetime.strptime(birth, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Invalid Birth Date",
                    "Use the date format YYYY-MM-DD.",
                    parent=parent
                )
                return None

        return (
            tag, name, species, breed, sex,
            birth, weight, status
        )

    # Add a new animal
    def add_animal():
        values = get_form_values()

        if values is None:
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO animals (
                    tag_number,
                    animal_name,
                    species,
                    breed,
                    sex,
                    birth_date,
                    weight,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, values)

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Animal registered successfully.",
                parent=parent
            )

            clear_form()
            load_animals()

        except Exception as error:
            if connection and connection.is_connected():
                connection.rollback()

            messagebox.showerror(
                "Unable to Save",
                f"Could not register the animal.\n\n{error}",
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Load selected animal into the form
    def load_selected_animal():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an animal from the table.",
                parent=parent
            )
            return

        values = table.item(selected[0], "values")

        entries["tag"].delete(0, tk.END)
        entries["tag"].insert(0, values[1] or "")

        entries["name"].delete(0, tk.END)
        entries["name"].insert(0, values[2] or "")

        entries["species"].delete(0, tk.END)
        entries["species"].insert(0, values[3] or "")

        entries["breed"].delete(0, tk.END)
        entries["breed"].insert(0, values[4] or "")

        entries["sex"].delete(0, tk.END)
        entries["sex"].insert(0, values[5] or "")

        entries["birth"].delete(0, tk.END)
        entries["birth"].insert(0, values[6] or "")

        entries["weight"].delete(0, tk.END)
        entries["weight"].insert(0, values[7] if values[7] is not None else "")

        entries["status"].set(values[8] or "Active")

    # Update selected animal
    def update_animal():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an animal to update.",
                parent=parent
            )
            return

        animal_id = table.item(selected[0], "values")[0]
        values = get_form_values()

        if values is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Update",
            "Update the information for this animal?",
            parent=parent
        )

        if not confirm:
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE animals
                SET
                    tag_number = %s,
                    animal_name = %s,
                    species = %s,
                    breed = %s,
                    sex = %s,
                    birth_date = %s,
                    weight = %s,
                    status = %s
                WHERE animal_id = %s
            """, values + (animal_id,))

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Animal information updated successfully.",
                parent=parent
            )

            clear_form()
            load_animals()

        except Exception as error:
            if connection and connection.is_connected():
                connection.rollback()

            messagebox.showerror(
                "Update Failed",
                f"Could not update the animal.\n\n{error}",
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Clear all form fields
    def clear_form():
        for key, entry in entries.items():
            if key == "status":
                entry.set("Active")
            else:
                entry.delete(0, tk.END)

        table.selection_remove(table.selection())

    # Delete selected animal
    def delete_animal():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an animal to delete.",
                parent=parent
            )
            return

        animal_id = table.item(selected[0], "values")[0]
        tag_number = table.item(selected[0], "values")[1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete animal {tag_number} and its related records?",
            parent=parent
        )

        if not confirm:
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM animals WHERE animal_id = %s",
                (animal_id,)
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Animal deleted successfully.",
                parent=parent
            )

            clear_form()
            load_animals()

        except Exception as error:
            if connection and connection.is_connected():
                connection.rollback()

            messagebox.showerror(
                "Delete Failed",
                "Could not delete this animal. Related records may "
                "prevent deletion.\n\n"
                f"{error}",
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Search animals
    def search_animals():
        load_animals(search_entry.get().strip())

    # Action buttons
    button_frame = tk.Frame(parent, bg=BG_COLOR)
    button_frame.pack(fill="x", pady=(0, 10))

    tk.Button(
        button_frame,
        text="Add Animal",
        command=add_animal,
        bg=PRIMARY_COLOR,
        fg="white",
        font=(FONT, 10, "bold"),
        padx=10,
        pady=6
    ).pack(side="left", padx=(0, 5))

    tk.Button(
        button_frame,
        text="Load Selected",
        command=load_selected_animal,
        font=(FONT, 10),
        padx=10,
        pady=6
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Update Selected",
        command=update_animal,
        font=(FONT, 10),
        padx=10,
        pady=6
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Clear Form",
        command=clear_form,
        font=(FONT, 10),
        padx=10,
        pady=6
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Delete Selected",
        command=delete_animal,
        font=(FONT, 10),
        padx=10,
        pady=6
    ).pack(side="left", padx=5)

    tk.Button(
        search_frame,
        text="Search",
        command=search_animals,
        bg=PRIMARY_COLOR,
        fg="white",
        font=(FONT, 9),
        padx=10
    ).pack(side="left")

    search_entry.bind(
        "<Return>",
        lambda event: search_animals()
    )

    # Load records when the page opens
    load_animals()


# ================== VACCINATION PAGE ==================


# vaccination.py

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from style import BG_COLOR, CARD_COLOR, PRIMARY_COLOR, TEXT_COLOR, FONT


def show_vaccination(parent, user=None):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent, text="Vaccination Records",
        font=(FONT, 21, "bold"), bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(anchor="w", pady=(0, 15))

    form = tk.Frame(parent, bg=CARD_COLOR, padx=12, pady=12)
    form.pack(fill="x")

    fields = [
        ("Animal ID", "animal"),
        ("Vaccine Name", "vaccine"),
        ("Date (YYYY-MM-DD)", "date"),
        ("Next Due (YYYY-MM-DD)", "due"),
        ("Notes", "notes")
    ]
    entries = {}

    for index, (label, key) in enumerate(fields):
        tk.Label(
            form, text=label, bg=CARD_COLOR, font=(FONT, 9)
        ).grid(row=0, column=index, sticky="w", padx=5)

        entry = tk.Entry(form, font=(FONT, 10), width=20)
        entry.grid(row=1, column=index, sticky="ew", padx=5, pady=5)
        entries[key] = entry

    table = ttk.Treeview(
        parent,
        columns=("id", "animal", "vaccine", "date", "due", "notes"),
        show="headings",
        height=12
    )

    for col, title in [
        ("id", "ID"), ("animal", "Animal ID"), ("vaccine", "Vaccine"),
        ("date", "Date Given"), ("due", "Next Due"), ("notes", "Notes")
    ]:
        table.heading(col, text=title)
        table.column(col, width=120)

    table.pack(fill="both", expand=True, pady=15)

    def load_records():
        table.delete(*table.get_children())
        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT vaccination_id, animal_id, vaccine_name,
                       vaccination_date, next_due_date, notes
                FROM vaccinations
                ORDER BY vaccination_date DESC
            """)
            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        except Exception as error:
            messagebox.showerror("Database Error", str(error), parent=parent)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def add_record():
        animal = entries["animal"].get().strip()
        vaccine = entries["vaccine"].get().strip()
        date_given = entries["date"].get().strip()
        due = entries["due"].get().strip() or None
        notes = entries["notes"].get().strip() or None

        if not animal or not vaccine or not date_given:
            messagebox.showwarning(
                "Required Fields",
                "Animal ID, Vaccine Name, and Date are required.",
                parent=parent
            )
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO vaccinations
                    (animal_id, vaccine_name, vaccination_date,
                     next_due_date, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (int(animal), vaccine, date_given, due, notes))
            connection.commit()

            for entry in entries.values():
                entry.delete(0, tk.END)

            load_records()
            messagebox.showinfo("Success", "Vaccination saved.", parent=parent)

        except Exception as error:
            messagebox.showerror(
                "Unable to Save",
                f"Check the Animal ID and dates.\n\n{error}",
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def delete_record():
        selected = table.selection()
        if not selected:
            messagebox.showwarning(
                "Select Record", "Select a vaccination first.", parent=parent
            )
            return

        record_id = table.item(selected[0], "values")[0]

        if not messagebox.askyesno("Confirm", "Delete this record?", parent=parent):
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM vaccinations WHERE vaccination_id = %s",
                (record_id,)
            )
            connection.commit()
            load_records()

        except Exception as error:
            messagebox.showerror("Delete Failed", str(error), parent=parent)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    buttons = tk.Frame(parent, bg=BG_COLOR)
    buttons.pack(anchor="w")

    tk.Button(
        buttons, text="Save Vaccination", command=add_record,
        bg=PRIMARY_COLOR, fg="white", font=(FONT, 10, "bold"),
        relief="flat", padx=12, pady=7
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        buttons, text="Delete Selected", command=delete_record
    ).pack(side="left")

    load_records()

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from style import BG_COLOR, CARD_COLOR, PRIMARY_COLOR, TEXT_COLOR, FONT


def show_feeding(parent, user=None):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent, text="Feeding Records",
        font=(FONT, 21, "bold"), bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(anchor="w", pady=(0, 15))

    form = tk.Frame(parent, bg=CARD_COLOR, padx=12, pady=12)
    form.pack(fill="x")

    fields = [
        ("Animal ID", "animal"),
        ("Feed Type", "feed"),
        ("Quantity", "quantity"),
        ("Unit (kg, g, etc.)", "unit"),
        ("Date (YYYY-MM-DD)", "date"),
        ("Time (HH:MM:SS)", "time"),
        ("Notes", "notes")
    ]
    entries = {}

    for index, (label, key) in enumerate(fields):
        tk.Label(
            form, text=label, bg=CARD_COLOR, font=(FONT, 9)
        ).grid(row=0, column=index, sticky="w", padx=3)

        entry = tk.Entry(form, font=(FONT, 9), width=15)
        entry.grid(row=1, column=index, padx=3, pady=5)
        entries[key] = entry

    table = ttk.Treeview(
        parent,
        columns=("id", "animal", "feed", "quantity", "unit", "date", "time", "notes"),
        show="headings",
        height=12
    )

    for col, title in [
        ("id", "ID"), ("animal", "Animal ID"), ("feed", "Feed Type"),
        ("quantity", "Quantity"), ("unit", "Unit"), ("date", "Date"),
        ("time", "Time"), ("notes", "Notes")
    ]:
        table.heading(col, text=title)
        table.column(col, width=105)

    table.pack(fill="both", expand=True, pady=15)

    def load_records():
        table.delete(*table.get_children())
        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT feeding_id, animal_id, feed_type, quantity, unit,
                       feeding_date, feeding_time, notes
                FROM feeding_records
                ORDER BY feeding_date DESC, feeding_time DESC
            """)
            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        except Exception as error:
            messagebox.showerror("Database Error", str(error), parent=parent)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def add_record():
        animal = entries["animal"].get().strip()
        feed = entries["feed"].get().strip()
        quantity = entries["quantity"].get().strip()
        unit = entries["unit"].get().strip()
        date_given = entries["date"].get().strip()
        time_given = entries["time"].get().strip() or None
        notes = entries["notes"].get().strip() or None

        if not animal or not feed or not date_given:
            messagebox.showwarning(
                "Required Fields",
                "Animal ID, Feed Type, and Date are required.",
                parent=parent
            )
            return

        connection = None
        cursor = None

        try:
            quantity_value = float(quantity) if quantity else None
            if quantity_value is not None and quantity_value < 0:
                raise ValueError("Quantity cannot be negative.")

            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO feeding_records
                    (animal_id, feed_type, quantity, unit,
                     feeding_date, feeding_time, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                int(animal), feed, quantity_value, unit or None,
                date_given, time_given, notes
            ))
            connection.commit()

            for entry in entries.values():
                entry.delete(0, tk.END)

            load_records()
            messagebox.showinfo("Success", "Feeding record saved.", parent=parent)

        except Exception as error:
            messagebox.showerror(
                "Unable to Save", f"Check your entries.\n\n{error}", parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def delete_record():
        selected = table.selection()
        if not selected:
            messagebox.showwarning(
                "Select Record", "Select a feeding record first.", parent=parent
            )
            return

        record_id = table.item(selected[0], "values")[0]

        if not messagebox.askyesno("Confirm", "Delete this record?", parent=parent):
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM feeding_records WHERE feeding_id = %s",
                (record_id,)
            )
            connection.commit()
            load_records()

        except Exception as error:
            messagebox.showerror("Delete Failed", str(error), parent=parent)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    buttons = tk.Frame(parent, bg=BG_COLOR)
    buttons.pack(anchor="w")

    tk.Button(
        buttons, text="Save Feeding Record", command=add_record,
        bg=PRIMARY_COLOR, fg="white", font=(FONT, 10, "bold"),
        relief="flat", padx=12, pady=7
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        buttons, text="Delete Selected", command=delete_record
    ).pack(side="left")

    load_records()

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import get_connection
from style import BG_COLOR, CARD_COLOR, PRIMARY_COLOR, TEXT_COLOR, FONT


def show_health_records(parent, user=None):
    for widget in parent.winfo_children():
        widget.destroy()

    # Page title
    tk.Label(
        parent,
        text="Animal Health Records",
        font=(FONT, 21, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", pady=(0, 15))

    # Form
    form = tk.Frame(parent, bg=CARD_COLOR, padx=12, pady=12)
    form.pack(fill="x")

    fields = [
        ("Animal ID", "animal"),
        ("Date (YYYY-MM-DD)", "date"),
        ("Condition", "condition"),
        ("Treatment", "treatment"),
        ("Veterinarian", "vet"),
        ("Notes", "notes")
    ]

    entries = {}

    for index, (label, key) in enumerate(fields):
        tk.Label(
            form,
            text=label,
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=(FONT, 9)
        ).grid(row=0, column=index, sticky="w", padx=4)

        if key == "condition":
            entry = ttk.Combobox(
                form,
                values=[
                    "Healthy",
                    "Sick",
                    "Injured",
                    "Recovering",
                    "Under Observation"
                ],
                state="readonly",
                font=(FONT, 10),
                width=16
            )
            entry.set("Healthy")
        else:
            entry = tk.Entry(
                form,
                font=(FONT, 10),
                width=18
            )

        entry.grid(row=1, column=index, padx=4, pady=5)
        entries[key] = entry

    for index in range(len(fields)):
        form.columnconfigure(index, weight=1)

    # Table
    table_frame = tk.Frame(parent, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, pady=15)

    columns = (
        "id", "animal", "date", "condition",
        "treatment", "vet", "notes"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=12
    )

    headings = {
        "id": "Health ID",
        "animal": "Animal ID",
        "date": "Date",
        "condition": "Condition",
        "treatment": "Treatment",
        "vet": "Veterinarian",
        "notes": "Notes"
    }

    for col in columns:
        table.heading(col, text=headings[col])
        table.column(col, width=130, anchor="center")

    table.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )
    scrollbar.pack(side="right", fill="y")
    table.configure(yscrollcommand=scrollbar.set)

    # Remember the ID of the record being edited
    selected_health_id = {"id": None}

    # Load records from database
    def load_records():
        table.delete(*table.get_children())

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    health_id,
                    animal_id,
                    record_date,
                    condition_name,
                    treatment,
                    veterinarian,
                    notes
                FROM health_records
                ORDER BY record_date DESC, health_id DESC
            """)

            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error),
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Clear form
    def clear_form():
        for key, entry in entries.items():
            if key == "condition":
                entry.set("Healthy")
            else:
                entry.delete(0, tk.END)

        selected_health_id["id"] = None
        table.selection_remove(table.selection())

    # Load selected record into form
    def load_selected():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a health record from the table.",
                parent=parent
            )
            return

        values = table.item(selected[0], "values")

        selected_health_id["id"] = values[0]

        entries["animal"].delete(0, tk.END)
        entries["animal"].insert(0, values[1] or "")

        entries["date"].delete(0, tk.END)
        entries["date"].insert(0, values[2] or "")

        condition = values[3] or "Healthy"
        if condition in entries["condition"]["values"]:
            entries["condition"].set(condition)
        else:
            entries["condition"].set("Healthy")

        entries["treatment"].delete(0, tk.END)
        entries["treatment"].insert(0, values[4] or "")

        entries["vet"].delete(0, tk.END)
        entries["vet"].insert(0, values[5] or "")

        entries["notes"].delete(0, tk.END)
        entries["notes"].insert(0, values[6] or "")

    # Validate form values
    def get_form_values():
        animal_text = entries["animal"].get().strip()
        record_date = entries["date"].get().strip()
        condition = entries["condition"].get().strip()

        if not animal_text or not record_date or not condition:
            messagebox.showwarning(
                "Required Fields",
                "Animal ID, Date, and Condition are required.",
                parent=parent
            )
            return None

        try:
            animal_id = int(animal_text)
            if animal_id <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid Animal ID",
                "Animal ID must be a positive whole number.",
                parent=parent
            )
            return None

        try:
            datetime.strptime(record_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Use YYYY-MM-DD, for example 2026-10-15.",
                parent=parent
            )
            return None

        allowed_conditions = [
            "Healthy",
            "Sick",
            "Injured",
            "Recovering",
            "Under Observation"
        ]

        if condition not in allowed_conditions:
            messagebox.showwarning(
                "Invalid Condition",
                "Please select a valid condition.",
                parent=parent
            )
            return None

        return (
            animal_id,
            record_date,
            condition,
            entries["treatment"].get().strip() or None,
            entries["vet"].get().strip() or None,
            entries["notes"].get().strip() or None
        )

    # Check whether an animal exists
    def animal_exists(cursor, animal_id):
        cursor.execute(
            "SELECT animal_id FROM animals WHERE animal_id = %s",
            (animal_id,)
        )
        return cursor.fetchone() is not None

    # Add a new health record
    def add_record():
        values = get_form_values()

        if values is None:
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            if not animal_exists(cursor, values[0]):
                messagebox.showwarning(
                    "Animal Not Found",
                    "The Animal ID does not exist.",
                    parent=parent
                )
                return

            cursor.execute("""
                INSERT INTO health_records (
                    animal_id, record_date, condition_name,
                    treatment, veterinarian, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, values)

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Health record saved successfully.",
                parent=parent
            )

            clear_form()
            load_records()

        except Exception as error:
            if connection and connection.is_connected():
                connection.rollback()

            messagebox.showerror(
                "Save Failed",
                str(error),
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Update selected health record
    def update_record():
        health_id = selected_health_id["id"]

        if health_id is None:
            messagebox.showwarning(
                "No Record Loaded",
                "Select a record, then click LOAD SELECTED before updating.",
                parent=parent
            )
            return

        values = get_form_values()

        if values is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Update",
            "Are you sure you want to update this health record?",
            parent=parent
        )

        if not confirm:
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            if not animal_exists(cursor, values[0]):
                messagebox.showwarning(
                    "Animal Not Found",
                    "The Animal ID does not exist.",
                    parent=parent
                )
                return

            cursor.execute("""
                UPDATE health_records
                SET
                    animal_id = %s,
                    record_date = %s,
                    condition_name = %s,
                    treatment = %s,
                    veterinarian = %s,
                    notes = %s
                WHERE health_id = %s
            """, values + (health_id,))

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Health record updated successfully.",
                parent=parent
            )

            clear_form()
            load_records()

        except Exception as error:
            if connection and connection.is_connected():
                connection.rollback()

            messagebox.showerror(
                "Update Failed",
                str(error),
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Delete selected health record
    def delete_record():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a health record to delete.",
                parent=parent
            )
            return

        health_id = table.item(selected[0], "values")[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this health record?",
            parent=parent
        )

        if not confirm:
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM health_records WHERE health_id = %s",
                (health_id,)
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Health record deleted successfully.",
                parent=parent
            )

            clear_form()
            load_records()

        except Exception as error:
            if connection and connection.is_connected():
                connection.rollback()

            messagebox.showerror(
                "Delete Failed",
                str(error),
                parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Buttons
    buttons = tk.Frame(parent, bg=BG_COLOR)
    buttons.pack(anchor="w", pady=(0, 10))

    tk.Button(
        buttons,
        text="Save Health Record",
        command=add_record,
        bg=PRIMARY_COLOR,
        fg="white",
        font=(FONT, 10, "bold"),
        relief="flat",
        padx=12,
        pady=7
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        buttons,
        text="Load Selected",
        command=load_selected,
        font=(FONT, 10),
        padx=12,
        pady=7
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        buttons,
        text="Update Selected",
        command=update_record,
        font=(FONT, 10),
        padx=12,
        pady=7
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        buttons,
        text="Clear Form",
        command=clear_form,
        font=(FONT, 10),
        padx=12,
        pady=7
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        buttons,
        text="Delete Selected",
        command=delete_record,
        font=(FONT, 10),
        padx=12,
        pady=7
    ).pack(side="left")

    # Load records when page opens
    load_records()

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from style import BG_COLOR, CARD_COLOR, PRIMARY_COLOR, TEXT_COLOR, FONT


def show_breeding(parent, user=None):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent, text="Breeding History",
        font=(FONT, 21, "bold"), bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(anchor="w", pady=(0, 15))

    form = tk.Frame(parent, bg=CARD_COLOR, padx=12, pady=12)
    form.pack(fill="x")

    fields = [
        ("Animal ID", "animal"),
        ("Mate Tag Number", "mate"),
        ("Breeding Date", "breeding"),
        ("Expected Birth Date", "expected"),
        ("Actual Birth Date", "actual"),
        ("Offspring Count", "offspring"),
        ("Notes", "notes")
    ]
    entries = {}

    for index, (label, key) in enumerate(fields):
        tk.Label(
            form, text=label, bg=CARD_COLOR, font=(FONT, 9)
        ).grid(row=0, column=index, sticky="w", padx=3)

        entry = tk.Entry(form, font=(FONT, 9), width=16)
        entry.grid(row=1, column=index, padx=3, pady=5)
        entries[key] = entry

    table = ttk.Treeview(
        parent,
        columns=("id", "animal", "mate", "breeding", "expected", "actual", "offspring", "notes"),
        show="headings",
        height=12
    )

    for col, title in [
        ("id", "ID"), ("animal", "Animal ID"), ("mate", "Mate Tag"),
        ("breeding", "Breeding Date"), ("expected", "Expected Birth"),
        ("actual", "Actual Birth"), ("offspring", "Offspring"),
        ("notes", "Notes")
    ]:
        table.heading(col, text=title)
        table.column(col, width=115)

    table.pack(fill="both", expand=True, pady=15)

    def load_records():
        table.delete(*table.get_children())
        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT breeding_id, animal_id, mate_tag_number,
                       breeding_date, expected_birth_date,
                       actual_birth_date, offspring_count, notes
                FROM breeding_records
                ORDER BY breeding_date DESC
            """)
            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        except Exception as error:
            messagebox.showerror("Database Error", str(error), parent=parent)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def add_record():
        animal = entries["animal"].get().strip()
        breeding_date = entries["breeding"].get().strip()

        if not animal or not breeding_date:
            messagebox.showwarning(
                "Required Fields",
                "Animal ID and Breeding Date are required.",
                parent=parent
            )
            return

        expected = entries["expected"].get().strip() or None
        actual = entries["actual"].get().strip() or None
        mate = entries["mate"].get().strip() or None
        notes = entries["notes"].get().strip() or None

        connection = None
        cursor = None

        try:
            offspring_text = entries["offspring"].get().strip()
            offspring = int(offspring_text) if offspring_text else 0

            if offspring < 0:
                raise ValueError("Offspring count cannot be negative.")

            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO breeding_records
                    (animal_id, mate_tag_number, breeding_date,
                     expected_birth_date, actual_birth_date,
                     offspring_count, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                int(animal), mate, breeding_date, expected,
                actual, offspring, notes
            ))
            connection.commit()

            for entry in entries.values():
                entry.delete(0, tk.END)

            load_records()
            messagebox.showinfo("Success", "Breeding record saved.", parent=parent)

        except Exception as error:
            messagebox.showerror(
                "Unable to Save", f"Check your entries.\n\n{error}", parent=parent
            )

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def delete_record():
        selected = table.selection()
        if not selected:
            messagebox.showwarning(
                "Select Record", "Select a breeding record first.", parent=parent
            )
            return

        record_id = table.item(selected[0], "values")[0]

        if not messagebox.askyesno("Confirm", "Delete this record?", parent=parent):
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM breeding_records WHERE breeding_id = %s",
                (record_id,)
            )
            connection.commit()
            load_records()

        except Exception as error:
            messagebox.showerror("Delete Failed", str(error), parent=parent)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    buttons = tk.Frame(parent, bg=BG_COLOR)
    buttons.pack(anchor="w")

    tk.Button(
        buttons, text="Save Breeding Record", command=add_record,
        bg=PRIMARY_COLOR, fg="white", font=(FONT, 10, "bold"),
        relief="flat", padx=12, pady=7
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        buttons, text="Delete Selected", command=delete_record
    ).pack(side="left")

    load_records()

import tkinter as tk
from tkinter import messagebox
from database import get_connection, hash_password, verify_password
from style import BG_COLOR, CARD_COLOR, PRIMARY_COLOR, TEXT_COLOR, MUTED_COLOR, FONT


def show_profile(parent, user=None):
    for widget in parent.winfo_children():
        widget.destroy()

    if not user or not user.get("user_id"):
        tk.Label(
            parent,
            text="No logged-in user was provided.",
            font=(FONT, 12),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        ).pack(anchor="w")
        return

    tk.Label(
        parent, text="My Profile",
        font=(FONT, 21, "bold"), bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(anchor="w", pady=(0, 15))

    card = tk.Frame(parent, bg=CARD_COLOR, padx=25, pady=25)
    card.pack(fill="x", anchor="n")

    tk.Label(
        card, text="Account Information",
        font=(FONT, 16, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR
    ).pack(anchor="w", pady=(0, 15))

    tk.Label(
        card, text="Username (cannot be changed here)",
        font=(FONT, 10), bg=CARD_COLOR, fg=MUTED_COLOR
    ).pack(anchor="w")

    username_entry = tk.Entry(card, font=(FONT, 11))
    username_entry.pack(fill="x", pady=(4, 12))
    username_entry.insert(0, user.get("username", ""))
    username_entry.config(state="readonly")

    tk.Label(
        card, text="Full Name",
        font=(FONT, 10), bg=CARD_COLOR, fg=TEXT_COLOR
    ).pack(anchor="w")

    name_entry = tk.Entry(card, font=(FONT, 11))
    name_entry.pack(fill="x", pady=(4, 12))
    name_entry.insert(0, user.get("full_name", ""))

    tk.Label(
        card, text="Role",
        font=(FONT, 10), bg=CARD_COLOR, fg=MUTED_COLOR
    ).pack(anchor="w")

    tk.Label(
        card, text=user.get("role", "Staff"),
        font=(FONT, 11, "bold"), bg=CARD_COLOR, fg=PRIMARY_COLOR
    ).pack(anchor="w", pady=(4, 15))

    def save_profile():
        full_name = name_entry.get().strip()

        if not full_name:
            messagebox.showwarning(
                "Required Field", "Full name cannot be empty.", parent=parent
            )
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET full_name = %s WHERE user_id = %s",
                (full_name, user["user_id"])
            )
            connection.commit()

            user["full_name"] = full_name

            messagebox.showinfo(
                "Success", "Profile updated successfully.", parent=parent
            )

        except Exception as error:
            messagebox.showerror("Update Failed", str(error), parent=parent)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    tk.Button(
        card, text="Save Profile", command=save_profile,
        bg=PRIMARY_COLOR, fg="white", font=(FONT, 10, "bold"),
        relief="flat", padx=12, pady=8
    ).pack(anchor="w", pady=(0, 25))

    tk.Label(
        card, text="Change Password",
        font=(FONT, 16, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR
    ).pack(anchor="w", pady=(0, 12))

    def password_field(label, show="*"):
        tk.Label(
            card, text=label,
            font=(FONT, 10), bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w")

        entry = tk.Entry(card, font=(FONT, 11), show=show)
        entry.pack(fill="x", pady=(4, 10))
        return entry

    current_password = password_field("Current Password")
    new_password = password_field("New Password")
    confirm_password = password_field("Confirm New Password")

    def change_password():
        current = current_password.get()
        new = new_password.get()
        confirm = confirm_password.get()

        if not current or not new or not confirm:
            messagebox.showwarning(
                "Missing Information",
                "Complete all password fields.",
                parent=parent
            )
            return

        if len(new) < 8:
            messagebox.showwarning(
                "Weak Password",
                "Use at least 8 characters for your new password.",
                parent=parent
            )
            return

        if new != confirm:
            messagebox.showerror(
                "Password Mismatch",
                "The new passwords do not match.",
                parent=parent
            )
            return

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT password_hash, password_salt
                FROM users WHERE user_id = %s
            """, (user["user_id"],))

            account = cursor.fetchone()

            if not account or not verify_password(
                current,
                account["password_salt"],
                account["password_hash"]
            ):
                messagebox.showerror(
                    "Incorrect Password",
                    "Your current password is incorrect.",
                    parent=parent
                )
                return

            salt, password_hash = hash_password(new)

            cursor.execute("""
                UPDATE users
                SET password_hash = %s, password_salt = %s
                WHERE user_id = %s
            """, (password_hash, salt, user["user_id"]))

            connection.commit()

            current_password.delete(0, tk.END)
            new_password.delete(0, tk.END)
            confirm_password.delete(0, tk.END)

            messagebox.showinfo(
                "Success", "Password changed successfully.", parent=parent
            )

        except Exception as error:
            messagebox.showerror("Update Failed", str(error), parent=parent)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    tk.Button(
        card, text="Change Password", command=change_password,
        bg=PRIMARY_COLOR, fg="white", font=(FONT, 10, "bold"),
        relief="flat", padx=12, pady=8
    ).pack(anchor="w")

PAGE_FUNCTIONS = {
    "Dashboard": show_dashboard,
    "Animals": show_animals,
    "Vaccination": show_vaccination,
    "Feeding": show_feeding,
    "Health Records": show_health_records,
    "Breeding": show_breeding,
    "Profile": show_profile,
}

def show_page(parent, page_name, user=None):
    page_function = PAGE_FUNCTIONS.get(page_name)
    if page_function is None:
        raise ValueError(f"Unknown page: {page_name}")
    page_function(parent, user=user)
