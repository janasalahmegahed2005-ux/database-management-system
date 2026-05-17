import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# ==========================================
# APP SETTINGS & THEME
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("ECU - Competition Management System")
app.geometry("1300x800")
app.minsize(1000, 600)

# ==========================================
# DATABASE CONNECTION
# ==========================================
try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=CompetitionManagementSystem;'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
except Exception as e:
    messagebox.showerror("Database Error", str(e))

# ==========================================
# CUSTOM TREEVIEW STYLE (Modern Look)
# ==========================================
style = ttk.Style()
style.theme_use("default")
style.configure(
    "Treeview",
    background="#2b2b2b",
    foreground="white",
    rowheight=35,
    fieldbackground="#2b2b2b",
    borderwidth=0,
    font=("Arial", 11)
)
style.map('Treeview', background=[('selected', '#1f538d')])
style.configure(
    "Treeview.Heading",
    background="#1f2122",
    foreground="white",
    font=('Arial', 13, 'bold'),
    borderwidth=0,
    padding=10
)

# ==========================================
# MAIN LAYOUT (Sidebar + Main Content)
# ==========================================
# Sidebar Frame
sidebar_frame = ctk.CTkFrame(app, width=250, corner_radius=0, fg_color="#1a1a1a")
sidebar_frame.pack(side="left", fill="y")
sidebar_frame.pack_propagate(False)

# Main Content Frame
main_frame = ctk.CTkFrame(app, corner_radius=0, fg_color="#242424")
main_frame.pack(side="right", fill="both", expand=True)

# App Logo / Title in Sidebar
logo_label = ctk.CTkLabel(
    sidebar_frame, 
    text="ECU \nCompetition\nSystem", 
    font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
    text_color="#1f538d",
    justify="center"
)
logo_label.pack(pady=(40, 40))

# ==========================================
# NAVIGATION LOGIC
# ==========================================
def select_frame(frame_name):
    # Hide all frames
    frame_participants.pack_forget()
    frame_scores.pack_forget()
    frame_ranking.pack_forget()
    
    # Reset button colors
    btn_participants.configure(fg_color="transparent")
    btn_scores.configure(fg_color="transparent")
    btn_ranking.configure(fg_color="transparent")
    
    # Show selected frame and highlight button
    if frame_name == "participants":
        frame_participants.pack(fill="both", expand=True)
        btn_participants.configure(fg_color="#1f538d")
    elif frame_name == "scores":
        frame_scores.pack(fill="both", expand=True)
        btn_scores.configure(fg_color="#1f538d")
    elif frame_name == "ranking":
        frame_ranking.pack(fill="both", expand=True)
        btn_ranking.configure(fg_color="#1f538d")

# Navigation Buttons
btn_participants = ctk.CTkButton(sidebar_frame, text="👥 Participants", anchor="w", font=("Arial", 16, "bold"), fg_color="transparent", hover_color="#2b2b2b", command=lambda: select_frame("participants"))
btn_participants.pack(pady=10, padx=20, fill="x")

btn_scores = ctk.CTkButton(sidebar_frame, text="⭐ Submit Scores", anchor="w", font=("Arial", 16, "bold"), fg_color="transparent", hover_color="#2b2b2b", command=lambda: select_frame("scores"))
btn_scores.pack(pady=10, padx=20, fill="x")

btn_ranking = ctk.CTkButton(sidebar_frame, text="🏆 Live Ranking", anchor="w", font=("Arial", 16, "bold"), fg_color="transparent", hover_color="#2b2b2b", command=lambda: select_frame("ranking"))
btn_ranking.pack(pady=10, padx=20, fill="x")

# ==========================================
# PAGE 1: PARTICIPANTS
# ==========================================
frame_participants = ctk.CTkFrame(main_frame, fg_color="transparent")

# Header
ctk.CTkLabel(frame_participants, text="Manage Participants", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", padx=40, pady=(40, 20))

content_part = ctk.CTkFrame(frame_participants, fg_color="transparent")
content_part.pack(fill="both", expand=True, padx=40, pady=(0, 40))

# Left Card: Input Form
card_input = ctk.CTkFrame(content_part, width=350, corner_radius=15)
card_input.pack(side="left", fill="y", padx=(0, 20))
card_input.pack_propagate(False)

ctk.CTkLabel(card_input, text="New Participant", font=("Arial", 20, "bold")).pack(pady=(30, 20))

name_entry = ctk.CTkEntry(card_input, width=280, height=45, placeholder_text="Full Name")
name_entry.pack(pady=15)
email_entry = ctk.CTkEntry(card_input, width=280, height=45, placeholder_text="Email Address")
email_entry.pack(pady=15)
country_entry = ctk.CTkEntry(card_input, width=280, height=45, placeholder_text="Country")
country_entry.pack(pady=15)

# Right Card: Table
card_table = ctk.CTkFrame(content_part, corner_radius=15)
card_table.pack(side="right", fill="both", expand=True)

columns_parts = ("ID", "Full Name", "Email", "Country")
tree_parts = ttk.Treeview(card_table, columns=columns_parts, show="headings")
for col in columns_parts:
    tree_parts.heading(col, text=col)
tree_parts.column("ID", width=50, anchor="center")
tree_parts.pack(fill="both", expand=True, padx=20, pady=20)

# Participant Functions
def load_participants():
    for row in tree_parts.get_children():
        tree_parts.delete(row)
    try:
        cursor.execute("SELECT * FROM Participants")
        for row in cursor.fetchall():
            tree_parts.insert("", "end", values=(row.ParticipantID, row.FullName, row.Email, row.Country))
    except: pass

def add_participant():
    fullname, email, country = name_entry.get(), email_entry.get(), country_entry.get()
    if not all([fullname, email, country]):
        messagebox.showwarning("Warning", "Please Fill All Fields")
        return
    try:
        cursor.execute("INSERT INTO Participants (FullName, Email, Country) VALUES (?, ?, ?)", (fullname, email, country))
        conn.commit()
        name_entry.delete(0, "end"); email_entry.delete(0, "end"); country_entry.delete(0, "end")
        load_participants(); load_comboboxes()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_participant():
    selected = tree_parts.selection()
    if not selected: return
    participant_id = tree_parts.item(selected)["values"][0]
    try:
        cursor.execute("DELETE FROM Participants WHERE ParticipantID=?", (participant_id,))
        conn.commit()
        load_participants(); load_comboboxes()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Action Buttons Container inside Input Card
btn_container = ctk.CTkFrame(card_input, fg_color="transparent")
btn_container.pack(pady=20, fill="x", padx=35)

ctk.CTkButton(btn_container, text="Add Participant", height=45, command=add_participant).pack(fill="x", pady=5)
ctk.CTkButton(btn_container, text="Delete Selected", height=45, fg_color="#c23b22", hover_color="#8f2b19", command=delete_participant).pack(fill="x", pady=5)
ctk.CTkButton(btn_container, text="Refresh Table", height=45, fg_color="#4a4a4a", hover_color="#333333", command=load_participants).pack(fill="x", pady=5)

# ==========================================
# PAGE 2: SUBMIT SCORES
# ==========================================
frame_scores = ctk.CTkFrame(main_frame, fg_color="transparent")

ctk.CTkLabel(frame_scores, text="Judges Evaluation Panel", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", padx=40, pady=(40, 20))

# Center Card for Scoring
card_score = ctk.CTkFrame(frame_scores, corner_radius=15, width=600, height=500)
card_score.pack(pady=40)
card_score.pack_propagate(False)

ctk.CTkLabel(card_score, text="Submit Official Score", font=("Arial", 22, "bold"), text_color="#1f538d").pack(pady=(40, 30))

combo_participant = ctk.CTkComboBox(card_score, width=400, height=45, font=("Arial", 16))
combo_participant.pack(pady=15)
combo_participant.set("Select Participant")

combo_competition = ctk.CTkComboBox(card_score, width=400, height=45, font=("Arial", 16))
combo_competition.pack(pady=15)
combo_competition.set("Select Competition")

combo_judge = ctk.CTkComboBox(card_score, width=400, height=45, font=("Arial", 16))
combo_judge.pack(pady=15)
combo_judge.set("Select Judge")

score_entry = ctk.CTkEntry(card_score, width=400, height=45, font=("Arial", 16), placeholder_text="Enter Score (e.g., 9.5)")
score_entry.pack(pady=15)

def load_comboboxes():
    try:
        cursor.execute("SELECT ParticipantID, FullName FROM Participants")
        combo_participant.configure(values=[f"{row[0]} - {row[1]}" for row in cursor.fetchall()])
        cursor.execute("SELECT CompetitionID, CompetitionName FROM Competitions")
        combo_competition.configure(values=[f"{row[0]} - {row[1]}" for row in cursor.fetchall()])
        cursor.execute("SELECT JudgeID, JudgeName FROM Judges")
        combo_judge.configure(values=[f"{row[0]} - {row[1]}" for row in cursor.fetchall()])
    except: pass

def submit_score():
    try:
        p_id = combo_participant.get().split(" - ")[0]
        c_id = combo_competition.get().split(" - ")[0]
        j_id = combo_judge.get().split(" - ")[0]
        score_val = float(score_entry.get())
        
        cursor.execute("EXEC SubmitScore ?, ?, ?, ?", (p_id, c_id, j_id, score_val))
        conn.commit()
        messagebox.showinfo("Success", "Score submitted successfully! Ranking updated.")
        score_entry.delete(0, "end")
        refresh_ranking()
    except Exception as e:
        messagebox.showerror("Error", "Please check your inputs.\n" + str(e))

ctk.CTkButton(card_score, text="CONFIRM & SUBMIT", command=submit_score, width=400, height=50, font=("Arial", 16, "bold"), fg_color="#2b8a3e", hover_color="#1e602b").pack(pady=30)

# ==========================================
# PAGE 3: LIVE RANKING
# ==========================================
frame_ranking = ctk.CTkFrame(main_frame, fg_color="transparent")

# Header with Live Indicator
header_frame = ctk.CTkFrame(frame_ranking, fg_color="transparent")
header_frame.pack(fill="x", padx=40, pady=(40, 20))
ctk.CTkLabel(header_frame, text="Live Leaderboard", font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
ctk.CTkLabel(header_frame, text="🔴 LIVE UPDATES", font=ctk.CTkFont(size=14, weight="bold"), text_color="#c23b22").pack(side="right", pady=10)

card_ranking = ctk.CTkFrame(frame_ranking, corner_radius=15)
card_ranking.pack(fill="both", expand=True, padx=40, pady=(0, 40))

columns_rank = ("Rank", "Participant", "Competition", "Total Score")
tree_rank = ttk.Treeview(card_ranking, columns=columns_rank, show="headings")
for col in columns_rank:
    tree_rank.heading(col, text=col)
tree_rank.column("Rank", width=80, anchor="center")
tree_rank.column("Total Score", width=120, anchor="center")
tree_rank.pack(fill="both", expand=True, padx=20, pady=20)

def refresh_ranking():
    for row in tree_rank.get_children():
        tree_rank.delete(row)
    try:
        query = """
        SELECT 
            RANK() OVER (PARTITION BY R.CompetitionID ORDER BY R.TotalScore DESC) AS RankPosition,
            P.FullName AS Participant,
            C.CompetitionName,
            R.TotalScore
        FROM Rankings R
        INNER JOIN Participants P ON R.ParticipantID = P.ParticipantID
        INNER JOIN Competitions C ON R.CompetitionID = C.CompetitionID;
        """
        cursor.execute(query)
        for row in cursor.fetchall():
            tree_rank.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:.2f}"))
    except: pass
    app.after(3000, refresh_ranking) # Auto refresh every 3 seconds

# ==========================================
# APP INITIALIZATION
# ==========================================
load_participants()
load_comboboxes()
refresh_ranking()

# Start on Participants Page
select_frame("participants")

app.mainloop()