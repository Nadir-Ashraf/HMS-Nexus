"""
Visitors Management View for HMS Desktop Application.
Enables Wardens and Admins to log, track, and manage visitor entries and exits.
"""
from datetime import date, datetime
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, ModalDialog, StatusBadge
from app import db_service

class VisitorsView(ctk.CTkFrame):
    def __init__(self, master, current_user=None):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user

        # Header
        self.header = PageHeader(
            self,
            title="Visitor Gate Register",
            subtitle="Security gate log for guest arrivals, departures, and student visits",
            action_text="🚪 + Log Visitor",
            action_cmd=self._open_add_visitor_dialog,
            action_color=theme.PRIMARY
        )
        self.header.pack(fill="x", padx=20, pady=(16, 12))

        # Filter and Search Bar
        filter_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        filter_card.pack(fill="x", padx=20, pady=(0, 14))

        filter_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_inner.pack(fill="x", padx=16, pady=12)

        self.seg_filter = ctk.CTkSegmentedButton(
            filter_inner,
            values=["All Visitors", "On Premises", "Departed"],
            command=lambda v: self.load_visitors()
        )
        self.seg_filter.set("All Visitors")
        self.seg_filter.pack(side="left", padx=(0, 12))

        self.entry_search = ctk.CTkEntry(
            filter_inner,
            placeholder_text="🔍 Search visitor name, phone, or student...",
            font=theme.FONT_BODY,
            height=34,
            corner_radius=theme.RADIUS_ENTRY
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_visitors())

        btn_refresh = ctk.CTkButton(
            filter_inner,
            text="🔄 Refresh",
            width=80,
            height=34,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            command=self.load_visitors
        )
        btn_refresh.pack(side="left")

        # Table Container
        table_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Table Header
        header_row = ctk.CTkFrame(table_card, fg_color=theme.BG_CARD_ALT, height=40, corner_radius=8)
        header_row.pack(fill="x", padx=12, pady=(12, 6))
        header_row.pack_propagate(False)

        cols = [
            ("Visitor Name", 140),
            ("Phone", 110),
            ("Student Visited", 160),
            ("Date", 90),
            ("Time In", 75),
            ("Time Out", 75),
            ("Purpose", 190),
            ("Action / Status", 110)
        ]
        for name, width in cols:
            ctk.CTkLabel(header_row, text=name, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=width, anchor="w").pack(side="left", padx=6)

        self.table_body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.load_visitors()

    def load_visitors(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        visitors = db_service.get_all_visitors()
        if not visitors:
            ctk.CTkLabel(self.table_body, text="No visitor entries logged yet.", font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=40)
            return

        filter_val = self.seg_filter.get()
        search_query = self.entry_search.get().strip().lower()

        filtered = []
        for v in visitors:
            # Status filter
            is_on_premise = v['time_out'] == '-'
            if filter_val == "On Premises" and not is_on_premise:
                continue
            if filter_val == "Departed" and is_on_premise:
                continue

            # Text search filter
            if search_query:
                combined = f"{v['visitor_name']} {v['phone']} {v['student_name']} {v['student_code']} {v['purpose']}".lower()
                if search_query not in combined:
                    continue

            filtered.append(v)

        if not filtered:
            ctk.CTkLabel(self.table_body, text="No visitor logs matching filters.", font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=40)
            return

        for idx, v in enumerate(filtered):
            bg = theme.BG_CARD if idx % 2 == 0 else theme.BG_CARD_ALT
            row = ctk.CTkFrame(self.table_body, fg_color=bg, height=48, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=v['visitor_name'], font=theme.FONT_BODY_BOLD, width=140, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=v['phone'], font=theme.FONT_BODY, width=110, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=f"{v['student_name']} ({v['student_code']})", font=theme.FONT_BODY, width=160, anchor="w", text_color=theme.PRIMARY).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=v['date'], font=theme.FONT_BODY, width=90, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=v['time_in'], font=theme.FONT_BODY, width=75, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=6)
            
            # Time Out label
            time_out_color = theme.TEXT_MUTED if v['time_out'] == '-' else theme.TEXT_SECONDARY
            ctk.CTkLabel(row, text=v['time_out'], font=theme.FONT_BODY, width=75, anchor="w", text_color=time_out_color).pack(side="left", padx=6)
            
            ctk.CTkLabel(row, text=v['purpose'], font=theme.FONT_BODY, width=190, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=6)

            # Action Frame
            action_frame = ctk.CTkFrame(row, fg_color="transparent", width=110)
            action_frame.pack(side="left", padx=6)

            if v['time_out'] == '-':
                btn_out = ctk.CTkButton(
                    action_frame,
                    text="🚪 Check Out",
                    font=theme.FONT_SMALL,
                    width=96,
                    height=28,
                    fg_color=theme.WARNING,
                    hover_color=theme.WARNING_HOVER,
                    command=lambda vid=v['id']: self._checkout_visitor(vid)
                )
                btn_out.pack(anchor="w")
            else:
                ctk.CTkLabel(action_frame, text="✓ Departed", font=theme.FONT_SMALL, text_color=theme.SUCCESS).pack(anchor="w")

    def _checkout_visitor(self, visitor_id):
        confirm = messagebox.askyesno(
            "Confirm Checkout",
            "Mark visitor as checked out at the current time?",
            parent=self.winfo_toplevel()
        )
        if confirm:
            ok, msg = db_service.checkout_visitor(visitor_id)
            if ok:
                messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
                self.load_visitors()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def _open_add_visitor_dialog(self):
        students = db_service.get_all_students()
        if not students:
            messagebox.showwarning("No Students", "Please register students first.", parent=self.winfo_toplevel())
            return

        dlg = ModalDialog(self.winfo_toplevel(), title="Log New Visitor", width=480, height=520)

        student_displays = [f"{s['student_id_str']} - {s['name']}" for s in students]
        e_student = ctk.CTkOptionMenu(dlg.body, values=student_displays)
        dlg.add_field("Select Student Visited *", e_student)

        e_name = dlg.add_field("Visitor Full Name *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. Robert Smith"))
        e_phone = dlg.add_field("Contact Phone *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. 9876543210"))
        
        e_date = dlg.add_field("Date (YYYY-MM-DD) *", ctk.CTkEntry(dlg.body, placeholder_text=str(date.today())))
        e_date.insert(0, str(date.today()))

        curr_time = datetime.now().strftime("%H:%M")
        e_time = dlg.add_field("Time In (HH:MM) *", ctk.CTkEntry(dlg.body, placeholder_text=curr_time))
        e_time.insert(0, curr_time)

        e_purpose = dlg.add_field("Purpose of Visit *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. Family visit / Book delivery"))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            chosen_stu = e_student.get()
            name = e_name.get().strip()
            phone = e_phone.get().strip()
            v_date = e_date.get().strip()
            v_time = e_time.get().strip()
            purpose = e_purpose.get().strip()

            stu_code = chosen_stu.split(" - ")[0]
            stu_obj = next((s for s in students if s["student_id_str"] == stu_code), None)

            if not (stu_obj and name and phone and purpose):
                lbl_msg.configure(text="Please fill in all visitor details.")
                return

            ok, res = db_service.add_visitor(stu_obj["id"], name, phone, v_date, v_time, purpose)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_visitors()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Save Entry", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
