"""
Warden Dashboard / Console View for HMS Desktop Application.
Provides Hostel Wardens with operational controls for daily attendance,
visitor security entries, leave request approvals, complaint resolution, and notices.
"""
from datetime import date
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, StatCard, StatusBadge, ModalDialog
from app import db_service

class WardenDashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, current_user, navigate_to):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.navigate_to = navigate_to

        # Header
        self.header = PageHeader(
            self,
            title="Warden Console",
            subtitle=f"Hostel Supervision • Today: {date.today().strftime('%A, %d %B %Y')}",
            action_text="🔄 Refresh",
            action_cmd=self.refresh,
            action_color=theme.SECONDARY
        )
        self.header.pack(fill="x", padx=20, pady=(16, 18))

        # Stats Row (4 Metric Cards)
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 16))
        for col in range(4):
            self.stats_frame.grid_columnconfigure(col, weight=1, uniform="warden_stat")

        self.card_attendance = StatCard(self.stats_frame, "Today's Attendance", "-", "📅", theme.SUCCESS)
        self.card_attendance.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_visitors = StatCard(self.stats_frame, "Visitors Today", "0", "🚪", theme.PRIMARY)
        self.card_visitors.grid(row=0, column=1, padx=4, sticky="ew")

        self.card_leaves = StatCard(self.stats_frame, "Pending Leaves", "0", "📝", theme.WARNING)
        self.card_leaves.grid(row=0, column=2, padx=4, sticky="ew")

        self.card_complaints = StatCard(self.stats_frame, "Active Complaints", "0", "⚠️", theme.DANGER)
        self.card_complaints.grid(row=0, column=3, padx=(8, 0), sticky="ew")

        # Quick Actions Card
        self._build_quick_actions()

        # Two-Column Operations Section: Pending Leaves & Pending Complaints
        self.ops_container = ctk.CTkFrame(self, fg_color="transparent")
        self.ops_container.pack(fill="x", padx=20, pady=(0, 20))
        self.ops_container.grid_columnconfigure(0, weight=1, uniform="ops_col")
        self.ops_container.grid_columnconfigure(1, weight=1, uniform="ops_col")

        # Left: Pending Leaves Card
        self.leaves_card = ctk.CTkFrame(
            self.ops_container,
            fg_color=theme.BG_CARD,
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        self.leaves_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Right: Pending Complaints Card
        self.complaints_card = ctk.CTkFrame(
            self.ops_container,
            fg_color=theme.BG_CARD,
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        self.complaints_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Bottom Section: Notice Board Highlights
        self._build_notices_section()

        # Initial data load
        self.refresh()

    def _build_quick_actions(self):
        qa_card = ctk.CTkFrame(
            self,
            corner_radius=theme.RADIUS_CARD,
            fg_color=theme.BG_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        qa_card.pack(fill="x", padx=20, pady=(0, 18))

        lbl = ctk.CTkLabel(
            qa_card,
            text="⚡ Operational Shortcuts",
            font=theme.FONT_SECTION_TITLE,
            text_color=theme.TEXT_PRIMARY
        )
        lbl.pack(anchor="w", padx=20, pady=(14, 10))

        btn_row = ctk.CTkFrame(qa_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        actions = [
            ("📅 Mark Attendance", lambda: self.navigate_to("attendance"), theme.PRIMARY),
            ("🚪 Log Visitor Entry", lambda: self.navigate_to("visitors"), theme.PRIMARY),
            ("📝 Review Leaves", lambda: self.navigate_to("leaves"), theme.WARNING),
            ("⚠️ Resolve Complaints", lambda: self.navigate_to("complaints"), theme.DANGER),
            ("📢 Publish Notice", self._open_publish_notice_dialog, theme.INFO),
            ("🎓 Student Directory", lambda: self.navigate_to("students"), theme.BG_CARD_ALT),
        ]

        for text, cmd, col in actions:
            text_col = theme.TEXT_PRIMARY if col == theme.BG_CARD_ALT else "#FFFFFF"
            btn = ctk.CTkButton(
                btn_row,
                text=text,
                font=theme.FONT_BODY_BOLD,
                height=38,
                fg_color=col,
                text_color=text_col,
                hover_color=theme.PRIMARY_HOVER if col != theme.BG_CARD_ALT else theme.BG_ROW_HOVER,
                corner_radius=theme.RADIUS_BUTTON,
                command=cmd
            )
            btn.pack(side="left", padx=(0, 8), expand=True, fill="x")

    def _build_notices_section(self):
        self.notices_card = ctk.CTkFrame(
            self,
            corner_radius=theme.RADIUS_CARD,
            fg_color=theme.BG_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        self.notices_card.pack(fill="x", padx=20, pady=(0, 24))

        top = ctk.CTkFrame(self.notices_card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(16, 10))

        ctk.CTkLabel(
            top,
            text="📢 Recent Hostel Announcements",
            font=theme.FONT_SECTION_TITLE,
            text_color=theme.TEXT_PRIMARY
        ).pack(side="left")

        btn_box = ctk.CTkFrame(top, fg_color="transparent")
        btn_box.pack(side="right")

        ctk.CTkButton(
            btn_box,
            text="+ Post Notice",
            font=theme.FONT_SMALL,
            width=100,
            height=28,
            fg_color=theme.PRIMARY,
            command=self._open_publish_notice_dialog
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_box,
            text="View Board →",
            font=theme.FONT_SMALL,
            width=90,
            height=28,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            command=lambda: self.navigate_to("notices")
        ).pack(side="left")

        self.notices_body = ctk.CTkFrame(self.notices_card, fg_color="transparent")
        self.notices_body.pack(fill="x", padx=20, pady=(0, 16))

    def refresh(self):
        stats = db_service.get_warden_dashboard_stats()

        # Update metric cards
        att = stats["attendance"]
        if att["marked"]:
            att_display = f"{att['present']} / {att['total_students']} Pres."
        else:
            att_display = "Not Marked"
        self.card_attendance.update_value(att_display)

        vis_display = f"{stats['visitors_today']} ({stats['active_visitors']} in)"
        self.card_visitors.update_value(vis_display)
        self.card_leaves.update_value(f"{stats['pending_leaves']} Pending")
        self.card_complaints.update_value(f"{stats['pending_complaints']} Active")

        # Populate Pending Leaves Section
        self._render_leaves_list(stats["recent_leaves"], stats["pending_leaves"])

        # Populate Pending Complaints Section
        self._render_complaints_list(stats["recent_complaints"], stats["pending_complaints"])

        # Populate Notices Section
        self._render_notices_list(stats["recent_notices"])

    def _render_leaves_list(self, leaves, total_pending):
        for w in self.leaves_card.winfo_children():
            w.destroy()

        top = ctk.CTkFrame(self.leaves_card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(
            top,
            text=f"📝 Pending Leaves ({total_pending})",
            font=theme.FONT_SECTION_TITLE,
            text_color=theme.TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="All Leaves →",
            font=theme.FONT_SMALL,
            width=80,
            height=26,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            command=lambda: self.navigate_to("leaves")
        ).pack(side="right")

        if not leaves:
            ctk.CTkLabel(
                self.leaves_card,
                text="✓ No pending leave requests.\nAll student leave passes are cleared.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED,
                justify="center"
            ).pack(pady=36)
            return

        for l in leaves:
            item = ctk.CTkFrame(self.leaves_card, fg_color=theme.BG_CARD_ALT, corner_radius=8)
            item.pack(fill="x", padx=14, pady=4)

            i_top = ctk.CTkFrame(item, fg_color="transparent")
            i_top.pack(fill="x", padx=10, pady=(8, 2))

            ctk.CTkLabel(
                i_top,
                text=f"{l['student_name']} ({l['student_code']})",
                font=theme.FONT_BODY_BOLD,
                text_color=theme.TEXT_PRIMARY
            ).pack(side="left")

            ctk.CTkLabel(
                i_top,
                text=f"{l['start_date']} to {l['end_date']}",
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_SECONDARY
            ).pack(side="right")

            # Reason & Actions Row
            i_bot = ctk.CTkFrame(item, fg_color="transparent")
            i_bot.pack(fill="x", padx=10, pady=(2, 8))

            ctk.CTkLabel(
                i_bot,
                text=l['reason'],
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_MUTED,
                anchor="w",
                wraplength=260
            ).pack(side="left", fill="x", expand=True)

            act_box = ctk.CTkFrame(i_bot, fg_color="transparent")
            act_box.pack(side="right")

            ctk.CTkButton(
                act_box,
                text="✓ Approve",
                font=theme.FONT_SMALL,
                width=64,
                height=26,
                fg_color=theme.SUCCESS,
                hover_color=theme.SUCCESS_HOVER,
                command=lambda lid=l["id"]: self._quick_update_leave(lid, "Approved")
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                act_box,
                text="✗ Reject",
                font=theme.FONT_SMALL,
                width=60,
                height=26,
                fg_color=theme.DANGER,
                hover_color=theme.DANGER_HOVER,
                command=lambda lid=l["id"]: self._quick_update_leave(lid, "Rejected")
            ).pack(side="left")

        # Bottom padding inside card
        ctk.CTkFrame(self.leaves_card, height=10, fg_color="transparent").pack()

    def _render_complaints_list(self, complaints, total_pending):
        for w in self.complaints_card.winfo_children():
            w.destroy()

        top = ctk.CTkFrame(self.complaints_card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(
            top,
            text=f"⚠️ Active Complaints ({total_pending})",
            font=theme.FONT_SECTION_TITLE,
            text_color=theme.TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="All Tickets →",
            font=theme.FONT_SMALL,
            width=80,
            height=26,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            command=lambda: self.navigate_to("complaints")
        ).pack(side="right")

        if not complaints:
            ctk.CTkLabel(
                self.complaints_card,
                text="✓ No active complaints.\nHostel facilities running smoothly.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED,
                justify="center"
            ).pack(pady=36)
            return

        for c in complaints:
            item = ctk.CTkFrame(self.complaints_card, fg_color=theme.BG_CARD_ALT, corner_radius=8)
            item.pack(fill="x", padx=14, pady=4)

            i_top = ctk.CTkFrame(item, fg_color="transparent")
            i_top.pack(fill="x", padx=10, pady=(8, 2))

            ctk.CTkLabel(
                i_top,
                text=f"🔧 {c['category']} - {c['student_name']}",
                font=theme.FONT_BODY_BOLD,
                text_color=theme.TEXT_PRIMARY
            ).pack(side="left")

            StatusBadge(i_top, c['priority']).pack(side="right")

            # Description & Resolve Button Row
            i_bot = ctk.CTkFrame(item, fg_color="transparent")
            i_bot.pack(fill="x", padx=10, pady=(2, 8))

            ctk.CTkLabel(
                i_bot,
                text=c['description'],
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_MUTED,
                anchor="w",
                wraplength=280
            ).pack(side="left", fill="x", expand=True)

            ctk.CTkButton(
                i_bot,
                text="✓ Resolve",
                font=theme.FONT_SMALL,
                width=72,
                height=26,
                fg_color=theme.SUCCESS,
                hover_color=theme.SUCCESS_HOVER,
                command=lambda cid=c["id"]: self._quick_resolve_complaint(cid)
            ).pack(side="right")

        # Bottom padding inside card
        ctk.CTkFrame(self.complaints_card, height=10, fg_color="transparent").pack()

    def _render_notices_list(self, notices):
        for w in self.notices_body.winfo_children():
            w.destroy()

        if not notices:
            ctk.CTkLabel(
                self.notices_body,
                text="No announcements published yet. Click '+ Post Notice' above to share an update.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED
            ).pack(pady=20)
            return

        for n in notices:
            row = ctk.CTkFrame(self.notices_body, fg_color=theme.BG_CARD_ALT, corner_radius=8)
            row.pack(fill="x", pady=3)

            r_top = ctk.CTkFrame(row, fg_color="transparent")
            r_top.pack(fill="x", padx=12, pady=(8, 2))

            ctk.CTkLabel(
                r_top,
                text=n['title'],
                font=theme.FONT_BODY_BOLD,
                text_color=theme.TEXT_PRIMARY
            ).pack(side="left")

            StatusBadge(r_top, n['category']).pack(side="right")

            desc = n.get('description', '')
            if desc:
                r_desc = ctk.CTkLabel(
                    row,
                    text=desc,
                    font=theme.FONT_SMALL,
                    text_color=theme.TEXT_SECONDARY,
                    anchor="w",
                    wraplength=850,
                    justify="left"
                )
                r_desc.pack(fill="x", padx=12, pady=(0, 4))

            r_bot = ctk.CTkFrame(row, fg_color="transparent")
            r_bot.pack(fill="x", padx=12, pady=(0, 6))

            ctk.CTkLabel(
                r_bot,
                text=f"📅 {n['date']}",
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_MUTED
            ).pack(side="left")

    def _quick_update_leave(self, leave_id, status):
        ok, msg = db_service.update_leave_status(leave_id, status)
        if ok:
            messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
            self.refresh()
        else:
            messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def _quick_resolve_complaint(self, complaint_id):
        confirm = messagebox.askyesno(
            "Confirm Resolution",
            "Mark this maintenance complaint as Resolved?",
            parent=self.winfo_toplevel()
        )
        if confirm:
            ok, msg = db_service.resolve_complaint(complaint_id)
            if ok:
                messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
                self.refresh()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def _open_publish_notice_dialog(self):
        dlg = ModalDialog(self.winfo_toplevel(), title="Publish Notice", width=500, height=520)

        e_title = dlg.add_field("Notice Title *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. Night Gate Closure Guidelines"))
        e_cat = ctk.CTkOptionMenu(dlg.body, values=["General", "Urgent", "Maintenance", "Mess / Food", "Security", "Events"])
        dlg.add_field("Category *", e_cat)

        e_desc = dlg.add_field("Description / Message *", ctk.CTkTextbox(dlg.body, height=140))
        e_expiry = dlg.add_field("Expiry Date (YYYY-MM-DD, Optional)", ctk.CTkEntry(dlg.body, placeholder_text="Leave blank for no expiry"))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            t = e_title.get().strip()
            c = e_cat.get()
            d = e_desc.get("1.0", "end-1c").strip()
            exp = e_expiry.get().strip()

            if not (t and d):
                lbl_msg.configure(text="Please provide both title and notice content.")
                return

            ok, res = db_service.add_notice(t, c, d, exp if exp else None)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.refresh()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Publish Notice", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
