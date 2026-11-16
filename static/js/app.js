// task counter
let taskCount = 0;

// add initial task on load
document.addEventListener('DOMContentLoaded', () => {
    addTask();
    loadSavedData();
});

function addTask() {
    taskCount++;
    const container = document.getElementById('tasksContainer');
    const taskDiv = document.createElement('div');
    taskDiv.className = 'task-card';
    taskDiv.id = `task-${taskCount}`;
    taskDiv.innerHTML = `
        <div class="task-card-header">
            <span class="task-number">Task ${container.children.length + 1}</span>
            <button type="button" class="btn-remove" onclick="removeTask('${taskDiv.id}')" title="Remove task">&times;</button>
        </div>
        <div class="field">
            <label>Task Title *</label>
            <input type="text" name="task_title" placeholder="e.g. Student Result Management System" required>
        </div>
        <div class="field">
            <label>Description</label>
            <textarea name="task_description" placeholder="Describe what the program should do..."></textarea>
        </div>
        <div class="field">
            <label>Requirements</label>
            <div class="requirements-list" id="reqs-${taskCount}"></div>
            <button type="button" class="btn-req-add" onclick="addRequirement('reqs-${taskCount}')">+ Add requirement</button>
        </div>
    `;
    container.appendChild(taskDiv);
}

function removeTask(id) {
    const container = document.getElementById('tasksContainer');
    if (container.children.length <= 1) return; // keep at least 1
    document.getElementById(id).remove();
    renumberTasks();
}

function renumberTasks() {
    const tasks = document.querySelectorAll('#tasksContainer .task-card');
    tasks.forEach((task, i) => {
        task.querySelector('.task-number').textContent = `Task ${i + 1}`;
    });
}

function addRequirement(containerId) {
    const container = document.getElementById(containerId);
    const row = document.createElement('div');
    row.className = 'req-row';
    row.innerHTML = `
        <input type="text" name="requirement" placeholder="e.g. Create a Student class with name, ID, marks">
        <button type="button" class="btn-req-remove" onclick="this.parentElement.remove()">&times;</button>
    `;
    container.appendChild(row);
}

function toggleCard(header) {
    const body = header.nextElementSibling;
    const arrow = header.querySelector('.collapse-arrow');
    body.classList.toggle('collapsed');
    arrow.classList.toggle('open');
}

// collect form data
function collectFormData() {
    const form = document.getElementById('reportForm');
    const tasks = [];
    document.querySelectorAll('#tasksContainer .task-card').forEach(card => {
        const title = card.querySelector('[name="task_title"]').value.trim();
        const description = card.querySelector('[name="task_description"]').value.trim();
        const reqs = [];
        card.querySelectorAll('[name="requirement"]').forEach(input => {
            if (input.value.trim()) reqs.push(input.value.trim());
        });
        if (title) {
            tasks.push({ title, description, requirements: reqs });
        }
    });

    return {
        groq_api_key: form.querySelector('#groqApiKey').value.trim(),
        student_name: form.querySelector('#studentName').value.trim(),
        student_id: form.querySelector('#studentId').value.trim(),
        session: form.querySelector('#session').value.trim(),
        university: form.querySelector('#university').value.trim(),
        university_short: form.querySelector('#universityShort').value.trim(),
        department: form.querySelector('#department').value.trim(),
        department_short: form.querySelector('#departmentShort').value.trim(),
        faculty: form.querySelector('#faculty').value.trim(),
        course_code: form.querySelector('#courseCode').value.trim(),
        course_title: form.querySelector('#courseTitle').value.trim(),
        instructor_name: form.querySelector('#instructorName').value.trim(),
        instructor_title: form.querySelector('#instructorTitle').value.trim(),
        lab_number: parseInt(form.querySelector('#labNumber').value) || 1,
        lab_title: form.querySelector('#labTitle').value.trim(),
        lab_subtitle: form.querySelector('#labSubtitle').value.trim(),
        language: form.querySelector('#language').value,
        github_link: form.querySelector('#githubLink').value.trim(),
        tasks: tasks,
    };
}

// save/load form data to localStorage
function saveFormData() {
    const data = collectFormData();
    delete data.groq_api_key; // dont save API key
    delete data.tasks;
    localStorage.setItem('labReportData', JSON.stringify(data));
}

function loadSavedData() {
    const saved = localStorage.getItem('labReportData');
    if (!saved) return;
    try {
        const data = JSON.parse(saved);
        const fields = {
            studentName: data.student_name,
            studentId: data.student_id,
            session: data.session,
            university: data.university,
            universityShort: data.university_short,
            department: data.department,
            departmentShort: data.department_short,
            faculty: data.faculty,
            courseCode: data.course_code,
            courseTitle: data.course_title,
            instructorName: data.instructor_name,
            instructorTitle: data.instructor_title,
            labNumber: data.lab_number,
            labTitle: data.lab_title,
            labSubtitle: data.lab_subtitle,
            language: data.language,
            githubLink: data.github_link,
        };
        for (const [id, value] of Object.entries(fields)) {
            const el = document.getElementById(id);
            if (el && value) el.value = value;
        }
    } catch (e) { /* ignore */ }
}

// progress simulation
function showProgress() {
    const overlay = document.getElementById('progressOverlay');
    const bar = document.getElementById('progressBar');
    const status = document.getElementById('overlayStatus');
    overlay.style.display = 'flex';

    const steps = [
        { pct: 10, text: 'Sending request to AI...' },
        { pct: 25, text: 'AI is writing code for Task 1...' },
        { pct: 40, text: 'Running code through sandbox...' },
        { pct: 55, text: 'AI is writing code for Task 2...' },
        { pct: 70, text: 'Compiling code outputs...' },
        { pct: 82, text: 'Building LaTeX report...' },
        { pct: 92, text: 'Compiling PDF...' },
    ];

    let i = 0;
    const interval = setInterval(() => {
        if (i < steps.length) {
            bar.style.width = steps[i].pct + '%';
            status.textContent = steps[i].text;
            i++;
        }
    }, 3000);

    return { interval, bar, status, overlay };
}

function hideProgress(progress) {
    clearInterval(progress.interval);
    progress.overlay.style.display = 'none';
}

// toast notifications
function showToast(message, type = 'error') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// form submission
document.getElementById('reportForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = collectFormData();

    if (!data.groq_api_key) {
        showToast('Please enter your Groq API key.');
        return;
    }
    if (!data.student_name || !data.student_id) {
        showToast('Student name and ID are required.');
        return;
    }
    if (data.tasks.length === 0) {
        showToast('Add at least one task with a title.');
        return;
    }

    saveFormData();

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.querySelector('.btn-text').style.display = 'none';
    btn.querySelector('.btn-loading').style.display = 'inline-flex';

    const progress = showProgress();

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Report generation failed.');
        }

        // download the PDF
        progress.bar.style.width = '100%';
        progress.status.textContent = 'Done! Downloading PDF...';

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${data.student_id}_Report_${data.lab_number}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);

        showToast('Report generated successfully!', 'success');

    } catch (err) {
        showToast(err.message);
    } finally {
        hideProgress(progress);
        btn.disabled = false;
        btn.querySelector('.btn-text').style.display = 'inline';
        btn.querySelector('.btn-loading').style.display = 'none';
    }
});
