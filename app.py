import flet as ft
from parser import parse_email


def main(page: ft.Page):
    page.title = "Opportunity Copilot | AI Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1100
    page.window_height = 900
    page.theme = ft.Theme(color_scheme_seed="indigo")

    # Using string "adaptive" is safer for different Flet versions
    page.scroll = "adaptive"

    # We set scroll to None (Python type) to let the page handle it
    results_column = ft.Column(spacing=15, scroll=None)
    progress_bar = ft.ProgressBar(visible=False, color="indigo")

    def on_scan_click(e):
        if not email_input.value:
            snack = ft.SnackBar(ft.Text("Please paste emails first!"), open=True)
            page.overlay.append(snack)
            page.update()
            return

        results_column.controls.clear()
        progress_bar.visible = True
        page.update()

        raw_texts = [t.strip() for t in email_input.value.split("\n\n") if t.strip()]

        user_profile = {
            "major": major_input.value,
            "year": int(year_input.value) if year_input.value.isdigit() else 1,
            "gpa": float(gpa_input.value) if gpa_input.value.replace('.', '', 1).isdigit() else 0.0,
            "skills": [s.strip().lower() for s in skills_input.value.split(",")],
            "interests": [i.strip().lower() for i in interests_input.value.split(",")]
        }

        for text in raw_texts:
            try:
                parsed = parse_email(text)

                if parsed["status"] == "extracted":
                    opp = parsed["data"]

                    if not opp.get("is_opportunity"):
                        continue

                    if opp.get("min_cgpa") and user_profile["gpa"] < opp["min_cgpa"]:
                        continue

                    results_column.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(opp["title"], size=18, weight="bold", color="indigo200"),
                                    ft.Container(
                                        content=ft.Text(opp["opportunity_type"].upper(), size=10, weight="bold"),
                                        padding=5, border_radius=5, bgcolor="indigo900"
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"Deadline: {opp.get('deadline') or 'Rolling'}", size=12, italic=True,
                                        color="grey400"),
                                ft.Divider(height=1, color="white10"),
                                ft.Text("Required Skills:", size=12, weight="bold"),
                                ft.Text(", ".join(opp.get("required_skills", ["General"])), size=12),
                                ft.FilledButton("Generate Action Plan", icon="bolt", bgcolor="indigo")
                            ], spacing=8),
                            padding=20,
                            border_radius=12,
                            bgcolor="black45",
                            border=ft.border.all(1, "white10")
                        )
                    )
            except Exception as ex:
                print(f"Error parsing email: {ex}")

        progress_bar.visible = False
        if not results_column.controls:
            results_column.controls.append(ft.Text("No qualified matches found.", color="red400"))

        page.update()

    # --- UI COMPONENTS ---
    major_input = ft.TextField(label="Major", value="Artificial Intelligence", width=250)
    year_input = ft.TextField(label="Year", value="2", width=100)
    gpa_input = ft.TextField(label="GPA", value="3.5", width=100)
    skills_input = ft.TextField(label="Skills (comma separated)", value="Python, Linux, ML", expand=True)
    interests_input = ft.TextField(label="Interests", value="Internship, Hackathon", expand=True)

    email_input = ft.TextField(
        label="Inbox Scanner",
        hint_text="Paste emails here. Separate different emails with a blank line.",
        multiline=True, min_lines=8, max_lines=12, border_color="indigo"
    )

    # --- LAYOUT ---
    page.add(
        ft.Column([
            ft.Row([
                ft.Text("🚀 Opportunity Copilot", size=32, weight="bold", color="indigo200"),
                ft.Text("v2.0 Beta", size=12, color="grey")
            ], alignment="spaceBetween", vertical_alignment="end"),

            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Student Profile", weight="bold", size=16),
                        ft.Row([major_input, year_input, gpa_input]),
                        ft.Row([skills_input, interests_input]),
                    ], spacing=15),
                    padding=20
                )
            ),

            email_input,
            ft.FilledButton(
                "Analyze & Rank Opportunities",
                icon="auto_awesome",
                on_click=on_scan_click,
                height=50,
                width=1100,
                bgcolor="indigo"
            ),
            progress_bar,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Top Matches For You", size=20, weight="bold"),
            results_column
        ], spacing=20)
    )


if __name__ == "__main__":
    ft.run(main)