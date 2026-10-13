"""Single source of truth for every word on the profile.

Facts come from Shrish's resume and from reading the code of each repo.
Edit here, re-run `python scripts/build_all.py`, commit.
"""

GH = "https://github.com/Arrow-Ghost"

PROFILE = {
    "name": "Shrish Verma",
    "handle": "Arrow-Ghost",
    "role": "CS undergrad @ VIT Vellore · builder at the edge of security, quantum & AI",
    "location": "Vellore, Tamil Nadu, India",
    "linkedin": "https://www.linkedin.com/in/shrish-verma-7486b1233/",
    "email": "shrishverma0001@gmail.com",
    "github": GH,
    "spoken": ["English", "Hindi", "German"],
}

# ---------------------------------------------------------------- 01 whoami --
# (prompt-less lines are output; "$ " lines are typed commands)
TERMINAL = [
    "$ whoami",
    "shrish verma — b.tech cse @ vit vellore ('29). i build things that shouldn't work yet.",
    "$ cat focus.txt",
    "cybersecurity · quantum computing · ai / ml · embedded & iot · full-stack web",
    "$ ls ./trophies",
    "AIR-1_national-ai-ideathon_1M1B    podium_code-day-hackathon_IIT-Delhi",
    "SIH-2025_internal-finalist          no.1-club-3-years-running_cyber-genie",
    "$ tail now.log",
    "[building]  riley ............ a jarvis-grade personal ai for android  (classified)",
    "[writing]   paper ............ quantum-computing-based game development",
    "[writing]   book ............. game dev using quantum computing for beginners (python)",
    "[serving]   ieee ............. junior core member @ vit vellore",
    "$ echo $SPEAKS",
    "english · hindi · german",
    "$ ",
]

# --------------------------------------------------------------- 02 arsenal --
ARSENAL = [
    # (domain, accent category, [tools])
    ("LANGUAGES", "systems-cli", ["Python", "TypeScript", "JavaScript", "C", "C++", "Java", "Go", "Dart", "GLSL", "SQL"]),
    ("FULL-STACK & WEB", "fullstack-web", ["React", "Next.js", "Astro", "Node.js", "Express", "FastAPI", "Flask", "Tailwind", "WebSockets", "Three.js", "WebGL2", "GSAP"]),
    ("AI · ML · VISION", "ai-ml", ["Gemini Live", "YOLOv8", "OpenVINO", "ONNX Runtime", "Depth Anything V2", "OpenCV", "Whisper", "TensorFlow.js", "Transformers.js", "Groq"]),
    ("QUANTUM", "quantum", ["Qiskit", "Qiskit Aer", "Statevector sims", "Quantum game design"]),
    ("CYBERSECURITY", "security", ["Kali Linux", "Nmap", "Burp Suite", "Wireshark", "Metasploit", "Zero-Trust design", "AES-GCM · ECDH"]),
    ("EMBEDDED & IoT", "iot-embedded", ["Arduino", "ESP32", "Raspberry Pi 5", "Sensors & I²C", "KiCad PCB", "Fusion 360"]),
    ("DATA & CLOUD", "mobile", ["MongoDB Atlas", "PostgreSQL", "Supabase", "SQLite", "Firebase", "Prisma", "Docker", "Vercel", "Render"]),
    ("MOBILE & DESIGN", "game", ["Flutter", "Riverpod", "Bluetooth LE", "Kotlin · Compose", "Figma", "MATLAB", "Tinkercad"]),
]

# -------------------------------------------------- 03 featured operations --
FEATURED = [
    {
        "key": "vidi",
        "code": "OP-01",
        "title": "VIDI",
        "category": "ai-ml",
        "tagline": "It sees the world so they can walk it.",
        "desc": "A voice-first AI companion for blind and low-vision users. Phone camera frames run through YOLOv8 "
                "tracking, Depth Anything V2 distance estimation, OCR and face recognition on OpenVINO, while a "
                "Gemini Live voice agent answers using only what the perception tools actually saw.",
        "highlights": ["~390 ms to first spoken word, with barge-in", "14 grounded tools, so it never invents obstacles", "200+ pytest tests"],
        "stack": ["Python", "FastAPI", "OpenVINO", "YOLOv8", "Gemini Live", "Astro"],
        "repo": f"{GH}/Vidi",
        "live": "",
        "motif": "viewfinder",   # camera HUD with tracked detection boxes + distance readouts
    },
    {
        "key": "shadowadj",
        "code": "OP-02",
        "title": "SHADOWADJ",
        "category": "ai-ml",
        "tagline": "Your voice. Measured. Judged. Never accused.",
        "desc": "A consent-first AI speech coach and debate judge. Browser audio streams at 16 kHz to a Node backend "
                "that measures pace, pauses, fillers and vocabulary live; a rubric judge scores with timestamped "
                "evidence and an integrity engine SHA-256-hashes every session.",
        "highlights": ["Streaming VAD · WPM · fillers · MATTR", "Rubric judge with timestamped evidence", "Three.js audio-reactive FFT sphere"],
        "stack": ["TypeScript", "Node.js", "WebSockets", "Gemini", "Groq", "Three.js"],
        "repo": f"{GH}/ShadowAdj",
        "live": "https://shadow-adj-frontend.vercel.app",
        "motif": "waveform",     # live waveform + FFT bars + WPM meter
    },
    {
        "key": "quantum-maze",
        "code": "OP-03",
        "title": "QUANTUM MAZE",
        "category": "quantum",
        "tagline": "Escape the maze. Collapse the wavefunction.",
        "desc": "A puzzle maze where every door is a qubit. Players apply H, X, Y, Z, S, T and CNOT gates and measure "
                "to open a path — computed by a FastAPI + Qiskit Aer backend, with a TypeScript statevector "
                "simulator for offline play.",
        "highlights": ["Doors are qubits; gates are your keys", "Qiskit Aer backend + TS statevector fallback", "6,000-particle Three.js shader intro"],
        "stack": ["Qiskit", "FastAPI", "TypeScript", "Three.js", "Astro"],
        "repo": f"{GH}/2D-Quantum-Maze",
        "live": "https://2-d-quantum-maze.vercel.app",
        "motif": "maze",         # glowing maze with qubit doors flipping |0>/|1>
    },
    {
        "key": "phishguard",
        "code": "OP-04",
        "title": "PHISHGUARD.JS",
        "category": "security",
        "tagline": "Every rogue script dies at the border.",
        "desc": "A zero-trust runtime shield for the browser. Proxies around fetch and localStorage block token "
                "exfiltration to untrusted origins, a MutationObserver strips injected scripts, and telemetry "
                "streams over WebSockets into a live SOC dashboard with a typosquat + CVE dependency scanner.",
        "highlights": ["Proxy-wrapped fetch blocks exfiltration", "MutationObserver kills injected scripts", "Live SOC dashboard + SQLite telemetry"],
        "stack": ["JavaScript", "React", "Node.js", "Express", "WebSockets", "SQLite"],
        "repo": f"{GH}/PhishGuard1.0",
        "live": "",
        "motif": "shield",       # radar sweep + shield + BLOCKED request log
    },
    {
        "key": "event-horizon",
        "code": "OP-05",
        "title": "EVENT HORIZON",
        "category": "quantum",
        "tagline": "Scroll past the point of no return.",
        "desc": "A cinematic scroll story built around a real-time black hole. A WebGL2 shader traces each pixel's "
                "photon path through Schwarzschild spacetime, so the shadow, photon ring, lensed disk and Doppler "
                "beaming all come from the physics — plus a GPU particle supernova and a generative Web Audio score.",
        "highlights": ["Per-pixel GR ray tracing in GLSL", "GPU particle supernova", "PhishGuard-protected via a custom Astro integration"],
        "stack": ["WebGL2", "GLSL", "Astro", "TypeScript", "Web Audio"],
        "repo": f"{GH}/event-horizon",
        "live": "",
        "motif": "blackhole",    # black hole: shadow, photon ring, lensed accretion disk
    },
    {
        "key": "nosql",
        "code": "OP-06",
        "title": "NOT ONLY SQL",
        "category": "fullstack-web",
        "tagline": "22,000 particles. 20 chapters. Not only SQL.",
        "desc": "A scroll-driven WebGL seminar on NoSQL. A 22k-particle GPU field morphs through 20 chapters next to a "
                "3D sharded-cluster simulation with hash routing, replication and failover, an R+W>N quorum lab, "
                "and a live quiz scored server-side on Express + MongoDB Atlas.",
        "highlights": ["22k-particle GPU shader field", "Sharding, replication & failover simulator", "Live quiz leaderboard on MongoDB Atlas"],
        "stack": ["TypeScript", "Three.js", "WebGL", "Express", "MongoDB Atlas"],
        "repo": f"{GH}/nosql",
        "live": "https://nosql-jade.vercel.app",
        "motif": "cluster",      # sharded cluster nodes + replication pulses + particles
    },
]

# ------------------------------------------------------------ 04 archive --
ARCHIVE = [
    {"title": "Kaledo", "category": "fullstack-web", "line": "Academia × industry portal: skill mapping, internships, verification", "repo": f"{GH}/Kaledo", "live": "https://kaledo-eta.vercel.app"},
    {"title": "Jeevika", "category": "ai-ml", "line": "Voice-first multilingual AI health assistant for rural India · SIH 2025", "repo": f"{GH}/Jeevika..", "live": ""},
    {"title": "Quantum Tic-Tac-Toe", "category": "quantum", "line": "Tic-tac-toe on a 9-qubit Qiskit circuit vs a minimax AI", "repo": f"{GH}/Quantum-Tic-Tac-Toe-Gui-Version", "live": ""},
    {"title": "Quantum Snake", "category": "quantum", "line": "Snake on Qiskit: superposed heads, entangled food, many-worlds AI", "repo": f"{GH}/Quantum-Snake-Game", "live": ""},
    {"title": "P2P Comm", "category": "mobile", "line": "Offline, end-to-end encrypted Flutter messenger over BLE + mDNS", "repo": f"{GH}/p2p-comm-app", "live": ""},
    {"title": "AgentX Vision", "category": "ai-ml", "line": "In-browser AR object detection with on-device Whisper voice control", "repo": f"{GH}/solid-funicular", "live": ""},
    {"title": "B-2 Spirit Cinematic", "category": "fullstack-web", "line": "Scroll-directed Three.js stealth-bomber flythrough in six camera shots", "repo": f"{GH}/pg_webtest1", "live": ""},
    {"title": "ChatPal 2.0", "category": "fullstack-web", "line": "Flask + Socket.IO chat with rooms, polls, uploads and in-chat Gemini/GPT", "repo": f"{GH}/ChatPal2.0", "live": ""},
    {"title": "VTOP Portal", "category": "fullstack-web", "line": "Full-stack university portal for four roles with RBAC", "repo": f"{GH}/VTOP", "live": ""},
    {"title": "FFCS Simulator", "category": "fullstack-web", "line": "Timed VIT course-registration simulator with clash detection", "repo": f"{GH}/ffcs-simulator-fall2026-27", "live": ""},
    {"title": "Smart Irrigation", "category": "iot-embedded", "line": "Arduino plant waterer with overwatering prevention and fault detection", "repo": f"{GH}/Smart-Irrigation-System", "live": ""},
    {"title": "Offline Notes", "category": "fullstack-web", "line": "Offline-first PWA notes with IndexedDB and background sync", "repo": f"{GH}/Offline-notes", "live": ""},
]

# --------------------------------------------------------- 05 mission log --
TIMELINE = [
    # (when, title, org, detail, category, kind)  kind: role | award | build | edu | writing
    ("NOW", "Writing a research paper + a book", "Quantum computing × game development",
     "Paper on quantum-computing-based game development; a beginner's book on quantum game dev in Python.", "quantum", "writing"),
    ("JAN 2026 — NOW", "IEEE Junior Core Member", "IEEE · VIT Vellore",
     "Technical initiatives and student engineering projects; organised the Sense-a-thon event.", "fullstack-web", "role"),
    ("JAN — JUL 2026", "Web Developer", "10th IEEE International Test Conference (ITC) India 2026",
     "Built and ran the official conference website: event info, real-time updates, responsive UI.", "fullstack-web", "role"),
    ("2025", "Smart India Hackathon — Internal Finalist", "SIH 2025",
     "Led an offline AI health LLM for remote, underserved communities (Jeevika).", "ai-ml", "award"),
    ("JUL 2025", "B.Tech Computer Science begins", "Vellore Institute of Technology",
     "Focus: web development, cybersecurity, IoT, AI/ML.", "systems-cli", "edu"),
    ("2024 — 2025", "President, Cyber Genie", "Kothari International School, Noida",
     "Led the club to #1 ranking three years running; workshops, events, competitions, mentoring.", "security", "role"),
    ("SCHOOL ERA", "All India Rank 1 — National AI Idea-thon", "1M1B",
     "Top national rank for an AI idea pitch.", "ai-ml", "award"),
    ("SCHOOL ERA", "Podium — Code Day Hackathon", "IIT Delhi",
     "Placed on the podium at IIT Delhi's Code Day hackathon.", "security", "award"),
    ("2023 — 2024", "Vice President, Cyber Genie", "Kothari International School, Noida",
     "Grew the club and its technical outreach on the way to #1.", "security", "role"),
]

# ------------------------------------------------------------- credits --
CREDITS = [
    ("DIRECTED BY", "Shrish Verma"),
    ("WRITTEN IN", "Python · TypeScript · C++ · Qiskit"),
    ("CINEMATOGRAPHY", "WebGL2 · Three.js · GLSL"),
    ("SECURITY CONSULTANT", "Zero-Trust (PhishGuard.js)"),
    ("QUANTUM EFFECTS", "Qiskit Aer"),
    ("COMPUTER VISION", "YOLOv8 · OpenVINO · Depth Anything"),
    ("FILMED ON LOCATION", "Vellore · Noida · India"),
    ("SPECIAL THANKS", "IEEE VIT · Cyber Genie · late-night coffee"),
]
CREDITS_TAG = "No qubits were harmed in the making of this profile."

# ----------------------------------------------------------- section heads --
SECTIONS = [
    ("01", "WHO AM I", "identity.dossier"),
    ("02", "THE ARSENAL", "tools of the trade"),
    ("03", "FEATURED OPERATIONS", "six missions, declassified"),
    ("04", "THE ARCHIVE", "more transmissions"),
    ("05", "MISSION LOG", "the story so far"),
    ("06", "TELEMETRY", "live signal from github"),
]

BUTTONS = [
    ("linkedin", "LINKEDIN", PROFILE["linkedin"]),
    ("email", "EMAIL", "mailto:" + PROFILE["email"]),
    ("play", "PLAY QUANTUM MAZE", "https://2-d-quantum-maze.vercel.app"),
]
