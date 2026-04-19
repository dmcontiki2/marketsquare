"""
seed_demo_data.py
-----------------
Creates 10 tutor listings and 10 service listings under dmcontiki2@gmail.com
All photos are royalty-free Unsplash CDN URLs.
Trust scores vary based on credentials/experience (15–92 range).
Run on server: python3 seed_demo_data.py
"""
import sqlite3, json

DB = '/var/www/marketsquare/marketsquare.db'
SELLER_EMAIL = 'dmcontiki2@gmail.com'
CITY = 'Pretoria'
SUBURB = 'Hatfield'

# ---------------------------------------------------------------------------
# TUTORS  (10 listings)
# ---------------------------------------------------------------------------
TUTORS = [
    {
        "title": "Experienced Mathematics & Physics Tutor",
        "price": "350",
        "subject": "Mathematics & Physics",
        "level": "Grade 10–12 / Matric",
        "mode": "In-person & Online",
        "description": (
            "Passionate and results-driven tutor with 8 years of experience helping Matric learners "
            "achieve distinctions in Mathematics and Physical Science. I hold a BSc in Applied Mathematics "
            "(University of Pretoria) and a PGCE from UNISA. My learners have consistently improved by "
            "2–3 symbol grades within one term.\n\n"
            "Certificates on file: BSc Applied Mathematics (UP, 2015), PGCE (UNISA, 2016), "
            "SACE Registration Certificate, 3× School Academic Excellence Awards."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&q=80",
        "trust_score": 88,
        "area": "Hatfield",
    },
    {
        "title": "English & Afrikaans Home Language Tutor",
        "price": "280",
        "subject": "English & Afrikaans HL",
        "level": "Grade 8–12",
        "mode": "In-person",
        "description": (
            "Qualified English and Afrikaans teacher with 5 years classroom experience at a top Pretoria "
            "high school. I specialise in essays, poetry analysis, and language structure. BA English (UP), "
            "PGCE Secondary (TUT).\n\n"
            "Certificates on file: BA English cum laude (UP, 2017), PGCE TUT (2018), "
            "SACE Registration, Reading Literacy Coach Certificate (2021)."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80",
        "trust_score": 76,
        "area": "Lynwood",
    },
    {
        "title": "Accounting & Economics Matric Tutor",
        "price": "320",
        "subject": "Accounting & Economics",
        "level": "Grade 10–12 / Matric",
        "mode": "Online",
        "description": (
            "BCom Accounting graduate with 4 years of private tutoring. I use past exam papers, "
            "worked solutions, and targeted practice to build exam confidence quickly. "
            "Students average a 20-mark jump within 6 weeks.\n\n"
            "Certificates on file: BCom Accounting (UNISA, 2019), "
            "Certificate in Tax Fundamentals (SAIPA, 2020), 12× 5-star parent reviews."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80",
        "trust_score": 72,
        "area": "Menlyn",
    },
    {
        "title": "Piano & Music Theory Lessons – All Ages",
        "price": "300",
        "subject": "Piano & Music Theory",
        "level": "Beginner – Grade 8 ABRSM",
        "mode": "In-person",
        "description": (
            "Professional pianist and accredited music teacher with 10+ years of teaching experience. "
            "I am an ABRSM Grade 8 pianist and Trinity College London examiner-trained educator. "
            "Lessons are structured, fun, and tailored to each student's pace.\n\n"
            "Certificates on file: BMus Performance (University of Pretoria, 2013), "
            "ABRSM Grade 8 Distinction Certificate, Trinity College Examiner Training (2018), "
            "SAMT Membership Certificate."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=1200&q=80",
        "trust_score": 84,
        "area": "Brooklyn",
    },
    {
        "title": "Life Sciences & Biology Tutor (IEB & NSC)",
        "price": "290",
        "subject": "Life Sciences",
        "level": "Grade 10–12",
        "mode": "In-person & Online",
        "description": (
            "BSc Life Sciences graduate offering focused Matric support in Life Sciences and Biology. "
            "I break down complex content — genetics, evolution, human physiology — into clear, visual notes. "
            "Available for IEB and NSC curricula.\n\n"
            "Certificates on file: BSc Life Sciences (UP, 2020), PGCE in progress (UNISA 2024), "
            "First Aid Level 1, 8× verified parent testimonials."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1628595351029-c2bf17511435?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1628595351029-c2bf17511435?w=1200&q=80",
        "trust_score": 61,
        "area": "Hatfield",
    },
    {
        "title": "Coding & Robotics Tutor – Python & Scratch",
        "price": "400",
        "subject": "Coding & Robotics",
        "level": "Grade 4 – Grade 9",
        "mode": "In-person & Online",
        "description": (
            "Software developer and certified educator teaching Python, Scratch, and basic robotics to "
            "young learners. Lessons are project-based — by week 4 your child builds a working game or robot.\n\n"
            "Certificates on file: BSc Computer Science (UP, 2016), Google Certified Educator Level 2, "
            "Raspberry Pi Foundation Educator Certificate, Code.org Facilitator Certificate."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200&q=80",
        "trust_score": 79,
        "area": "Centurion",
    },
    {
        "title": "Primary School Maths & English Tutor",
        "price": "220",
        "subject": "Primary Maths & English",
        "level": "Grade 1–7",
        "mode": "In-person",
        "description": (
            "Patient and encouraging BEd Foundation Phase teacher with 6 years of school experience. "
            "I use hands-on activities, visual aids, and games to make learning stick for young children. "
            "Available after school Monday–Friday.\n\n"
            "Certificates on file: BEd Foundation Phase (UNISA, 2017), "
            "Remedial Education Certificate (Optima College, 2019), SACE Registration."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=1200&q=80",
        "trust_score": 67,
        "area": "Faerie Glen",
    },
    {
        "title": "Conversational Zulu & Sesotho Language Tutor",
        "price": "250",
        "subject": "Zulu & Sesotho",
        "level": "Beginner – Intermediate",
        "mode": "In-person & Online",
        "description": (
            "Native Zulu speaker with a degree in African Languages. I offer structured conversational "
            "lessons for professionals and families wanting to connect with their local community. "
            "Business language modules also available.\n\n"
            "Certificates on file: BA African Languages (UNISA, 2018), "
            "Pan South African Language Board (PanSALB) Translator Accreditation, "
            "Certificate in Business Zulu (Language Lab, 2021)."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1543269865-cbf427effbad?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1543269865-cbf427effbad?w=1200&q=80",
        "trust_score": 55,
        "area": "Sunnyside",
    },
    {
        "title": "Chess Coach – Beginner to Tournament Level",
        "price": "200",
        "subject": "Chess",
        "level": "Beginner – Club/Tournament",
        "mode": "In-person & Online",
        "description": (
            "FIDE-rated chess coach (1 850 Elo) with 7 years of coaching at schools and clubs. "
            "I train openings, middle-game tactics, endgames, and tournament psychology. "
            "Coached 3 South African junior provincial champions.\n\n"
            "Certificates on file: FIDE Instructor Certificate (2019), Chess South Africa (CSA) "
            "Coaching Licence, Arbiters Certificate (FIDE 2021), provincial youth coaching award."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1529699211952-734e80c4d42b?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1529699211952-734e80c4d42b?w=1200&q=80",
        "trust_score": 48,
        "area": "Brooklyn",
    },
    {
        "title": "University-Level Statistics & Data Science Tutor",
        "price": "450",
        "subject": "Statistics & Data Science",
        "level": "University (1st–3rd year)",
        "mode": "Online",
        "description": (
            "MSc Statistics graduate and part-time lecturer. I assist with R, Python (pandas/scipy), "
            "SPSS, regression analysis, hypothesis testing, and exam preparation for UP, UNISA, and NWU "
            "statistics modules.\n\n"
            "Certificates on file: MSc Statistics with Distinction (UP, 2022), "
            "IBM Data Science Professional Certificate (Coursera, 2023), "
            "Associate of the South African Statistical Association (SASA), "
            "Google Data Analytics Certificate (2023)."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80",
        "trust_score": 92,
        "area": "Hatfield",
    },
]

# ---------------------------------------------------------------------------
# SERVICES  (10 listings)
# ---------------------------------------------------------------------------
SERVICES = [
    {
        "title": "Professional Web Design & WordPress Development",
        "price": "4500",
        "service_class": "Technical",
        "service_type": "Web Design & Development",
        "availability": "Mon–Fri, flexible hours",
        "description": (
            "Full-stack web developer offering professional business websites, e-commerce stores, and "
            "landing pages. Specialise in WordPress, WooCommerce, and custom HTML/CSS/JS. "
            "Turnaround: 5–10 business days. Includes 30-day post-launch support.\n\n"
            "Certificates on file: BSc Computer Science (UP, 2015), "
            "Google UX Design Certificate (2022), "
            "WordPress Certified Developer (WP Engine, 2021), "
            "Cloudflare Accredited Partner Certificate."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&q=80",
        "trust_score": 85,
        "area": "Centurion",
    },
    {
        "title": "Certified Plumber – Residential & Commercial",
        "price": "650",
        "service_class": "Technical",
        "service_type": "Plumbing",
        "availability": "Mon–Sat, emergency call-outs available",
        "description": (
            "Registered plumber with 12 years of hands-on experience in residential and light-commercial "
            "plumbing. Services include leak detection, geyser installation, drain clearing, and bathroom "
            "renovations. PIRB-registered and fully insured.\n\n"
            "Certificates on file: National Trade Test Certificate Plumbing (QCTO, 2011), "
            "PIRB Registration Certificate, SANS 10252 Compliance Certificate, "
            "Public Liability Insurance Policy (R2M cover)."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1200&q=80",
        "trust_score": 90,
        "area": "Pretoria North",
    },
    {
        "title": "Professional Bookkeeping & SARS Tax Returns",
        "price": "800",
        "service_class": "Technical",
        "service_type": "Bookkeeping & Tax",
        "availability": "Mon–Fri 08:00–17:00",
        "description": (
            "ICB-qualified bookkeeper offering monthly bookkeeping, VAT returns, payroll (PaySpace/SimplePay), "
            "and SARS eFiling for small and medium businesses. Fixed monthly packages from R800. "
            "Xero and Sage Pastel certified.\n\n"
            "Certificates on file: ICB Certificate in Bookkeeping to Trial Balance (2016), "
            "Xero Advisor Certified (2023), Sage Pastel Partner Certificate, "
            "SARS Tax Practitioner Registration (TPR-2019-0047)."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80",
        "trust_score": 83,
        "area": "Menlyn",
    },
    {
        "title": "Garden Services – Lawn, Pruning & Landscaping",
        "price": "350",
        "service_class": "Casuals",
        "service_type": "Garden & Landscaping",
        "availability": "Mon–Sat",
        "description": (
            "Experienced garden service with a 3-man team. We offer regular lawn mowing, pruning, "
            "hedge trimming, refuse removal, and full landscape makeovers. Pretoria East area. "
            "Own equipment and transport.\n\n"
            "Certificates on file: Certificate in Horticulture (Tshwane College, 2018), "
            "South African Landscapers Institute (SALI) Affiliate Membership, "
            "Business Registration Certificate (CIPC), Public Liability Certificate."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80",
        "trust_score": 58,
        "area": "Faerie Glen",
    },
    {
        "title": "Personal Trainer – In-Home & Outdoor Fitness",
        "price": "300",
        "service_class": "Casuals",
        "service_type": "Personal Training & Fitness",
        "availability": "Weekdays 05:30–08:00 & 17:00–20:00, Sat 07:00–12:00",
        "description": (
            "Biokineticist-registered personal trainer offering customised programmes for weight loss, "
            "strength, and injury rehabilitation. I come to you — home, park, or gym. "
            "Nutrition guidance included.\n\n"
            "Certificates on file: BSc Biokinetics (UP, 2018), "
            "Biokineticist Registration (HPCSA BK-0023451), "
            "Precision Nutrition Level 1 Coach Certificate, "
            "First Aid Level 3 (Sanca 2022)."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1200&q=80",
        "trust_score": 78,
        "area": "Waterkloof",
    },
    {
        "title": "Professional Photography – Events & Portraits",
        "price": "1800",
        "service_class": "Casuals",
        "service_type": "Photography",
        "availability": "Weekends & evenings by appointment",
        "description": (
            "Award-winning photographer specialising in corporate events, family portraits, and product "
            "photography. Full edit and gallery delivery within 72 hours. "
            "Package includes 3-hour shoot + 50 edited high-res images.\n\n"
            "Certificates on file: Diploma in Photography (Vega, 2014), "
            "SACP Professional Member Certificate (2020), "
            "SA Professional Photographers Association Member, "
            "Bronze Award – Africa Photography Awards 2022."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=1200&q=80",
        "trust_score": 74,
        "area": "Brooklyn",
    },
    {
        "title": "Electrical Repairs & Installations – Registered",
        "price": "550",
        "service_class": "Technical",
        "service_type": "Electrical",
        "availability": "Mon–Fri, emergency call-outs available",
        "description": (
            "DOL-registered electrician with 15 years of experience in domestic and small commercial "
            "electrical work. Services: fault finding, DB board upgrades, lighting installation, "
            "solar PV hook-up, COC certificates.\n\n"
            "Certificates on file: National Trade Test Certificate Electrical (QCTO, 2008), "
            "DOL Registration Certificate (ER-XXXXXX), "
            "Eskom Approved Installer Certificate, Public Liability R5M coverage."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=1200&q=80",
        "trust_score": 87,
        "area": "Centurion",
    },
    {
        "title": "Mobile Car Valeting & Detailing",
        "price": "450",
        "service_class": "Casuals",
        "service_type": "Car Valeting & Detailing",
        "availability": "Mon–Sat 08:00–17:00",
        "description": (
            "Professional mobile car detailer coming to your home or office. Services include full valet, "
            "paint correction, ceramic coating, and interior steam cleaning. "
            "Packages from R450. All equipment supplied.\n\n"
            "Certificates on file: Detail King Professional Detailer Certificate (2020), "
            "Meguiar's Training Programme Certificate, "
            "CIPC Business Registration, "
            "Goods in Transit Insurance Certificate."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=1200&q=80",
        "trust_score": 52,
        "area": "Lynnwood",
    },
    {
        "title": "Graphic Design – Logos, Branding & Print",
        "price": "1200",
        "service_class": "Technical",
        "service_type": "Graphic Design",
        "availability": "Mon–Fri, 2–5 day turnaround",
        "description": (
            "Freelance graphic designer with 9 years of experience delivering brand identities, "
            "marketing material, and print-ready artwork for small businesses across Gauteng. "
            "Tools: Adobe Illustrator, Photoshop, InDesign.\n\n"
            "Certificates on file: NDip Graphic Design (TUT, 2014), "
            "Adobe Certified Professional – Visual Design (2022), "
            "CSD (Communication Design) Professional Membership, "
            "Portfolio of 200+ completed commercial projects."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1626785774625-ddcddc3445e9?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1626785774625-ddcddc3445e9?w=1200&q=80",
        "trust_score": 69,
        "area": "Hatfield",
    },
    {
        "title": "House Cleaning – Reliable Weekly or Once-Off",
        "price": "280",
        "service_class": "Casuals",
        "service_type": "Cleaning",
        "availability": "Mon–Sat 07:00–17:00",
        "description": (
            "Trustworthy domestic cleaning service for homes and apartments. "
            "We supply our own eco-friendly cleaning products. Available for weekly, bi-weekly, "
            "monthly, or once-off deep-cleans. Police clearance on file.\n\n"
            "Certificates on file: SAPS Police Clearance Certificate (2023), "
            "City of Tshwane Business Licence, "
            "Fidelity Security Vetting Certificate, "
            "3 written references from current weekly clients."
        ),
        "thumb_url": "https://images.unsplash.com/photo-1581578949510-fa7315c4c350?w=800&q=80",
        "medium_url": "https://images.unsplash.com/photo-1581578949510-fa7315c4c350?w=1200&q=80",
        "trust_score": 63,
        "area": "Mooikloof",
    },
]

# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------
conn = sqlite3.connect(DB)

def insert_listing(d, category):
    # Build description with photo/cert block appended
    full_desc = d["description"]
    cursor = conn.execute(
        """INSERT INTO listings
           (title, price, category, city, area, suburb, description,
            thumb_url, medium_url, service_class,
            subject, level, mode,
            service_type, availability,
            trust_score, seller_email)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            d["title"],
            d["price"],
            category,
            CITY,
            d.get("area", SUBURB),
            d.get("area", SUBURB),
            full_desc,
            d.get("thumb_url"),
            d.get("medium_url"),
            d.get("service_class"),        # NULL for tutors
            d.get("subject"),              # NULL for services
            d.get("level"),
            d.get("mode"),
            d.get("service_type"),         # NULL for tutors
            d.get("availability"),
            d["trust_score"],
            SELLER_EMAIL,
        )
    )
    return cursor.lastrowid

inserted = []

print("=== Inserting TUTORS ===")
for t in TUTORS:
    lid = insert_listing(t, "Tutors")
    inserted.append((lid, "Tutors", t["title"], t["trust_score"]))
    print(f"  ID {lid}: {t['title'][:55]}  trust={t['trust_score']}")

print("\n=== Inserting SERVICES ===")
for s in SERVICES:
    lid = insert_listing(s, "Services")
    inserted.append((lid, "Services", s["title"], s["trust_score"]))
    print(f"  ID {lid}: {s['title'][:55]}  trust={s['trust_score']}")

conn.commit()
conn.close()

print(f"\nDone — {len(inserted)} listings created under {SELLER_EMAIL}")
