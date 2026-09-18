from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeItem

DEFAULT_KNOWLEDGE = [
    {
        "title": "Minimum Attendance Requirements & Condonation Rules",
        "category": "academics",
        "content": (
            "Students are required to maintain a minimum of 75% attendance in each registered theory and laboratory course "
            "to be eligible to appear for the End-Semester Examinations. Attendance between 65% and 74% may be condoned by "
            "the Dean of Academic Affairs strictly on valid medical grounds, supported by a Government Hospital Medical Certificate "
            "submitted within 3 working days of resumption of classes, subject to payment of the prescribed condonation fee of ₹1,000 per subject. "
            "Students with attendance below 65% are detained (Redo status) and must re-register for the course in subsequent semesters."
        ),
        "source_name": "Academic Regulations & Curriculum Handbook v2.4",
        "source_url": "https://university.edu/academics/regulations",
        "tags": "attendance, condonation, medical certificate, detention, eligibility, minimum attendance",
        "is_active": True,
    },
    {
        "title": "Grading System, SGPA & CGPA Calculation",
        "category": "academics",
        "content": (
            "The university follows a 10-point Letter Grading System: O (Outstanding, 10 grade points), A+ (Excellent, 9), "
            "A (Very Good, 8), B+ (Good, 7), B (Above Average, 6), C (Average, 5), P (Pass, 4), and F (Fail, 0). "
            "A minimum semester grade point average (SGPA) of 5.0 and minimum cumulative grade point average (CGPA) of 5.0 "
            "is required for graduation. Semester Grade Cards are issued within 15 days of result declaration by the Examination Branch."
        ),
        "source_name": "Controller of Examinations Grading Manual",
        "source_url": "https://university.edu/coe/grading-system",
        "tags": "grades, sgpa, cgpa, grade points, marks, result",
        "is_active": True,
    },
    {
        "title": "Semester Examination Hall Tickets & Admit Card Issuance",
        "category": "examinations",
        "content": (
            "Hall tickets for End-Semester Examinations are published electronically on the Student Information Portal exactly 5 days "
            "prior to commencement of the examinations. To download the Hall Ticket, students must have: (1) Cleared all tuition and hostel dues, "
            "(2) Satisfied minimum attendance criteria (75%), and (3) Completed faculty feedback. Physical printouts must carry the seal of the "
            "respective Department Head and student signature to gain entry to the exam hall."
        ),
        "source_name": "Controller of Examinations Notification #2026/08",
        "source_url": "https://university.edu/coe/notices",
        "tags": "hall ticket, admit card, examination, exam entry, dues clearance",
        "is_active": True,
    },
    {
        "title": "Paper Revaluation & Answer Script Photocopy Procedure",
        "category": "examinations",
        "content": (
            "Students dissatisfied with their semester exam evaluation can apply for answer script revaluation within 7 days of result declaration. "
            "Step 1: Apply online for photocopy of answer sheet by paying ₹300 per subject on the university payment portal. "
            "Step 2: Review the script with subject faculty. "
            "Step 3: If discrepancy exists, apply for Challenge Revaluation with ₹1,000 fee per paper. "
            "If the awarded marks increase by 15% or more, 50% of the revaluation fee will be refunded to the student's registered bank account."
        ),
        "source_name": "Controller of Examinations Evaluation Bylaws",
        "source_url": "https://university.edu/coe/revaluation",
        "tags": "revaluation, paper scrutiny, photocopy, challenge revaluation, marks correction",
        "is_active": True,
    },
    {
        "title": "Tuition Fee Schedule, Payment Modes & Late Fines",
        "category": "fees",
        "content": (
            "Semester tuition fees must be remitted on or before the specified due date (normally July 31 for Odd Semester and December 31 for Even Semester). "
            "Payment can be made exclusively through Net Banking, UPI, or Debit/Credit Cards via the official payment gateway at https://fees.university.edu. "
            "Late Fee Policy: (1) Grace period of 7 days: No fine. (2) 8 to 15 days delay: ₹500 late fine. (3) 16 to 30 days delay: ₹1,500 late fine. "
            "Beyond 30 days, registration for the current semester will be placed on administrative hold."
        ),
        "source_name": "Finance & Accounts Section Circular #2025-26/11",
        "source_url": "https://university.edu/accounts/circulars",
        "tags": "fees, tuition fee, late fine, payment deadline, net banking, accounts",
        "is_active": True,
    },
    {
        "title": "Hostel Allotment, Curfew Timings & Outing Pass Rules",
        "category": "hostel",
        "content": (
            "Hostel admission is renewed annually based on academic clearance and disciplinary record. "
            "Curfew Timings: All hostel residents must mark biometric attendance inside their respective hostels before 09:00 PM on weekdays and 09:30 PM on weekends. "
            "Outstation Leave & Outing Passes: Overnight outing requests must be submitted through the Hostel Management Portal at least 24 hours in advance, "
            "and require explicit SMS/Email approval from registered parent/guardian phone numbers. Late entry without prior sanctioned pass invites ₹500 penalty."
        ),
        "source_name": "Chief Warden Office - Hostel Regulations 2026",
        "source_url": "https://university.edu/hostels/rules",
        "tags": "hostel, mess, curfew, leave pass, outing, night entry, warden",
        "is_active": True,
    },
    {
        "title": "Central Library Borrowing Privileges & Overdue Fines",
        "category": "library",
        "content": (
            "Undergraduate students are entitled to borrow up to 4 books for a loan duration of 14 calendar days. "
            "Postgraduate and research scholars may borrow up to 6 books for 28 days. Books may be renewed once online if not reserved by another reader. "
            "Overdue Fine: ₹2 per book per day for the first 7 days, and ₹5 per book per day thereafter. "
            "Digital Library: Access to IEEE Xplore, ScienceDirect, and Springer journals is available on-campus via LAN and off-campus through OpenAthens SSO."
        ),
        "source_name": "Central Library Handbook & Code of Conduct",
        "source_url": "https://university.edu/library/services",
        "tags": "library, books, issue, return, overdue fine, digital library, ieee",
        "is_active": True,
    },
    {
        "title": "Campus Placement Drive Eligibility & Policy",
        "category": "placements",
        "content": (
            "Eligibility criteria for registering with the University Placement Cell: Minimum CGPA of 6.5 across completed semesters, with no active standing backlogs. "
            "Dream Company Policy: A student who secures a placement with CTC below ₹8 LPA remains eligible to attend interviews for Tier-1 'Dream' companies offering CTC ≥ ₹12 LPA. "
            "Once a student receives an offer from a Dream company, they are barred from participating in subsequent campus drives to ensure fair opportunity for peers."
        ),
        "source_name": "Training & Placement Cell Policy Manual v3.2",
        "source_url": "https://university.edu/placements/policy",
        "tags": "placements, jobs, campus drive, eligibility, dream company, ctc, cgpa",
        "is_active": True,
    },
    {
        "title": "Bonafide Certificate & Official Transcript Issuance",
        "category": "certificates",
        "content": (
            "To obtain an official Bonafide Certificate (for bank loan, passport, or visa purposes), students can apply via the Student Portal under 'Service Requests'. "
            "Standard processing time is 2 working days; certificates are digitally signed and can be downloaded as PDF. "
            "For Official Transcripts: Submit an application with a copy of all semester grade cards and pay ₹250 per copy at the Academic Counter. "
            "Physical transcripts with university embossed seal are ready for collection within 5 working days."
        ),
        "source_name": "Academic Section Student Services Guidelines",
        "source_url": "https://university.edu/admin/certificates",
        "tags": "bonafide, transcript, passport, education loan, certificates, documents",
        "is_active": True,
    },
    {
        "title": "Campus Transportation Routes, Bus Passes & Timings",
        "category": "transport",
        "content": (
            "The university operates 24 bus routes connecting major railway stations and metropolitan hubs. "
            "Bus Pass Application: Students must apply at the beginning of each semester on the Transport Portal with passport photograph and fee receipt. "
            "Bus pass fee is ₹14,000 per semester. Daily morning buses arrive on campus by 08:30 AM; evening departures occur at 04:45 PM and 06:15 PM (for lab students). "
            "Night shuttle operates between campus and the metro station every 30 minutes until 10:00 PM."
        ),
        "source_name": "Department of Transport Operations Schedule 2026",
        "source_url": "https://university.edu/transport/routes",
        "tags": "bus, transport, bus pass, timings, route, shuttle, commute",
        "is_active": True,
    },
    {
        "title": "Branch Change Regulations After First Year (B.Tech)",
        "category": "admissions",
        "content": (
            "Branch change is permitted at the beginning of the 3rd semester for students admitted through standard merit quota. "
            "Eligibility: (1) Student must have passed all 1st and 2nd semester courses in the first attempt. (2) Minimum CGPA of 8.5 at the end of 2nd semester. "
            "Change of branch is strictly based on inter-se merit against sanctioned intake vacancies (not exceeding 10% of intake in the target department). "
            "Applications open in the first week of July on the Academic Section portal."
        ),
        "source_name": "Undergraduate Admissions & Regulations Committee",
        "source_url": "https://university.edu/admissions/branch-change",
        "tags": "branch change, sliding, department change, eligibility, first year, btech",
        "is_active": True,
    },
    {
        "title": "Campus Anti-Ragging Policy & Emergency Help Desk",
        "category": "rules",
        "content": (
            "The university maintains a Zero Tolerance Policy towards ragging in any form, in strict compliance with UGC and Supreme Court directives. "
            "Any student found guilty of ragging, harassment, or intimidation will face immediate suspension, hostel expulsion, and police filing under the Anti-Ragging Act. "
            "24/7 Anti-Ragging Helpline: Toll-free 1800-180-5522 | Campus Security Desk: 011-23456789 | Email: antiragging@university.edu. "
            "Complaints can also be filed anonymously through the drop-boxes installed across departments."
        ),
        "source_name": "University Anti-Ragging Committee Bylaws 2026",
        "source_url": "https://university.edu/rules/anti-ragging",
        "tags": "ragging, anti-ragging, safety, complaint, helpline, discipline, security",
        "is_active": True,
    },
]


def seed_knowledge_base(db: Session):
    existing_count = db.query(KnowledgeItem).count()
    if existing_count == 0:
        for item_data in DEFAULT_KNOWLEDGE:
            item = KnowledgeItem(**item_data)
            db.add(item)
        db.commit()
        print(f"[*] Seeded {len(DEFAULT_KNOWLEDGE)} initial verified institutional knowledge records.")
    else:
        print(f"[*] Knowledge base already contains {existing_count} records.")
