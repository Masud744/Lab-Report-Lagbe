/* ==========================================================================
   Lab Report Lagbe? — Workspace Application Controller
   ========================================================================== */

const STORAGE_KEYS = {
    SETTINGS: "lrg_settings_v2",
    DRAFTS: "lrg_drafts_v2",
};

const LANG_META = {
    python:     { label: "Python",     short: "Py", color: "#3776AB", ext: "py" },
    "c++":      { label: "C++",        short: "C+", color: "#00599C", ext: "cpp" },
    java:       { label: "Java",       short: "Jv", color: "#E76F00", ext: "java" },
    dart:       { label: "Dart",       short: "Dt", color: "#0175C2", ext: "dart" },
    javascript: { label: "JavaScript", short: "JS", color: "#D97706", ext: "js" },
    c:          { label: "C",          short: "C",  color: "#2563EB", ext: "c" },
    typescript: { label: "TypeScript", short: "TS", color: "#3178C6", ext: "ts" },
    sql:        { label: "SQL",        short: "SQ", color: "#0D9488", ext: "sql" },
    go:         { label: "Go",         short: "Go", color: "#00ADD8", ext: "go" },
    rust:       { label: "Rust",       short: "Rs", color: "#B45309", ext: "rs" },
    kotlin:     { label: "Kotlin",     short: "Kt", color: "#7F52FF", ext: "kt" },
    csharp:     { label: "C#",         short: "C#", color: "#68217A", ext: "cs" },
    php:        { label: "PHP",        short: "PH", color: "#4F5D95", ext: "php" },
    ruby:       { label: "Ruby",       short: "Rb", color: "#CC342D", ext: "rb" },
    swift:      { label: "Swift",      short: "Sw", color: "#F05138", ext: "swift" },
    r:          { label: "R",          short: "R",  color: "#276DC3", ext: "R" },
    bash:       { label: "Bash",       short: "Sh", color: "#334155", ext: "sh" },
    matlab:     { label: "MATLAB",     short: "Mt", color: "#D95319", ext: "m" },
    arduino:    { label: "Arduino",    short: "In", color: "#00979D", ext: "ino" },
    lua:        { label: "Lua",        short: "Lu", color: "#000080", ext: "lua" },
    perl:       { label: "Perl",       short: "Pl", color: "#39457E", ext: "pl" },
    scala:      { label: "Scala",      short: "Sc", color: "#DC322F", ext: "scala" },
};

const FEATURED_LANGS = ["python", "c++", "java", "dart", "javascript", "c", "sql", "go", "rust", "bash"];

const TEMPLATES = [
    {
        id: "opengl-cuboid",
        title: "3D Wireframe Cuboid & Rotation",
        courseCode: "IRE 404",
        courseTitle: "Computer Graphics and Animation Sessional",
        labNumber: 4,
        language: "python",
        summary: "OpenGL + Pygame rotating rectangular cuboid with 3px red edges, black background, and automatic 4-angle visualization.",
        tasks: [
            {
                title: "3D Wireframe Cuboid and Continuous Y-Axis Rotation",
                description: "Build a Python OpenGL application using Pygame to render a 3D rectangular wireframe cuboid with distinct width, height, and depth, rotating smoothly around the Y-axis.",
                requirements: [
                    "Create an 800x600 OpenGL window using pygame.display.set_mode()",
                    "Set background color to black using glClearColor(0, 0, 0, 1)",
                    "Draw cuboid edges in red with glColor3f(1, 0, 0) and glLineWidth(3.0)",
                    "Use distinct width, height, and depth coordinates",
                    "Rotate continuously around the Y-axis with glRotatef() at 60 FPS",
                ],
            },
        ],
    },
    {
        id: "dda-line",
        title: "DDA Line Drawing Algorithm",
        courseCode: "IRE 404",
        courseTitle: "Computer Graphics Lab",
        labNumber: 2,
        language: "python",
        summary: "Digital Differential Analyzer line rasterization algorithm with step-by-step pixel coordinate calculation and automatic 2D grid visualization.",
        tasks: [
            {
                title: "Implementation of DDA Line Drawing Algorithm",
                description: "Implement the Digital Differential Analyzer (DDA) line drawing algorithm in Python to compute and verify rasterized integer pixel coordinates for gentle, steep, and negative slopes.",
                requirements: [
                    "Compute dx, dy, and total steps = max(|dx|, |dy|)",
                    "Calculate incremental X and Y offsets per step",
                    "Round intermediate floating-point coordinates to nearest pixel",
                    "Verify output table across multiple slope cases",
                ],
            },
        ],
    },
    {
        id: "dart-oop",
        title: "OOP Concepts Implementation",
        courseCode: "IRE 460",
        courseTitle: "Mobile Platform for IoT Devices Sessional",
        labNumber: 1,
        language: "dart",
        summary: "Classes, encapsulation, inheritance, and polymorphism in Dart with Student Result and Course Registration workflows.",
        tasks: [
            {
                title: "Student Result & GPA Management System",
                description: "Design an object-oriented Student Result system in Dart demonstrating encapsulation, constructors, methods, and grade computation.",
                requirements: [
                    "Create a Student class with private fields, getters, and validation",
                    "Calculate GPA and letter grade from course marks",
                    "Display formatted academic transcript in console",
                ],
            },
        ],
    },
    {
        id: "cpp-sorting",
        title: "Sorting Algorithm Analysis",
        courseCode: "CSE 204",
        courseTitle: "Data Structures & Algorithms Sessional",
        labNumber: 3,
        language: "c++",
        summary: "Implement and benchmark Quick Sort, Merge Sort, and Insertion Sort in modern C++17 with comparison counts and execution timings.",
        tasks: [
            {
                title: "Merge Sort vs Quick Sort Comparative Benchmark",
                description: "Implement Merge Sort and Quick Sort in C++17, verify sorted outputs on sample arrays, and compare time complexity and swap/comparison counts.",
                requirements: [
                    "Implement recursive Merge Sort and partition-based Quick Sort",
                    "Track comparison counts and execution duration using std::chrono",
                    "Verify sorted correctness across random and reverse-sorted arrays",
                ],
            },
        ],
    },
    {
        id: "c-linked-list",
        title: "Singly Linked List Operations",
        courseCode: "CSE 202",
        courseTitle: "Data Structures Sessional",
        labNumber: 2,
        language: "c",
        summary: "Dynamic memory allocation in C for linked list insertion, deletion, search, and reversal with clean memory cleanup.",
        tasks: [
            {
                title: "Dynamic Singly Linked List in C",
                description: "Implement a singly linked list using struct pointers and malloc/free supporting insert, delete, search, reverse, and traversal operations.",
                requirements: [
                    "Define Node struct with integer payload and next pointer",
                    "Implement insertAtHead, insertAtTail, deleteByValue, and reverseList",
                    "Free all allocated heap memory cleanly before program exit",
                ],
            },
        ],
    },
    {
        id: "java-bank",
        title: "Bank Account Inheritance Hierarchy",
        courseCode: "CSE 210",
        courseTitle: "Object-Oriented Programming Sessional",
        labNumber: 4,
        language: "java",
        summary: "Abstract classes, method overriding, and exception handling in Java modeling Savings and Checking accounts.",
        tasks: [
            {
                title: "Polymorphic Banking System in Java",
                description: "Build an abstract Account base class with SavingsAccount and CheckingAccount subclasses supporting deposits, withdrawals, interest, and overdraft rules.",
                requirements: [
                    "Create abstract Account class with shared balance and account metadata",
                    "Override withdraw() in SavingsAccount and CheckingAccount",
                    "Demonstrate runtime polymorphism via an Account array",
                ],
            },
        ],
    },
    {
        id: "python-matplotlib",
        title: "Algorithm Time Complexity Plot",
        courseCode: "CSE 306",
        courseTitle: "Algorithm Design & Analysis Sessional",
        labNumber: 5,
        language: "python",
        summary: "Benchmark Bubble Sort vs Python Timsort across input sizes and auto-capture Matplotlib charts directly into your LaTeX PDF.",
        tasks: [
            {
                title: "Empirical Time Complexity Comparison with Matplotlib",
                description: "Write a Python program that benchmarks Bubble Sort against Python's built-in sorted() on arrays of sizes 100 to 800, prints timing tables, and plots execution time vs input size using Matplotlib.",
                requirements: [
                    "Implement Bubble Sort and time both algorithms using time.perf_counter()",
                    "Measure execution times for n = 100, 200, 400, 600, 800",
                    "Plot a labeled comparison graph using matplotlib.pyplot with title, grid, and legend",
                ],
            },
        ],
    },
];

const WORKSPACE_SAMPLES = {
    python: `# Python 3 — Quick Lab Experiment\ndef dda_line(x0, y0, x1, y1):\n    dx, dy = x1 - x0, y1 - y0\n    steps = max(abs(dx), abs(dy))\n    x_inc, y_inc = dx / steps, dy / steps\n    x, y = float(x0), float(y0)\n    points = []\n    for _ in range(steps + 1):\n        points.append((round(x), round(y)))\n        x += x_inc\n        y += y_inc\n    return points\n\npts = dda_line(2, 2, 10, 6)\nprint("DDA Rasterized Pixels:", pts)\n`,
    "c++": `#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    vector<int> arr = {42, 17, 8, 99, 23, 4};\n    sort(arr.begin(), arr.end());\n    cout << "Sorted Array: ";\n    for (int x : arr) cout << x << " ";\n    cout << endl;\n    return 0;\n}\n`,
    c: `#include <stdio.h>\n\nint main() {\n    int arr[] = {12, 5, 29, 1, 18};\n    int n = 5, sum = 0;\n    for (int i = 0; i < n; i++) sum += arr[i];\n    printf("Sum = %d, Average = %.2f\\n", sum, (double)sum / n);\n    return 0;\n}\n`,
    java: `public class Main {\n    public static void main(String[] args) {\n        int[] scores = {88, 92, 79, 95};\n        int total = 0;\n        for (int s : scores) total += s;\n        System.out.printf("Average Score: %.2f%n", total / (double) scores.length);\n    }\n}\n`,
    dart: `void main() {\n  final courses = {'IRE 404': 3.75, 'IRE 460': 4.00, 'CSE 312': 3.50};\n  final avg = courses.values.reduce((a, b) => a + b) / courses.length;\n  print('Semester GPA: \${avg.toStringAsFixed(2)}');\n}\n`,
    javascript: `const nums = [15, 3, 27, 8, 42];\nconst sorted = [...nums].sort((a, b) => a - b);\nconsole.log("Sorted:", sorted.join(", "));\n`,
    bash: `#!/usr/bin/env bash\necho "System Date: $(date)"\nfor i in 1 2 3 4 5; do\n  echo "Step $i squared = $((i * i))"\ndone\n`,
};

// ─── Global App State ───
const state = {
    currentView: "dashboard",
    reports: [],
    activity: [],
    stats: {
        total_reports: 0,
        completed_reports: 0,
        code_executions: 0,
        this_month_reports: 0,
        monthly_goal: 50,
        report_dates: [],
    },
    engine: { has_groq_api_key: false, model: "qwen/qwen3.8-27b" },
    reportsFilter: "all",
    calendarCursor: new Date(),
    taskCounter: 0,
    taskImages: {}, // { taskId: [{ data, caption }] }
    activeDraftId: null,
};

// ─── Settings & Drafts LocalStorage Helpers ───
function loadSettings() {
    const defaults = {
        studentName: "Shahriar Alom Masud",
        studentId: "2201032",
        session: "2022-2023",
        instructorName: "",
        university: "University of Frontier Technology, Bangladesh",
        universityShort: "UFTB",
        department: "Department of Internet of Things and Robotics Engineering (IRE)",
        departmentShort: "IRE",
        faculty: "Faculty of Cyber Physical System Engineering",
        customLogo: "",
        groqKey: "",
    };
    try {
        const raw = localStorage.getItem(STORAGE_KEYS.SETTINGS);
        return raw ? { ...defaults, ...JSON.parse(raw) } : defaults;
    } catch {
        return defaults;
    }
}

function persistSettings(cfg) {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(cfg));
}

function loadDrafts() {
    try {
        const raw = localStorage.getItem(STORAGE_KEYS.DRAFTS);
        const list = raw ? JSON.parse(raw) : [];
        return Array.isArray(list) ? list : [];
    } catch {
        return [];
    }
}

function persistDrafts(drafts) {
    localStorage.setItem(STORAGE_KEYS.DRAFTS, JSON.stringify(drafts));
}

// ─── Boot Initialization ───
document.addEventListener("DOMContentLoaded", () => {
    populateLanguageSelects();
    applySettingsToUI();
    renderSupportedLanguageChips();
    renderTemplatesGrid();
    addTask();
    loadWorkspaceSample(true);
    setupGlobalSearch();
    setupKeyboardShortcuts();
    setupFormSubmit();
    setupEditorTabKey();
    fetchDashboardData();
    initFirebaseAuth();
});

// ─── Navigation ───
function navigateTo(view) {
    state.currentView = view;
    document.querySelectorAll(".view").forEach((el) => el.classList.remove("active"));
    const target = document.getElementById(`view-${view}`);
    if (target) target.classList.add("active");

    document.querySelectorAll(".nav-item").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.view === view);
    });

    closeMobileSidebar();

    if (view === "dashboard" || view === "reports" || view === "activity") {
        fetchDashboardData();
    }
}

function openMobileSidebar() {
    document.getElementById("sidebar").classList.add("open");
    document.getElementById("sidebarBackdrop").classList.add("open");
}

function closeMobileSidebar() {
    document.getElementById("sidebar").classList.remove("open");
    document.getElementById("sidebarBackdrop").classList.remove("open");
}

// ─── Fetch Dashboard & Backend Data ───
async function fetchDashboardData() {
    try {
        const res = await fetch("/api/dashboard");
        if (!res.ok) return;
        const data = await res.json();
        state.reports = data.recent_reports || [];
        state.stats = data.stats || state.stats;
        state.activity = data.activity || [];
        state.engine = data.engine || state.engine;

        // Fetch full list for My Reports view
        const allRes = await fetch("/api/reports");
        if (allRes.ok) {
            const allData = await allRes.json();
            state.reports = allData.reports || state.reports;
        }
        renderAllDynamicViews();
    } catch (err) {
        console.warn("Dashboard refresh skipped:", err);
        renderAllDynamicViews();
    }
}

function renderAllDynamicViews() {
    const drafts = loadDrafts();
    const totalCount = state.stats.total_reports + drafts.length;

    // KPIs
    document.getElementById("kpiTotal").textContent = totalCount;
    document.getElementById("kpiCompleted").textContent = state.stats.completed_reports;
    document.getElementById("kpiExecutions").textContent = state.stats.code_executions;
    document.getElementById("kpiDrafts").textContent = drafts.length;

    const navBadge = document.getElementById("navReportsCount");
    if (totalCount > 0) {
        navBadge.textContent = totalCount;
        navBadge.hidden = false;
    } else {
        navBadge.hidden = true;
    }

    // Usage This Month
    const monthCount = state.stats.this_month_reports || 0;
    const goal = state.stats.monthly_goal || 50;
    const pct = Math.min(100, Math.round((monthCount / goal) * 100));
    document.getElementById("usageRatio").textContent = `${monthCount} / ${goal} reports`;
    document.getElementById("usageBarFill").style.width = `${pct}%`;
    document.getElementById("usagePercent").textContent = `${pct}% used`;

    // Engine status pills
    updateEngineStatusUI();

    // Tables, Calendar, Notifications, Activity, Profile Card
    renderRecentReportsTable();
    renderAllReports();
    renderCalendar();
    renderActivityViews();
    if (typeof updateProfileHeroCard === "function") {
        updateProfileHeroCard(state.currentUser);
    }
}

function updateEngineStatusUI() {
    const cfg = loadSettings();
    const hasKey = state.engine.has_groq_api_key || Boolean(cfg.groqKey);
    const modelName = state.engine.model || "qwen/qwen3.8-27b";

    const pill = document.getElementById("engineStatusPill");
    const formBadge = document.getElementById("formEngineBadge");
    const settingsInfo = document.getElementById("settingsEngineInfo");

    if (hasKey) {
        const label = `Active • ${modelName.split("/").pop()}`;
        pill.textContent = label;
        pill.classList.remove("warn");
        formBadge.textContent = `Server Key Active (${modelName})`;
        formBadge.classList.remove("warn");
        if (settingsInfo) {
            settingsInfo.textContent = `Connected to Groq AI using ${modelName}. Server .env key is active — no manual key required.`;
        }
    } else {
        pill.textContent = "API Key Needed";
        pill.classList.add("warn");
        formBadge.textContent = "Enter Groq API Key";
        formBadge.classList.add("warn");
        if (settingsInfo) {
            settingsInfo.textContent = "No server GROQ_API_KEY detected. Enter a free Groq key below.";
        }
    }
}

// ─── Greeting & Settings Sync ───
function applySettingsToUI() {
    const cfg = loadSettings();
    const hour = new Date().getHours();
    const greet = hour < 12 ? "Good Morning" : hour < 17 ? "Good Afternoon" : "Good Evening";
    const nameParts = (cfg.studentName || "Masud").trim().split(/\s+/);
    const shortName = nameParts[nameParts.length - 1] || "Masud";
    const initials = nameParts.length >= 2
        ? (nameParts[0][0] + nameParts[nameParts.length - 1][0]).toUpperCase()
        : shortName.slice(0, 2).toUpperCase();

    if (!state.currentUser) {
        document.getElementById("greetingTitle").textContent = `${greet}, Student! 👋`;
        document.getElementById("sidebarProfileName").textContent = "Guest Student";
        document.getElementById("sidebarProfileSub").textContent = "Click to Sign In";
        document.getElementById("sidebarAvatar").textContent = initials;
        const avatarText = document.getElementById("topbarAvatarText");
        if (avatarText) avatarText.textContent = initials;
    }

    // Populate Settings inputs
    document.getElementById("setStudentName").value = cfg.studentName;
    document.getElementById("setStudentId").value = cfg.studentId;
    document.getElementById("setSession").value = cfg.session;
    document.getElementById("setInstructorName").value = cfg.instructorName;
    document.getElementById("setUniversity").value = cfg.university;
    document.getElementById("setUnivShort").value = cfg.universityShort;
    document.getElementById("setDeptShort").value = cfg.departmentShort;
    document.getElementById("setDepartment").value = cfg.department;
    document.getElementById("setFaculty").value = cfg.faculty;
    document.getElementById("setGroqKey").value = cfg.groqKey || "";
    document.getElementById("settingsLogoPreview").src = cfg.customLogo || "/images/uftb.png";

    // Sync defaults into Create Report form
    document.getElementById("studentName").value = cfg.studentName;
    document.getElementById("studentId").value = cfg.studentId;
    document.getElementById("session").value = cfg.session;
    if (cfg.instructorName && !document.getElementById("instructorName").value) {
        document.getElementById("instructorName").value = cfg.instructorName;
    }
    document.getElementById("university").value = cfg.university;
    document.getElementById("universityShort").value = cfg.universityShort;
    document.getElementById("departmentShort").value = cfg.departmentShort;
    document.getElementById("department").value = cfg.department;
    document.getElementById("faculty").value = cfg.faculty;
    if (cfg.groqKey) {
        document.getElementById("groqApiKey").value = cfg.groqKey;
    }
}

async function saveSettings() {
    const existing = loadSettings();
    const cfg = {
        ...existing,
        studentName: document.getElementById("setStudentName").value.trim() || "Shahriar Alom Masud",
        studentId: document.getElementById("setStudentId").value.trim() || "2201032",
        session: document.getElementById("setSession").value.trim() || "2022-2023",
        instructorName: document.getElementById("setInstructorName").value.trim(),
        university: document.getElementById("setUniversity").value.trim(),
        universityShort: document.getElementById("setUnivShort").value.trim(),
        departmentShort: document.getElementById("setDeptShort").value.trim(),
        department: document.getElementById("setDepartment").value.trim(),
        faculty: document.getElementById("setFaculty").value.trim(),
        groqKey: document.getElementById("setGroqKey").value.trim(),
    };
    persistSettings(cfg);
    applySettingsToUI();
    updateEngineStatusUI();

    if (state.currentUser && firestoreDb && typeof firebase !== "undefined") {
        try {
            const user = state.currentUser;
            const userRef = firestoreDb.collection("users").doc(user.uid);
            const snap = await userRef.get();
            const ts = firebase.firestore.FieldValue.serverTimestamp();
            if (snap.exists) {
                await userRef.update({
                    displayName: cfg.studentName.slice(0, 100),
                    studentId: cfg.studentId.slice(0, 50),
                    department: cfg.department.slice(0, 100),
                    university: cfg.university.slice(0, 150),
                    updatedAt: ts,
                });
            } else {
                const docData = {
                    displayName: cfg.studentName.slice(0, 100),
                    email: user.email,
                    studentId: cfg.studentId.slice(0, 50),
                    department: cfg.department.slice(0, 100),
                    university: cfg.university.slice(0, 150),
                    createdAt: ts,
                    updatedAt: ts,
                };
                if (user.photoURL && /^https?:\/\//.test(user.photoURL)) {
                    docData.photoUrl = user.photoURL.slice(0, 500);
                }
                await userRef.set(docData);
            }
            if (cfg.studentName && cfg.studentName !== user.displayName) {
                await user.updateProfile({ displayName: cfg.studentName });
            }
            handleAuthStateChanged(firebaseAuth.currentUser || user);
        } catch (err) {
            console.warn("Could not sync settings to Firestore:", err.message);
        }
    }

    showToast("Workspace settings saved.");
}

function handleCustomLogoUpload(input) {
    const file = input.files && input.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
        showToast("Please select a PNG or JPG image.", true);
        return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
        const cfg = loadSettings();
        cfg.customLogo = e.target.result;
        persistSettings(cfg);
        document.getElementById("settingsLogoPreview").src = cfg.customLogo;
        showToast("Custom cover logo updated.");
    };
    reader.readAsDataURL(file);
}

function resetCustomLogo() {
    const cfg = loadSettings();
    cfg.customLogo = "";
    persistSettings(cfg);
    document.getElementById("settingsLogoPreview").src = "/images/uftb.png";
    showToast("Reset to official UFTB cover seal.");
}

// ─── Language Selects & Chips ───
function populateLanguageSelects() {
    const entries = Object.entries(LANG_META);
    const createSel = document.getElementById("language");
    const filterSel = document.getElementById("reportsLangFilter");
    const wsSel = document.getElementById("workspaceLang");

    createSel.innerHTML = "";
    wsSel.innerHTML = "";

    entries.forEach(([key, meta]) => {
        createSel.add(new Option(meta.label, key));
        filterSel.add(new Option(meta.label, key));
        if (["python", "c++", "c", "java", "dart", "javascript", "bash", "sql", "go", "rust"].includes(key)) {
            wsSel.add(new Option(meta.label, key));
        }
    });
    createSel.value = "python";
    wsSel.value = "python";
}

function renderSupportedLanguageChips() {
    const container = document.getElementById("supportedLangChips");
    container.innerHTML = FEATURED_LANGS.map((key) => {
        const m = LANG_META[key];
        return `
            <button type="button" class="lang-chip-btn" onclick="startFreshReport('${key}')">
                <span class="lang-chip-badge" style="background:${m.color}">${m.short}</span>
                <span>${m.label}</span>
            </button>
        `;
    }).join("");
}

// ─── Reports Tables (Dashboard + My Reports) ───
function getMergedReports() {
    const drafts = loadDrafts().map((d) => ({
        id: d.id,
        title: d.lab_title || d.tasks?.[0]?.title || "Untitled Draft",
        course_title: d.course_title || d.course_code || "Saved Draft",
        language: d.language || "python",
        status: "draft",
        updated_at: d.updated_at,
        isDraft: true,
        draftData: d,
    }));
    const completed = state.reports.map((r) => ({ ...r, isDraft: false }));
    return [...drafts, ...completed].sort((a, b) => (b.updated_at || "").localeCompare(a.updated_at || ""));
}

function renderReportRow(item, idx) {
    const lang = LANG_META[item.language] || { label: item.language || "Code", color: "#0B4F4A" };
    const statusHtml = item.isDraft
        ? `<span class="status-pill status-draft">○ Draft</span>`
        : `<span class="status-pill status-completed">✓ Completed</span>`;

    const actionsHtml = item.isDraft
        ? `
            <button type="button" class="action-icon-btn" title="Resume Draft" onclick="resumeDraft('${item.id}')">
                <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M13.5 3.5L16.5 6.5L7 16H4V13L13.5 3.5Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>
            </button>
            <button type="button" class="action-icon-btn danger" title="Delete Draft" onclick="deleteDraft('${item.id}')">
                <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M4.5 6H15.5M8 6V4H12V6M6.5 6V16H13.5V6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
        `
        : `
            <button type="button" class="action-icon-btn" title="Preview PDF" onclick="openPdfPreview('${item.id}', '${escapeAttr(item.title)}', '${escapeAttr(item.course_title || "")}', ${Boolean(item.has_latex_zip)})">
                <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M2.5 10C4.2 6.8 6.8 5.2 10 5.2C13.2 5.2 15.8 6.8 17.5 10C15.8 13.2 13.2 14.8 10 14.8C6.8 14.8 4.2 13.2 2.5 10Z" stroke="currentColor" stroke-width="1.6"/><circle cx="10" cy="10" r="2.3" stroke="currentColor" stroke-width="1.6"/></svg>
            </button>
            <button type="button" class="action-icon-btn" title="Download PDF" onclick="downloadReportDirect('${item.id}')">
                <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M10 3.5V12.5M10 12.5L6.8 9.3M10 12.5L13.2 9.3M4 15.8H16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
            ${item.has_latex_zip ? `<button type="button" class="tex-action-btn" title="Download Overleaf LaTeX .zip" onclick="downloadLatexDirect('${item.id}')">TeX</button>` : ""}
            <button type="button" class="action-icon-btn danger" title="Delete Report" onclick="deleteReport('${item.id}')">
                <svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M4.5 6H15.5M8 6V4H12V6M6.5 6V16H13.5V6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
        `;

    return `
        <tr>
            <td>${idx + 1}</td>
            <td class="report-title-cell">
                <strong>${escapeHtml(item.title)}</strong>
                <small>${escapeHtml(item.course_code ? `${item.course_code} • ${item.course_title}` : (item.course_title || ""))}</small>
            </td>
            <td>
                <span class="lang-pill">
                    <span class="lang-dot" style="background:${lang.color}"></span>
                    ${escapeHtml(lang.label)}
                </span>
            </td>
            <td>${statusHtml}</td>
            <td class="muted-hint">${formatRelativeTime(item.updated_at)}</td>
            <td class="col-actions"><div class="row-actions">${actionsHtml}</div></td>
        </tr>
    `;
}

function renderRecentReportsTable() {
    const tbody = document.getElementById("recentReportsBody");
    const items = getMergedReports().slice(0, 5);
    if (!items.length) {
        tbody.innerHTML = `
            <tr><td colspan="6">
                <div class="empty-table-state">
                    <p>No lab reports yet. Generate your first LaTeX PDF report in under a minute.</p>
                    <button type="button" class="btn btn-primary btn-sm" onclick="startFreshReport()">+ Create New Report</button>
                </div>
            </td></tr>
        `;
        return;
    }
    tbody.innerHTML = items.map((item, i) => renderReportRow(item, i)).join("");
}

function setReportsFilter(filter, btn) {
    state.reportsFilter = filter;
    document.querySelectorAll(".filter-tab").forEach((t) => t.classList.remove("active"));
    if (btn) btn.classList.add("active");
    renderAllReports();
}

function renderAllReports() {
    const tbody = document.getElementById("allReportsBody");
    const q = (document.getElementById("reportsSearchInput")?.value || "").toLowerCase().trim();
    const langFilter = document.getElementById("reportsLangFilter")?.value || "";

    let items = getMergedReports();
    if (state.reportsFilter === "completed") items = items.filter((r) => !r.isDraft);
    if (state.reportsFilter === "draft") items = items.filter((r) => r.isDraft);
    if (langFilter) items = items.filter((r) => r.language === langFilter);
    if (q) {
        items = items.filter((r) =>
            `${r.title} ${r.course_title || ""} ${r.course_code || ""} ${r.language}`.toLowerCase().includes(q)
        );
    }

    if (!items.length) {
        tbody.innerHTML = `
            <tr><td colspan="6">
                <div class="empty-table-state">
                    <p>No matching reports found.</p>
                </div>
            </td></tr>
        `;
        return;
    }
    tbody.innerHTML = items.map((item, i) => renderReportRow(item, i)).join("");
}

async function deleteReport(id) {
    try {
        const res = await fetch(`/api/reports/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Could not delete report");
        showToast("Report deleted.");
        fetchDashboardData();
    } catch (e) {
        showToast(e.message, true);
    }
}

// ─── PDF Preview Modal ───
function openPdfPreview(reportId, title, sub, hasLatexZip = false) {
    if (!ensureAuthenticated("Sign in or create an account to preview and download your complete PDF report.", () => {
        openPdfPreview(reportId, title, sub, hasLatexZip);
    })) {
        return;
    }

    document.getElementById("pdfModalTitle").textContent = title || "Lab Report Preview";
    document.getElementById("pdfModalSub").textContent = sub || "Compiled LaTeX PDF";
    document.getElementById("pdfModalDownload").href = `/api/reports/${reportId}/file`;
    const latexBtn = document.getElementById("pdfModalLatex");
    const repMeta = state.reports.find((r) => r.id === reportId);
    const showLatex = Boolean(hasLatexZip || repMeta?.has_latex_zip);
    if (showLatex) {
        latexBtn.href = `/api/reports/${reportId}/latex`;
        latexBtn.hidden = false;
    } else {
        latexBtn.hidden = true;
    }
    document.getElementById("pdfModalFrame").src = `/api/reports/${reportId}/file?inline=1`;
    document.getElementById("pdfPreviewModal").hidden = false;
}

function closePdfModal() {
    document.getElementById("pdfPreviewModal").hidden = true;
    document.getElementById("pdfModalFrame").src = "about:blank";
}

// ─── Interactive Calendar ───
function changeCalendarMonth(delta) {
    state.calendarCursor = new Date(
        state.calendarCursor.getFullYear(),
        state.calendarCursor.getMonth() + delta,
        1
    );
    renderCalendar();
}

function renderCalendar() {
    const cur = state.calendarCursor;
    const year = cur.getFullYear();
    const month = cur.getMonth();
    const today = new Date();

    const monthName = cur.toLocaleDateString("en-US", { month: "long", year: "numeric" });
    document.getElementById("calendarMonthLabel").textContent = monthName;

    const firstDay = new Date(year, month, 1);
    const startOffset = (firstDay.getDay() + 6) % 7; // Monday = 0
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const reportDates = new Set(state.stats.report_dates || []);

    let html = "";
    for (let i = 0; i < startOffset; i++) {
        html += `<span class="cal-day"></span>`;
    }
    for (let d = 1; d <= daysInMonth; d++) {
        const iso = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        const isToday =
            year === today.getFullYear() &&
            month === today.getMonth() &&
            d === today.getDate();
        const hasRep = reportDates.has(iso);
        const cls = `cal-day${isToday ? " today" : ""}${hasRep ? " has-report" : ""}`;
        html += `<span class="${cls}" title="${hasRep ? "Report generated on " + iso : iso}">${d}</span>`;
    }
    document.getElementById("calendarDays").innerHTML = html;
}

// ─── Activity & Notifications ───
function renderActivityViews() {
    const list = state.activity || [];
    const notifList = document.getElementById("notifList");
    const timeline = document.getElementById("activityTimeline");
    const dot = document.getElementById("notifDot");

    if (dot) dot.style.display = list.length ? "block" : "none";

    if (!list.length) {
        const emptyHtml = `<div class="empty-table-state"><p>No activity recorded yet.</p></div>`;
        notifList.innerHTML = emptyHtml;
        timeline.innerHTML = emptyHtml;
        return;
    }

    notifList.innerHTML = list.slice(0, 6).map((a) => `
        <div class="notif-entry">
            <strong>${escapeHtml(a.title)}</strong>
            <small>${escapeHtml(a.detail || "")} • ${formatRelativeTime(a.timestamp)}</small>
        </div>
    `).join("");

    const icons = { report: "PDF", execute: "</>", delete: "×", system: "★" };
    timeline.innerHTML = list.map((a) => `
        <div class="activity-row">
            <span class="activity-badge">${icons[a.type] || "•"}</span>
            <div class="activity-content">
                <strong>${escapeHtml(a.title)}</strong>
                <small>${escapeHtml(a.detail || "")}</small>
            </div>
            <span class="activity-time">${formatRelativeTime(a.timestamp)}</span>
        </div>
    `).join("");
}

function toggleNotifications(force) {
    const pop = document.getElementById("notifPopover");
    const btn = document.getElementById("notifBtn");
    const next = typeof force === "boolean" ? force : pop.hidden;
    pop.hidden = !next;
    btn.setAttribute("aria-expanded", String(next));
}

// ─── Templates View ───
function renderTemplatesGrid() {
    const grid = document.getElementById("templatesGrid");
    grid.innerHTML = TEMPLATES.map((t) => {
        const lang = LANG_META[t.language] || { label: t.language, color: "#0B4F4A" };
        return `
            <article class="template-card">
                <div class="template-top">
                    <span class="lang-pill"><span class="lang-dot" style="background:${lang.color}"></span>${lang.label}</span>
                    <span class="template-course">${escapeHtml(t.courseCode)} • Lab ${String(t.labNumber).padStart(2, "0")}</span>
                </div>
                <h3>${escapeHtml(t.title)}</h3>
                <p>${escapeHtml(t.summary)}</p>
                <div class="template-footer">
                    <small class="muted-hint">${t.tasks.length} task preset</small>
                    <button type="button" class="btn btn-primary btn-sm" onclick="applyTemplate('${t.id}')">Use Template</button>
                </div>
            </article>
        `;
    }).join("");
}

function applyTemplate(templateId) {
    const tpl = TEMPLATES.find((t) => t.id === templateId);
    if (!tpl) return;
    state.activeDraftId = null;

    document.getElementById("courseCode").value = tpl.courseCode;
    document.getElementById("courseTitle").value = tpl.courseTitle;
    document.getElementById("labNumber").value = tpl.labNumber;
    document.getElementById("labTitle").value = tpl.title;
    document.getElementById("language").value = tpl.language;

    clearTasks();
    tpl.tasks.forEach((task) => addTask(task));
    navigateTo("create");
    showToast(`Loaded "${tpl.title}" template.`);
}

function startFreshReport(presetLang) {
    state.activeDraftId = null;
    if (presetLang && LANG_META[presetLang]) {
        document.getElementById("language").value = presetLang;
    }
    navigateTo("create");
}

// ─── Create Report: Tasks, Custom Code & Image Uploader ───
function toggleSection(bodyId, headerEl) {
    const body = document.getElementById(bodyId);
    body.classList.toggle("collapsed");
    headerEl.classList.toggle("open", !body.classList.contains("collapsed"));
}

function clearTasks() {
    document.getElementById("tasksContainer").innerHTML = "";
    state.taskCounter = 0;
    state.taskImages = {};
}

function addTask(preset = null) {
    state.taskCounter += 1;
    const tid = `task_${state.taskCounter}`;
    state.taskImages[tid] = preset?.images ? [...preset.images] : [];

    const container = document.getElementById("tasksContainer");
    const num = container.children.length + 1;
    const card = document.createElement("div");
    card.className = "task-card";
    card.dataset.taskId = tid;

    const reqs = preset?.requirements?.length ? preset.requirements : [""];
    const reqRowsHtml = reqs.map((r) => buildReqRowHtml(r)).join("");
    const hasCustomCode = Boolean(preset?.custom_code);

    card.innerHTML = `
        <div class="task-card-header">
            <span class="task-badge">Task ${num}</span>
            <button type="button" class="task-remove-btn" onclick="removeTask(this)">Remove</button>
        </div>
        <div class="field">
            <label>Task Title *</label>
            <input type="text" class="task-title-input" placeholder="e.g. 3D Wireframe Cuboid and Rotation" value="${escapeAttr(preset?.title || "")}" required>
        </div>
        <div class="field">
            <label>Problem Description</label>
            <textarea class="task-desc-input" rows="3" placeholder="Describe what the program should accomplish...">${escapeHtml(preset?.description || "")}</textarea>
        </div>
        <div class="field">
            <label>Key Requirements</label>
            <div class="req-list">${reqRowsHtml}</div>
            <button type="button" class="link-btn" style="width:fit-content" onclick="addReqRow(this)">+ Add Requirement</button>
        </div>
        <div class="field">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <label>Custom Source Code (Optional — leave blank to let AI write code)</label>
                <button type="button" class="link-btn" onclick="toggleTaskCodeBox(this)">${hasCustomCode ? "Hide Code" : "+ Paste My Code"}</button>
            </div>
            <textarea class="custom-code-area task-code-input" ${hasCustomCode ? "" : "hidden"} placeholder="Paste your own code here if you want AI to analyze and format your exact solution...">${escapeHtml(preset?.custom_code || "")}</textarea>
        </div>
        <div class="field">
            <label>Output Screenshots (Optional — up to 4 images for 2×2 LaTeX figure grid)</label>
            <div class="upload-dropzone"
                 onclick="this.querySelector('input[type=file]').click()"
                 ondragover="event.preventDefault(); this.classList.add('dragover')"
                 ondragleave="this.classList.remove('dragover')"
                 ondrop="handleImageDrop(event, '${tid}')">
                <span>Click or drag &amp; drop up to 4 PNG/JPG screenshots here</span>
                <input type="file" accept="image/*" multiple hidden onchange="handleImageFiles(this.files, '${tid}')">
            </div>
            <div class="image-preview-grid" id="preview_${tid}"></div>
        </div>
    `;

    container.appendChild(card);
    renderTaskImagePreviews(tid);
    renumberTasks();
}

function buildReqRowHtml(val = "") {
    return `
        <div class="req-row">
            <input type="text" class="req-input" placeholder="e.g. Set background color to black..." value="${escapeAttr(val)}">
            <button type="button" class="req-remove-btn" onclick="this.parentElement.remove()" aria-label="Remove requirement">×</button>
        </div>
    `;
}

function addReqRow(btn) {
    const list = btn.previousElementSibling;
    list.insertAdjacentHTML("beforeend", buildReqRowHtml(""));
    list.lastElementChild.querySelector("input").focus();
}

function toggleTaskCodeBox(btn) {
    const ta = btn.parentElement.nextElementSibling;
    ta.hidden = !ta.hidden;
    btn.textContent = ta.hidden ? "+ Paste My Code" : "Hide Code";
    if (!ta.hidden) ta.focus();
}

function removeTask(btn) {
    const container = document.getElementById("tasksContainer");
    if (container.children.length <= 1) {
        showToast("At least one task is required.", true);
        return;
    }
    const card = btn.closest(".task-card");
    delete state.taskImages[card.dataset.taskId];
    card.remove();
    renumberTasks();
}

function renumberTasks() {
    document.querySelectorAll("#tasksContainer .task-card").forEach((card, i) => {
        card.querySelector(".task-badge").textContent = `Task ${i + 1}`;
    });
}

function handleImageDrop(event, tid) {
    event.preventDefault();
    event.currentTarget.classList.remove("dragover");
    handleImageFiles(event.dataTransfer.files, tid);
}

function handleImageFiles(files, tid) {
    const current = state.taskImages[tid] || [];
    const remaining = 4 - current.length;
    if (remaining <= 0) {
        showToast("Maximum 4 screenshots allowed per task.", true);
        return;
    }
    Array.from(files).slice(0, remaining).forEach((file) => {
        if (!file.type.startsWith("image/")) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            state.taskImages[tid].push({
                data: e.target.result,
                caption: file.name.replace(/\.[^/.]+$/, "").replace(/[_-]+/g, " "),
            });
            renderTaskImagePreviews(tid);
        };
        reader.readAsDataURL(file);
    });
}

function renderTaskImagePreviews(tid) {
    const grid = document.getElementById(`preview_${tid}`);
    if (!grid) return;
    const imgs = state.taskImages[tid] || [];
    grid.innerHTML = imgs.map((img, idx) => `
        <div class="image-preview-item">
            <button type="button" class="image-remove-btn" onclick="removeTaskImage('${tid}', ${idx})" aria-label="Remove image">×</button>
            <img src="${img.data}" alt="Figure ${idx + 1}">
            <input type="text" value="${escapeAttr(img.caption)}" placeholder="Figure caption..." oninput="updateTaskImageCaption('${tid}', ${idx}, this.value)">
        </div>
    `).join("");
}

function updateTaskImageCaption(tid, idx, val) {
    if (state.taskImages[tid]?.[idx]) {
        state.taskImages[tid][idx].caption = val;
    }
}

function removeTaskImage(tid, idx) {
    state.taskImages[tid].splice(idx, 1);
    renderTaskImagePreviews(tid);
}

// ─── Collect Form Payload & Drafts ───
function collectFormPayload() {
    const cfg = loadSettings();
    const tasks = [];
    document.querySelectorAll("#tasksContainer .task-card").forEach((card) => {
        const tid = card.dataset.taskId;
        const title = card.querySelector(".task-title-input").value.trim();
        const description = card.querySelector(".task-desc-input").value.trim();
        const custom_code = card.querySelector(".task-code-input").value;
        const requirements = Array.from(card.querySelectorAll(".req-input"))
            .map((i) => i.value.trim())
            .filter(Boolean);
        const images = (state.taskImages[tid] || []).map((im) => ({
            data: im.data,
            caption: im.caption || "",
        }));
        if (title || description) {
            tasks.push({ title: title || "Lab Task", description, requirements, custom_code, images });
        }
    });

    return {
        student_name: document.getElementById("studentName").value.trim(),
        student_id: document.getElementById("studentId").value.trim(),
        session: document.getElementById("session").value.trim(),
        university: document.getElementById("university").value.trim(),
        university_short: document.getElementById("universityShort").value.trim(),
        department: document.getElementById("department").value.trim(),
        department_short: document.getElementById("departmentShort").value.trim(),
        faculty: document.getElementById("faculty").value.trim(),
        course_code: document.getElementById("courseCode").value.trim(),
        course_title: document.getElementById("courseTitle").value.trim(),
        instructor_name: document.getElementById("instructorName").value.trim(),
        instructor_title: document.getElementById("instructorTitle").value.trim(),
        lab_number: parseInt(document.getElementById("labNumber").value, 10) || 1,
        lab_title: document.getElementById("labTitle").value.trim(),
        language: document.getElementById("language").value,
        github_link: document.getElementById("githubLink").value.trim(),
        custom_logo: cfg.customLogo || "",
        groq_api_key: document.getElementById("groqApiKey").value.trim() || cfg.groqKey || "",
        tasks,
    };
}

function saveCurrentDraft() {
    const payload = collectFormPayload();
    const drafts = loadDrafts();
    const draftId = state.activeDraftId || `draft_${Date.now().toString(36)}`;
    state.activeDraftId = draftId;

    // Strip heavy base64 images from localStorage draft if huge, keep lightweight metadata
    const safeDraft = {
        ...payload,
        id: draftId,
        updated_at: new Date().toISOString(),
        custom_logo: "",
        tasks: payload.tasks.map((t) => ({ ...t, images: [] })),
    };

    const idx = drafts.findIndex((d) => d.id === draftId);
    if (idx >= 0) drafts[idx] = safeDraft;
    else drafts.unshift(safeDraft);

    persistDrafts(drafts);
    renderAllDynamicViews();
    showToast("Draft saved to My Reports.");
}

function resumeDraft(draftId) {
    const draft = loadDrafts().find((d) => d.id === draftId);
    if (!draft) return;
    state.activeDraftId = draftId;

    document.getElementById("studentName").value = draft.student_name || "";
    document.getElementById("studentId").value = draft.student_id || "";
    document.getElementById("session").value = draft.session || "";
    document.getElementById("courseCode").value = draft.course_code || "";
    document.getElementById("courseTitle").value = draft.course_title || "";
    document.getElementById("instructorName").value = draft.instructor_name || "";
    document.getElementById("instructorTitle").value = draft.instructor_title || "Lecturer";
    document.getElementById("labNumber").value = draft.lab_number || 1;
    document.getElementById("labTitle").value = draft.lab_title || "";
    document.getElementById("language").value = draft.language || "python";
    document.getElementById("githubLink").value = draft.github_link || "";

    clearTasks();
    if (draft.tasks && draft.tasks.length) {
        draft.tasks.forEach((t) => addTask(t));
    } else {
        addTask();
    }
    navigateTo("create");
    showToast("Draft loaded into editor.");
}

function deleteDraft(draftId) {
    const remaining = loadDrafts().filter((d) => d.id !== draftId);
    persistDrafts(remaining);
    if (state.activeDraftId === draftId) state.activeDraftId = null;
    renderAllDynamicViews();
    showToast("Draft removed.");
}

// ─── Form Submission & PDF Compilation ───
function setupFormSubmit() {
    document.getElementById("reportForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = collectFormPayload();

        if (!payload.student_name || !payload.student_id) {
            showToast("Student name and ID are required.", true);
            return;
        }
        if (!payload.tasks.length) {
            showToast("Please add at least one lab task.", true);
            return;
        }

        if (!ensureAuthenticated("Sign in or create an account to compile and download your lab report PDF.", () => {
            document.getElementById("reportForm").requestSubmit();
        })) {
            return;
        }

        const overlay = document.getElementById("progressOverlay");
        const statusEl = document.getElementById("overlayStatus");
        const bar = document.getElementById("progressBar");
        const submitBtn = document.getElementById("submitBtn");

        overlay.hidden = false;
        submitBtn.disabled = true;
        bar.style.width = "14%";
        statusEl.textContent = "Generating academic methodology and source code with Groq AI...";

        const steps = [
            { pct: "38%", msg: "Executing code and verifying output..." },
            { pct: "68%", msg: "Formatting figures and LaTeX document..." },
            { pct: "88%", msg: "Compiling PDF with pdflatex..." },
        ];
        let stepIdx = 0;
        const timer = setInterval(() => {
            if (stepIdx < steps.length) {
                bar.style.width = steps[stepIdx].pct;
                statusEl.textContent = steps[stepIdx].msg;
                stepIdx += 1;
            }
        }, 3500);

        try {
            const res = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                let errMsg = `Generation failed (HTTP ${res.status})`;
                try {
                    const errJson = await res.json();
                    errMsg = errJson.detail || errMsg;
                } catch {}
                throw new Error(errMsg);
            }

            bar.style.width = "100%";
            statusEl.textContent = "PDF compiled successfully! Downloading...";

            const reportId = res.headers.get("X-Report-Id");
            const hasLatexZip = res.headers.get("X-Has-Latex-Zip") === "true";
            const blob = await res.blob();
            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = `${payload.student_id}_Lab${payload.lab_number}_Report.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => URL.revokeObjectURL(downloadUrl), 4000);

            // Remove draft if this came from a draft
            if (state.activeDraftId) {
                persistDrafts(loadDrafts().filter((d) => d.id !== state.activeDraftId));
                state.activeDraftId = null;
            }

            await fetchDashboardData();
            showToast("Lab report PDF compiled and downloaded!");

            if (reportId) {
                openPdfPreview(reportId, payload.lab_title || `Lab Report ${payload.lab_number}`, payload.course_title, hasLatexZip);
            }
        } catch (err) {
            showToast(err.message, true);
        } finally {
            clearInterval(timer);
            overlay.hidden = true;
            submitBtn.disabled = false;
        }
    });
}

// ─── Code Workspace ───
function loadWorkspaceSample(force = false) {
    const lang = document.getElementById("workspaceLang").value;
    const meta = LANG_META[lang] || { ext: "txt" };
    document.getElementById("workspaceFilename").textContent = `main.${meta.ext}`;
    const editor = document.getElementById("workspaceEditor");
    if (force || !editor.value.trim()) {
        editor.value = WORKSPACE_SAMPLES[lang] || `// Write your ${meta.label || lang} code here\n`;
    }
}

function setupEditorTabKey() {
    const editor = document.getElementById("workspaceEditor");
    editor.addEventListener("keydown", (e) => {
        if (e.key === "Tab") {
            e.preventDefault();
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            editor.value = editor.value.substring(0, start) + "    " + editor.value.substring(end);
            editor.selectionStart = editor.selectionEnd = start + 4;
        }
    });
}

async function runWorkspaceCode() {
    const code = document.getElementById("workspaceEditor").value;
    const language = document.getElementById("workspaceLang").value;
    const stdin = document.getElementById("workspaceStdin").value;
    const outEl = document.getElementById("workspaceOutput");
    const plotsEl = document.getElementById("workspacePlots");
    const metaEl = document.getElementById("workspaceExecMeta");
    const runBtn = document.getElementById("runCodeBtn");

    if (!code.trim()) {
        showToast("Write some code before running.", true);
        return;
    }

    runBtn.disabled = true;
    runBtn.textContent = "Running...";
    metaEl.textContent = "Executing...";
    outEl.classList.remove("has-error");
    outEl.textContent = "Running code...";
    plotsEl.hidden = true;
    plotsEl.innerHTML = "";

    try {
        const cfg = loadSettings();
        const res = await fetch("/api/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code, language, stdin, groq_api_key: cfg.groqKey || "" }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Execution failed");

        if (data.success) {
            outEl.textContent = data.output || "(Program finished with no console output)";
            const plotNote = data.images?.length ? ` • ${data.images.length} plot(s)` : "";
            metaEl.textContent = `${data.engine} • ${data.execution_ms}ms${plotNote}`;
            metaEl.classList.remove("warn");
            if (data.images && data.images.length) {
                plotsEl.innerHTML = data.images.map((im) => `
                    <div class="workspace-plot-item">
                        <img src="${im.data}" alt="${escapeAttr(im.caption || "Plot")}">
                        <span>${escapeHtml(im.caption || "Generated Plot")}</span>
                    </div>
                `).join("");
                plotsEl.hidden = false;
            }
        } else {
            outEl.classList.add("has-error");
            outEl.textContent = [data.error, data.output].filter(Boolean).join("\n\n");
            metaEl.textContent = `Error • ${data.execution_ms}ms`;
            metaEl.classList.add("warn");
        }
        fetchDashboardData();
    } catch (err) {
        outEl.classList.add("has-error");
        outEl.textContent = err.message;
        metaEl.textContent = "Failed";
        metaEl.classList.add("warn");
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = "▶ Run Code";
    }
}

function copyWorkspaceCode() {
    navigator.clipboard.writeText(document.getElementById("workspaceEditor").value);
    showToast("Code copied to clipboard.");
}

function sendWorkspaceToReport() {
    const code = document.getElementById("workspaceEditor").value.trim();
    const lang = document.getElementById("workspaceLang").value;
    if (!code) {
        showToast("Code editor is empty.", true);
        return;
    }
    document.getElementById("language").value = lang;
    clearTasks();
    addTask({
        title: `${(LANG_META[lang]?.label || lang)} Lab Implementation`,
        description: "Academic analysis, methodology, execution, and discussion of the provided source code.",
        requirements: ["Explain core algorithm and implementation structure", "Verify execution output and edge cases"],
        custom_code: code,
    });
    navigateTo("create");
    showToast("Code transferred into Create Report!");
}

// ─── Global Search & Keyboard Shortcuts ───
function setupGlobalSearch() {
    const input = document.getElementById("globalSearchInput");
    const box = document.getElementById("globalSearchResults");

    input.addEventListener("input", () => {
        const q = input.value.trim().toLowerCase();
        if (!q) {
            box.hidden = true;
            return;
        }
        const results = [];
        getMergedReports().forEach((r) => {
            if (`${r.title} ${r.course_title} ${r.language}`.toLowerCase().includes(q)) {
                results.push({
                    label: r.title,
                    tag: r.isDraft ? "Draft" : "Report",
                    action: () => r.isDraft ? resumeDraft(r.id) : openPdfPreview(r.id, r.title, r.course_title),
                });
            }
        });
        TEMPLATES.forEach((t) => {
            if (`${t.title} ${t.summary} ${t.language}`.toLowerCase().includes(q)) {
                results.push({
                    label: t.title,
                    tag: "Template",
                    action: () => applyTemplate(t.id),
                });
            }
        });
        if (!results.length) {
            box.innerHTML = `<div class="notif-entry"><small>No matches for "${escapeHtml(q)}"</small></div>`;
        } else {
            box.innerHTML = "";
            results.slice(0, 6).forEach((item) => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "search-result-item";
                btn.innerHTML = `<span>${escapeHtml(item.label)}</span><span class="search-result-tag">${item.tag}</span>`;
                btn.onclick = () => {
                    box.hidden = true;
                    input.value = "";
                    item.action();
                };
                box.appendChild(btn);
            });
        }
        box.hidden = false;
    });

    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-box")) box.hidden = true;
        if (!e.target.closest(".notif-wrap")) toggleNotifications(false);
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            document.getElementById("globalSearchInput").focus();
        }
        if (e.key === "Escape") {
            closePdfModal();
            closeReviewModal();
            closeAuthModal();
            toggleUserDropdown(false);
            document.getElementById("globalSearchResults").hidden = true;
            toggleNotifications(false);
            closeMobileSidebar();
        }
    });
}

// ─── Utilities ───
function showToast(message, isError = false) {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast${isError ? " error" : ""}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4200);
}

function formatRelativeTime(iso) {
    if (!iso) return "Just now";
    const diffSec = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
    if (diffSec < 60) return "Just now";
    const mins = Math.floor(diffSec / 60);
    if (mins < 60) return `${mins} min${mins > 1 ? "s" : ""} ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs} hour${hrs > 1 ? "s" : ""} ago`;
    const days = Math.floor(hrs / 24);
    if (days < 30) return `${days} day${days > 1 ? "s" : ""} ago`;
    return new Date(iso).toLocaleDateString();
}

function escapeHtml(str) {
    return String(str ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function escapeAttr(str) {
    return escapeHtml(str).replace(/'/g, "&#39;");
}

// ─── Lab Sheet Auto-Fill (PDF / Image / TXT) ───
function handleLabSheetDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove("dragover");
    const file = event.dataTransfer.files && event.dataTransfer.files[0];
    if (file) handleLabSheetFile(file);
}

async function handleLabSheetFile(file) {
    if (!file) return;
    const banner = document.getElementById("labsheetDropzone");
    const titleEl = document.getElementById("labsheetTitle");
    const statusEl = document.getElementById("labsheetStatus");

    banner.classList.add("loading");
    titleEl.textContent = `Parsing "${file.name}" with AI...`;
    statusEl.textContent = "Extracting course info, lab title, tasks, and requirements...";

    try {
        const cfg = loadSettings();
        const fd = new FormData();
        fd.append("file", file);
        fd.append("groq_api_key", document.getElementById("groqApiKey").value.trim() || cfg.groqKey || "");

        const res = await fetch("/api/parse-labsheet", {
            method: "POST",
            body: fd,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Could not parse lab sheet");

        if (data.course_code) document.getElementById("courseCode").value = data.course_code;
        if (data.course_title) document.getElementById("courseTitle").value = data.course_title;
        if (data.lab_number) document.getElementById("labNumber").value = parseInt(data.lab_number, 10) || 1;
        if (data.lab_title) document.getElementById("labTitle").value = data.lab_title;
        if (data.language && LANG_META[data.language]) {
            document.getElementById("language").value = data.language;
        }

        if (Array.isArray(data.tasks) && data.tasks.length) {
            clearTasks();
            data.tasks.forEach((t) => addTask({
                title: t.title || "",
                description: t.description || "",
                requirements: Array.isArray(t.requirements) ? t.requirements : [],
            }));
        }

        showToast(`Auto-filled ${data.tasks?.length || 1} task(s) from "${file.name}"!`);
    } catch (err) {
        showToast(err.message, true);
    } finally {
        banner.classList.remove("loading");
        titleEl.textContent = "Auto-Fill from Lab Sheet (PDF, PNG, JPG, or TXT)";
        statusEl.textContent = "Drop your teacher's lab manual PDF or question screenshot here to extract course info, tasks, and requirements automatically.";
    }
}

// ─── Review & Edit Studio (Prepare -> Edit -> Compile) ───
async function prepareAndReview() {
    const payload = collectFormPayload();
    if (!payload.student_name || !payload.student_id) {
        showToast("Student name and ID are required.", true);
        return;
    }
    if (!payload.tasks.length) {
        showToast("Please add at least one lab task.", true);
        return;
    }

    const overlay = document.getElementById("progressOverlay");
    const titleEl = document.getElementById("overlayTitle");
    const statusEl = document.getElementById("overlayStatus");
    const bar = document.getElementById("progressBar");
    const reviewBtn = document.getElementById("reviewBtn");

    overlay.hidden = false;
    reviewBtn.disabled = true;
    titleEl.textContent = "Preparing Editable Report";
    bar.style.width = "20%";
    statusEl.textContent = "Generating methodology, source code, and running self-healing checks...";

    const timer = setInterval(() => {
        const cur = parseInt(bar.style.width, 10) || 20;
        if (cur < 85) bar.style.width = `${cur + 15}%`;
    }, 3000);

    try {
        const res = await fetch("/api/prepare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Preparation failed");

        state.preparedReport = data;
        renderReviewModal(data);
        document.getElementById("reviewModal").hidden = false;
        showToast("Content ready! Review or edit anything before compiling.");
    } catch (err) {
        showToast(err.message, true);
    } finally {
        clearInterval(timer);
        overlay.hidden = true;
        titleEl.textContent = "Generating Your Lab Report";
        reviewBtn.disabled = false;
    }
}

function renderReviewModal(report) {
    document.getElementById("reviewModalTitle").textContent = `Review: ${report.lab_title || `Lab Report ${report.lab_number}`}`;
    document.getElementById("reviewModalSub").textContent = `${report.course_code || ""} ${report.course_title || ""} • ${(LANG_META[report.language]?.label || report.language)}`;

    const body = document.getElementById("reviewModalBody");
    body.innerHTML = (report.tasks || []).map((t, ti) => {
        const methHtml = (t.methodology || []).map((m, mi) => `
            <div class="review-meth-row" data-meth-idx="${mi}">
                <input type="text" class="rev-meth-title" value="${escapeAttr(m.title || "")}" placeholder="Point title">
                <input type="text" class="rev-meth-desc" value="${escapeAttr(m.description || "")}" placeholder="Technical description">
            </div>
        `).join("");

        const figsHtml = (t.images || []).length
            ? `
                <div class="field">
                    <label>Captured Figures (${t.images.length})</label>
                    <div class="review-figs-grid">
                        ${t.images.map((im, fi) => `
                            <div class="review-fig-card">
                                <img src="${im.data}" alt="Figure ${fi + 1}">
                                <input type="text" class="rev-fig-cap" data-fig-idx="${fi}" value="${escapeAttr(im.caption || "")}" placeholder="Figure caption">
                            </div>
                        `).join("")}
                    </div>
                </div>
            `
            : "";

        return `
            <div class="review-task-block" data-rev-task="${ti}">
                <div class="review-task-head">
                    <strong>Task ${ti + 1}: ${escapeHtml(t.title)}</strong>
                    <div class="review-badges">
                        <span class="engine-pill">Engine: ${escapeHtml(t.exec_engine || "local")}</span>
                        ${t.self_healed ? `<span class="status-pill status-completed">Self-Healed</span>` : ""}
                    </div>
                </div>
                <div class="field">
                    <label>1. Problem Overview</label>
                    <textarea rows="3" class="rev-overview">${escapeHtml(t.problem_overview || "")}</textarea>
                </div>
                <div class="field">
                    <label>2. Methodology Points</label>
                    <div class="rev-meth-list">${methHtml}</div>
                </div>
                <div class="field-row-2">
                    <div class="field">
                        <label>3. Source Filename</label>
                        <input type="text" class="rev-filename" value="${escapeAttr(t.filename || "main.py")}">
                    </div>
                    <div class="field">
                        <label>Task Title</label>
                        <input type="text" class="rev-title" value="${escapeAttr(t.title || "")}">
                    </div>
                </div>
                <div class="field">
                    <label>Source Code</label>
                    <textarea rows="8" class="custom-code-area rev-code">${escapeHtml(t.code || "")}</textarea>
                </div>
                <div class="field">
                    <label>4. Execution Output (stdout)</label>
                    <textarea rows="4" class="custom-code-area rev-output">${escapeHtml(t.output || "")}</textarea>
                </div>
                ${figsHtml}
                <div class="field">
                    <label>5. Result and Discussion</label>
                    <textarea rows="4" class="rev-discussion">${escapeHtml(t.result_discussion || "")}</textarea>
                </div>
            </div>
        `;
    }).join("");
}

function closeReviewModal() {
    document.getElementById("reviewModal").hidden = true;
}

async function compileReviewedReport() {
    if (!state.preparedReport) return;
    if (!ensureAuthenticated("Sign in or create an account to compile and download your final reviewed PDF report.", () => {
        compileReviewedReport();
    })) {
        return;
    }
    const btn = document.getElementById("compileFinalBtn");
    btn.disabled = true;
    btn.textContent = "Compiling PDF...";

    try {
        const edited = structuredClone(state.preparedReport);
        document.querySelectorAll("#reviewModalBody .review-task-block").forEach((block, ti) => {
            const task = edited.tasks[ti];
            if (!task) return;
            task.title = block.querySelector(".rev-title").value.trim() || task.title;
            task.filename = block.querySelector(".rev-filename").value.trim() || task.filename;
            task.problem_overview = block.querySelector(".rev-overview").value.trim();
            task.code = block.querySelector(".rev-code").value;
            task.output = block.querySelector(".rev-output").value;
            task.result_discussion = block.querySelector(".rev-discussion").value.trim();
            task.methodology = Array.from(block.querySelectorAll(".review-meth-row")).map((row) => ({
                title: row.querySelector(".rev-meth-title").value.trim(),
                description: row.querySelector(".rev-meth-desc").value.trim(),
            })).filter((m) => m.title || m.description);
            block.querySelectorAll(".rev-fig-cap").forEach((inp) => {
                const fi = parseInt(inp.dataset.figIdx, 10);
                if (task.images?.[fi]) task.images[fi].caption = inp.value.trim();
            });
        });

        const res = await fetch("/api/compile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(edited),
        });
        if (!res.ok) {
            let msg = `Compilation failed (HTTP ${res.status})`;
            try { msg = (await res.json()).detail || msg; } catch {}
            throw new Error(msg);
        }

        const reportId = res.headers.get("X-Report-Id");
        const hasLatexZip = res.headers.get("X-Has-Latex-Zip") === "true";
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${edited.student_id}_Lab${edited.lab_number}_Report.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 4000);

        if (state.activeDraftId) {
            persistDrafts(loadDrafts().filter((d) => d.id !== state.activeDraftId));
            state.activeDraftId = null;
        }

        closeReviewModal();
        await fetchDashboardData();
        showToast("Edited report compiled to PDF + Overleaf .zip!");
        if (reportId) {
            openPdfPreview(reportId, edited.lab_title || `Lab Report ${edited.lab_number}`, edited.course_title, hasLatexZip);
        }
    } catch (err) {
        showToast(err.message, true);
    } finally {
        btn.disabled = false;
        btn.textContent = "Compile Final PDF";
    }
}

// ==========================================================================
// Firebase Authentication & User State Controller
// ==========================================================================

let firebaseApp = null;
let firebaseAuth = null;
let firestoreDb = null;

async function initFirebaseAuth() {
    try {
        if (typeof firebase === "undefined") {
            console.warn("Firebase SDK not loaded yet.");
            return;
        }

        const res = await fetch("/api/firebase-config");
        if (!res.ok) return;
        const cfg = await res.json();
        if (!cfg.apiKey) return;

        if (!firebase.apps.length) {
            firebaseApp = firebase.initializeApp(cfg);
        } else {
            firebaseApp = firebase.app();
        }

        firebaseAuth = firebase.auth();
        firestoreDb = firebase.firestore();

        firebaseAuth.onAuthStateChanged((user) => {
            handleAuthStateChanged(user);
        });

        // Close user dropdown when clicking outside
        document.addEventListener("click", (e) => {
            const wrap = document.getElementById("userMenuRel");
            const menu = document.getElementById("userDropdownMenu");
            if (menu && !menu.hidden && wrap && !wrap.contains(e.target)) {
                menu.hidden = true;
            }
        });
    } catch (err) {
        console.error("Firebase auth initialization error:", err);
    }
}

function handleAuthStateChanged(user) {
    state.currentUser = user;
    const btnSignIn = document.getElementById("btnTopbarSignIn");
    const userMenu = document.getElementById("userMenuRel");
    const avatarText = document.getElementById("topbarAvatarText");
    const avatarImg = document.getElementById("topbarAvatarImg");
    const sideAvatar = document.getElementById("sidebarAvatar");
    const sideAvatarImg = document.getElementById("sidebarAvatarImg");
    const sideName = document.getElementById("sidebarProfileName");
    const sideSub = document.getElementById("sidebarProfileSub");
    const dropName = document.getElementById("dropdownUserName");
    const dropEmail = document.getElementById("dropdownUserEmail");
    const dropBadge = document.getElementById("dropdownUserBadge");
    const greetingTitle = document.getElementById("greetingTitle");
    const verifBanner = document.getElementById("emailVerificationBanner");

    const timeOfDay = getGreetingPeriod();

    if (user) {
        if (btnSignIn) {
            btnSignIn.hidden = true;
            btnSignIn.style.display = "none";
        }
        if (userMenu) {
            userMenu.hidden = false;
            userMenu.style.display = "block";
        }

        const displayName = user.displayName || user.email.split("@")[0] || "Student";
        const firstName = displayName.split(" ")[0];
        const initials = getInitials(displayName);

        if (greetingTitle) {
            greetingTitle.textContent = `Good ${timeOfDay}, ${firstName}! 👋`;
        }

        if (sideName) sideName.textContent = displayName;
        if (sideSub) sideSub.textContent = user.email;
        if (dropName) dropName.textContent = displayName;
        if (dropEmail) dropEmail.textContent = user.email;

        // Avatar handling
        if (user.photoURL) {
            if (avatarImg) {
                avatarImg.src = user.photoURL;
                avatarImg.hidden = false;
            }
            if (avatarText) avatarText.hidden = true;
            if (sideAvatarImg) {
                sideAvatarImg.src = user.photoURL;
                sideAvatarImg.hidden = false;
            }
            if (sideAvatar) sideAvatar.hidden = true;
        } else {
            if (avatarText) {
                avatarText.textContent = initials;
                avatarText.hidden = false;
            }
            if (avatarImg) avatarImg.hidden = true;
            if (sideAvatar) {
                sideAvatar.textContent = initials;
                sideAvatar.hidden = false;
            }
            if (sideAvatarImg) sideAvatarImg.hidden = true;
        }

        // Email verification handling
        const isPasswordAuth = user.providerData?.some((p) => p.providerId === "password");
        if (dropBadge) {
            if (user.emailVerified || !isPasswordAuth) {
                dropBadge.textContent = "Verified";
                dropBadge.className = "user-badge badge-verified";
                dropBadge.onclick = null;
                dropBadge.style.cursor = "default";
            } else {
                dropBadge.textContent = "Unverified • Send Link";
                dropBadge.className = "user-badge badge-unverified";
                dropBadge.style.cursor = "pointer";
                dropBadge.onclick = () => resendVerificationLink();
            }
        }

        if (verifBanner) {
            if (!user.emailVerified && isPasswordAuth) {
                verifBanner.hidden = false;
                verifBanner.style.display = "flex";
                const emailSpan = document.getElementById("verifEmailText");
                if (emailSpan) emailSpan.textContent = user.email;
            } else {
                verifBanner.hidden = true;
                verifBanner.style.display = "none";
            }
        }

        updateProfileHeroCard(user);
        syncUserProfileFromFirestore(user);

        // Resume pending user action only once email is verified (or using OAuth provider)
        if (state.pendingAuthAction && (user.emailVerified || !isPasswordAuth)) {
            const pending = state.pendingAuthAction;
            state.pendingAuthAction = null;
            setTimeout(() => pending(), 250);
        }
    } else {
        if (btnSignIn) {
            btnSignIn.hidden = false;
            btnSignIn.style.display = "inline-flex";
        }
        if (userMenu) {
            userMenu.hidden = true;
            userMenu.style.display = "none";
        }
        if (greetingTitle) greetingTitle.textContent = `Good ${timeOfDay}, Student! 👋`;
        if (sideName) sideName.textContent = "Guest Student";
        if (sideSub) sideSub.textContent = "Click to Sign In";
        if (sideAvatar) {
            sideAvatar.textContent = "SM";
            sideAvatar.hidden = false;
        }
        if (sideAvatarImg) sideAvatarImg.hidden = true;
        if (verifBanner) {
            verifBanner.hidden = true;
            verifBanner.style.display = "none";
        }

        updateProfileHeroCard(null);
    }
}

function updateProfileHeroCard(user) {
    const cardName = document.getElementById("profCardName");
    const cardEmail = document.getElementById("profCardEmail");
    const cardBadge = document.getElementById("profCardBadge");
    const tagProvider = document.getElementById("profTagProvider");
    const tagReports = document.getElementById("profTagReports");
    const tagSync = document.getElementById("profTagSync");
    const avatar = document.getElementById("profCardAvatar");
    const avatarImg = document.getElementById("profCardAvatarImg");
    const btnSignIn = document.getElementById("btnProfSignIn");
    const btnSignOut = document.getElementById("btnProfSignOut");
    const btnResetPass = document.getElementById("btnProfResetPass");

    if (!cardName) return;

    if (user) {
        const isGoogle = user.providerData?.some((p) => p.providerId === "google.com");
        const displayName = user.displayName || user.email.split("@")[0] || "Student";
        const initials = getInitials(displayName);

        cardName.textContent = displayName;
        cardEmail.textContent = user.email;

        if (user.emailVerified || isGoogle) {
            cardBadge.textContent = "Verified Student";
            cardBadge.className = "user-badge badge-verified";
        } else {
            cardBadge.textContent = "Email Unverified";
            cardBadge.className = "user-badge badge-unverified";
        }

        if (tagProvider) tagProvider.textContent = isGoogle ? "Provider: Google Account" : "Provider: Email / Password";
        if (tagReports) tagReports.textContent = `Total Reports: ${state.stats?.total_reports || state.reports?.length || 0}`;
        if (tagSync) tagSync.textContent = "Cloud Sync: Active";

        if (user.photoURL) {
            if (avatarImg) {
                avatarImg.src = user.photoURL;
                avatarImg.hidden = false;
            }
            if (avatar) avatar.hidden = true;
        } else {
            if (avatar) {
                avatar.textContent = initials;
                avatar.hidden = false;
            }
            if (avatarImg) avatarImg.hidden = true;
        }

        if (btnSignIn) btnSignIn.hidden = true;
        if (btnSignOut) btnSignOut.hidden = false;
        if (btnResetPass) btnResetPass.hidden = isGoogle;
    } else {
        cardName.textContent = "Guest Student";
        cardEmail.textContent = "Sign in to save reports and sync student profile across all devices.";
        cardBadge.textContent = "Guest Mode";
        cardBadge.className = "user-badge";

        if (tagProvider) tagProvider.textContent = "Provider: Local Guest";
        if (tagReports) tagReports.textContent = `Total Reports: ${state.stats?.total_reports || state.reports?.length || 0}`;
        if (tagSync) tagSync.textContent = "Cloud Sync: Off";

        if (avatar) {
            avatar.textContent = "SM";
            avatar.hidden = false;
        }
        if (avatarImg) avatarImg.hidden = true;

        if (btnSignIn) btnSignIn.hidden = false;
        if (btnSignOut) btnSignOut.hidden = true;
        if (btnResetPass) btnResetPass.hidden = true;
    }
}

// ─── Authentication Gatekeeper (Soft Wall) ───
function ensureAuthenticated(actionDescription, retryCallback) {
    if (!state.currentUser) {
        state.pendingAuthAction = typeof retryCallback === "function" ? retryCallback : null;
        openAuthModal("signup", actionDescription || "Sign in or create an account in 10 seconds to download and save your PDF report.");
        showToast("Please sign in or create an account to view or download reports.", true);
        return false;
    }

    const isPasswordAuth = state.currentUser.providerData?.some((p) => p.providerId === "password");
    if (!state.currentUser.emailVerified && isPasswordAuth) {
        state.pendingAuthAction = typeof retryCallback === "function" ? retryCallback : null;
        showToast("Please verify your email address before downloading your PDF. Check your inbox!", true);
        const banner = document.getElementById("emailVerificationBanner");
        if (banner) {
            banner.hidden = false;
            banner.style.display = "flex";
            banner.scrollIntoView({ behavior: "smooth" });
        }
        return false;
    }

    return true;
}

function triggerFileDownload(url) {
    const a = document.createElement("a");
    a.href = url;
    a.download = "";
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function downloadReportDirect(reportId) {
    if (!ensureAuthenticated("Sign in or create an account to download your PDF report.", () => {
        downloadReportDirect(reportId);
    })) {
        return;
    }
    triggerFileDownload(`/api/reports/${reportId}/file`);
}

function downloadLatexDirect(reportId) {
    if (!ensureAuthenticated("Sign in or create an account to download Overleaf LaTeX source.", () => {
        downloadLatexDirect(reportId);
    })) {
        return;
    }
    triggerFileDownload(`/api/reports/${reportId}/latex`);
}

async function checkEmailVerificationStatus() {
    if (!state.currentUser) return;
    try {
        await state.currentUser.reload();
        const updated = firebase.auth().currentUser;
        handleAuthStateChanged(updated);
        if (updated.emailVerified) {
            showToast("Your email address is verified! Full access unlocked.");
        } else {
            showToast("Email not verified yet. Please click the link in your inbox or spam folder.", true);
        }
    } catch (err) {
        showToast(err.message || "Failed to check verification status.", true);
    }
}

async function syncUserProfileFromFirestore(user) {
    if (!firestoreDb || !user) return;
    try {
        const userRef = firestoreDb.collection("users").doc(user.uid);
        const doc = await userRef.get();
        if (doc.exists) {
            const data = doc.data();
            state.userProfile = data;
            const nameInput = document.getElementById("studentName");
            const idInput = document.getElementById("studentId");
            const deptInput = document.getElementById("department");
            if (nameInput && data.displayName) nameInput.value = data.displayName;
            if (idInput && data.studentId) idInput.value = data.studentId;
            if (deptInput && data.department) deptInput.value = data.department;

            // Settings view inputs
            const setName = document.getElementById("setStudentName");
            const setId = document.getElementById("setStudentId");
            const setDept = document.getElementById("setDepartment");
            if (setName && data.displayName) setName.value = data.displayName;
            if (setId && data.studentId) setId.value = data.studentId;
            if (setDept && data.department) setDept.value = data.department;
        } else {
            const ts = firebase.firestore.FieldValue.serverTimestamp();
            const docData = {
                displayName: (user.displayName || user.email.split("@")[0] || "Student").slice(0, 100),
                email: user.email,
                createdAt: ts,
                updatedAt: ts,
            };
            if (user.photoURL && /^https?:\/\//.test(user.photoURL)) {
                docData.photoUrl = user.photoURL.slice(0, 500);
            }
            await userRef.set(docData);
        }
    } catch (e) {
        console.warn("Firestore profile sync notice:", e.message);
    }
}

function getGreetingPeriod() {
    const hour = new Date().getHours();
    if (hour < 12) return "Morning";
    if (hour < 17) return "Afternoon";
    return "Evening";
}

function getInitials(name) {
    if (!name) return "ST";
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    return parts[0].slice(0, 2).toUpperCase();
}

function openAuthModal(defaultTab = "signin", customSub = "") {
    switchAuthTab(defaultTab);
    clearAuthAlert();
    if (customSub) {
        const sub = document.getElementById("authModalSub");
        if (sub) sub.textContent = customSub;
    }
    document.getElementById("authModal").hidden = false;
}

function closeAuthModal(clearPending = true) {
    document.getElementById("authModal").hidden = true;
    clearAuthAlert();
    if (clearPending) {
        state.pendingAuthAction = null;
    }
}

function switchAuthTab(tab) {
    const tabSignIn = document.getElementById("tabSignIn");
    const tabSignUp = document.getElementById("tabSignUp");
    const formSignIn = document.getElementById("signInForm");
    const formSignUp = document.getElementById("signUpForm");
    const title = document.getElementById("authModalTitle");
    const sub = document.getElementById("authModalSub");

    clearAuthAlert();

    if (tab === "signup") {
        tabSignUp.classList.add("active");
        tabSignIn.classList.remove("active");
        formSignUp.hidden = false;
        formSignIn.hidden = true;
        title.textContent = "Create an Account";
        sub.textContent = "Join with email or Google to download and save your lab reports.";
    } else {
        tabSignIn.classList.add("active");
        tabSignUp.classList.remove("active");
        formSignIn.hidden = false;
        formSignUp.hidden = true;
        title.textContent = "Welcome to Lab Report Lagbe?";
        sub.textContent = "Sign in with your Google account or email to sync lab reports across devices.";
    }
}

function toggleUserDropdown(forceState) {
    const menu = document.getElementById("userDropdownMenu");
    if (!menu) return;
    if (typeof forceState === "boolean") {
        menu.hidden = !forceState;
    } else {
        menu.hidden = !menu.hidden;
    }
}

function handleSidebarProfileClick() {
    if (!state.currentUser) {
        openAuthModal("signin");
    } else {
        navigateTo("settings");
    }
}

function showAuthAlert(msg, type = "error") {
    const banner = document.getElementById("authAlertBanner");
    if (!banner) return;
    banner.textContent = msg;
    banner.className = `auth-alert-box ${type}`;
    banner.hidden = false;
}

function clearAuthAlert() {
    const banner = document.getElementById("authAlertBanner");
    if (banner) {
        banner.hidden = true;
        banner.textContent = "";
        banner.className = "auth-alert-box";
    }
}

async function handleGoogleSignIn() {
    if (!firebaseAuth) {
        showToast("Firebase Auth is not ready.", true);
        return;
    }
    const btn = document.getElementById("btnGoogleAuth");
    btn.disabled = true;
    clearAuthAlert();

    try {
        const provider = new firebase.auth.GoogleAuthProvider();
        provider.setCustomParameters({ prompt: "select_account" });
        const result = await firebaseAuth.signInWithPopup(provider);
        closeAuthModal(false);
        showToast(`Signed in as ${result.user.displayName || result.user.email}!`);
    } catch (err) {
        if (err.code === "auth/popup-closed-by-user") {
            showAuthAlert("Sign-in window closed before completing.", "warning");
        } else {
            showAuthAlert(err.message || "Failed to sign in with Google.");
        }
    } finally {
        btn.disabled = false;
    }
}

async function handleEmailSignIn(event) {
    event.preventDefault();
    if (!firebaseAuth) return;

    const email = document.getElementById("authSignInEmail").value.trim();
    const pass = document.getElementById("authSignInPassword").value;
    const btn = document.getElementById("btnSubmitSignIn");

    btn.disabled = true;
    clearAuthAlert();

    try {
        const result = await firebaseAuth.signInWithEmailAndPassword(email, pass);
        closeAuthModal(false);
        showToast(`Welcome back, ${result.user.displayName || result.user.email}!`);
    } catch (err) {
        let msg = "Invalid email or password.";
        if (err.code === "auth/user-not-found") msg = "No account found with this email.";
        else if (err.code === "auth/wrong-password" || err.code === "auth/invalid-credential") msg = "Invalid email or password.";
        else if (err.code === "auth/too-many-requests") msg = "Too many failed attempts. Try again later.";
        showAuthAlert(msg, "error");
    } finally {
        btn.disabled = false;
    }
}

async function handleEmailSignUp(event) {
    event.preventDefault();
    if (!firebaseAuth) return;

    const name = document.getElementById("authSignUpName").value.trim();
    const studentId = document.getElementById("authSignUpStudentId").value.trim();
    const dept = document.getElementById("authSignUpDept").value.trim();
    const email = document.getElementById("authSignUpEmail").value.trim();
    const pass = document.getElementById("authSignUpPassword").value;
    const btn = document.getElementById("btnSubmitSignUp");

    btn.disabled = true;
    clearAuthAlert();

    try {
        const cred = await firebaseAuth.createUserWithEmailAndPassword(email, pass);
        const user = cred.user;

        // Set user profile display name
        await user.updateProfile({ displayName: name });

        // Send email verification link
        await user.sendEmailVerification();

        // Save initial student details in Firestore using server timestamps (matches firestore.rules)
        if (firestoreDb) {
            const ts = firebase.firestore.FieldValue.serverTimestamp();
            await firestoreDb.collection("users").doc(user.uid).set({
                displayName: name.slice(0, 100),
                studentId: studentId.slice(0, 50),
                department: dept.slice(0, 100),
                email: email,
                createdAt: ts,
                updatedAt: ts,
            });
        }

        // Refresh UI state with updated displayName immediately
        handleAuthStateChanged(firebaseAuth.currentUser || user);

        showAuthAlert(`Account created! A verification link has been sent to ${email}. Please check your inbox and verify your email.`, "success");
        showToast("Verification link sent to your email!");
    } catch (err) {
        let msg = err.message;
        if (err.code === "auth/email-already-in-use") msg = "An account already exists with this email.";
        else if (err.code === "auth/weak-password") msg = "Password should be at least 6 characters.";
        else if (err.code === "auth/invalid-email") msg = "Please enter a valid email address.";
        showAuthAlert(msg, "error");
    } finally {
        btn.disabled = false;
    }
}

async function handleForgotPassword() {
    if (!firebaseAuth) return;
    const email = document.getElementById("authSignInEmail").value.trim() || prompt("Enter your registered email address:");
    if (!email) return;

    try {
        await firebaseAuth.sendPasswordResetEmail(email);
        showAuthAlert(`Password reset link sent to ${email}. Check your inbox!`, "success");
        showToast("Password reset email sent.");
    } catch (err) {
        showAuthAlert(err.message || "Failed to send password reset email.", "error");
    }
}

async function resendVerificationLink() {
    if (!state.currentUser) return;
    try {
        await state.currentUser.sendEmailVerification();
        showToast("Verification email sent! Please check your inbox.");
    } catch (err) {
        showToast(err.message || "Could not send verification email.", true);
    }
}

async function handleSignOut() {
    if (!firebaseAuth) return;
    try {
        state.pendingAuthAction = null;
        await firebaseAuth.signOut();
        showToast("Signed out successfully.");
    } catch (err) {
        showToast(err.message || "Sign out failed.", true);
    }
}
