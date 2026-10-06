"""Narration script. Order == edit order. Each line id maps to a shot in build.py."""

VOICE = "am_michael"
SPEED = 1.0

LINES = [
    # ---- cold open (motion graphics) ----
    ("intro1", "Every engineering project runs on documents. Drawings. Transmittals. Reviews. Approvals."),
    ("intro2", "Keeping track of all of it... shouldn't be the hard part."),
    ("title",  "Meet PIM-X."),
    # ---- hub ----
    ("hub1", "One home screen. Every part of your project. Project management, procurement, transmittals, C-D-E. A single click away."),
    ("hub2", "And inside the Engineering Tools Hub: workflows and status, tag extraction, materials management, data analytics, and the full S-D-C and I-D-C suite."),
    # ---- dashboard ----
    ("ch1", ""),
    ("dash1", "Start with the Power B-I Dashboard. Live project data, embedded right inside PIM-X. No extra browser tabs. No extra logins."),
    ("dash2", "Two hundred and fifty-six wells tracked. Completed, in progress, and status by discipline. All at a glance."),
    ("dash3", "Switch to the Drawing Register, and every drawing number, requested, used, or unused, is tracked per project."),
    ("dash4", "Need it in Excel? Export. And the data is on your desk in seconds."),
    # ---- tracker ----
    ("ch2", ""),
    ("trk1", "Next, the S-D-C and I-D-C Tracker. Pick any project from the tree, sub-projects included."),
    ("trk2", "Hit Load Data, and the tracker shows you exactly where every document stands."),
    ("trk3", "Seventy-six documents. Twenty-six through S-D-C. Twenty-six through I-D-C. Stage by stage, with the full document list underneath. Live snapshot, or full audit history. Your choice."),
    # ---- transmittals ----
    ("ch3", ""),
    ("tx1", "And then, the one that changes how you issue documents. PIM-X Transmittals. Log in. Select your project."),
    ("tx2", "And your project hub lights up. Audit Explorer. Project Management. Documents Repository. And Transmittals."),
    ("tx3", "Need something fast? Ask the built-in PIM-X Assistant. List of transmittals. And it answers straight from your project data."),
    ("tx4", "Register. New outgoing. New incoming. Document sets. Pending acknowledgements. Everything transmittal, in one place."),
    ("tx5", "Create a new outgoing transmittal. Fill in the details. Add your recipients."),
    ("tx6", "Then pull documents straight from ProjectWise. Browse the folder, tick the files, Add Selected. Eight documents, attached in seconds."),
    ("tx7", "Every transmittal follows a clear workflow. Draft. P-M approval. Client response. And you can see the current stage at any time."),
    ("tx8", "Hit Email, and PIM-X drafts the approval request for you. Documents listed, cover sheet attached, ready to send from Outlook."),
    ("tx9", "The cover sheet is generated automatically. Formatted, numbered, and ready for the client."),
    ("tx10", "Submit for P-M approval."),
    ("tx11", "The project manager accepts and signs."),
    ("tx12", "The workflow moves forward."),
    ("tx13", "And with one click, the transmittal is issued to the client. Tracked, logged, and auditable. From draft to delivery."),
    ("tx14", "Every transmittal lives in the Register. Direction, status, project, recipient. Searchable, and exportable."),
    # ---- close ----
    ("recap", "Dashboards. Trackers. Transmittals. One platform. One login. Zero documents lost in email."),
    ("end", "PIM-X. Built for the way engineers actually work."),
]
