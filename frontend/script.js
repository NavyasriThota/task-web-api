const form = document.getElementById('studentForm');
const formTitle = document.getElementById('formTitle');
const totalStudents = document.getElementById('totalStudents');
const studentTableBody = document.getElementById('studentTableBody');
const searchInput = document.getElementById('searchInput');
const clearSearchButton = document.getElementById('clearSearchButton');
const resetButton = document.getElementById('resetButton');
const deleteSelectedButton = document.getElementById('deleteSelectedButton');
const searchMessage = document.getElementById('searchMessage');
const tableLoading = document.getElementById('tableLoading');

const state = {
  selectedStudentId: null,
  searchTimer: null,
  loadingTimer: null,
  requestId: 0,
  students: [],
};

function showLoading(message = 'Loading records...') {
  clearTimeout(state.loadingTimer);
  tableLoading.textContent = message;
  state.loadingTimer = window.setTimeout(() => {
    tableLoading.hidden = false;
  }, 180);
}

function hideLoading() {
  clearTimeout(state.loadingTimer);
  state.loadingTimer = null;
  tableLoading.textContent = '';
  tableLoading.hidden = true;
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}) },
    ...options,
  });

  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(typeof data === 'object' ? (data.detail || 'Request failed.') : data || 'Request failed.');
  }

  return data;
}

function formatDate(dateString) {
  if (!dateString) return '—';
  const date = new Date(dateString);
  return Number.isNaN(date.getTime()) ? dateString : date.toLocaleDateString();
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function setStatus(message, isError = false) {
  searchMessage.textContent = message;
  searchMessage.style.color = isError ? '#b91c1c' : '#475569';
}

function resetForm() {
  form.reset();
  state.selectedStudentId = null;
  formTitle.textContent = 'Add Student';
  deleteSelectedButton.hidden = true;
}

function renderTable(students, query = '') {
  if (!students.length) {
    studentTableBody.innerHTML = '<tr><td class="empty-row" colspan="8">No matching students found.</td></tr>';
    setStatus(query ? `No records matched "${query}".` : 'No students available yet.');
    return;
  }

  studentTableBody.innerHTML = students
    .map(
      (student) => `
        <tr>
          <td>${escapeHtml(student.student_id)}</td>
          <td>${escapeHtml(student.first_name)} ${escapeHtml(student.last_name)}</td>
          <td>${escapeHtml(student.email)}</td>
          <td>${escapeHtml(student.phone_number)}</td>
          <td>${escapeHtml(student.course)}</td>
          <td>${escapeHtml(student.batch)}</td>
          <td>${escapeHtml(formatDate(student.created_at))}</td>
          <td>
            <div class="actions">
              <button class="action-btn view-btn" data-action="view" data-id="${student.student_id}">View</button>
              <button class="action-btn edit-btn" data-action="edit" data-id="${student.student_id}">Edit</button>
              <button class="action-btn delete-btn" data-action="delete" data-id="${student.student_id}">Delete</button>
            </div>
          </td>
        </tr>
      `
    )
    .join('');

  setStatus(query ? `Showing ${students.length} result(s) for "${query}".` : '');
}

function applyStudentListUpdate(student, operation) {
  const list = [...state.students];

  if (operation === 'create') {
    state.students = [student, ...list];
  }

  if (operation === 'update') {
    state.students = list.map((item) => (item.student_id === student.student_id ? { ...item, ...student } : item));
  }

  if (operation === 'delete') {
    state.students = list.filter((item) => item.student_id !== student.student_id);
  }

  const searchQuery = searchInput.value.trim();
  const visibleStudents = searchQuery.length >= 3
    ? state.students.filter((item) => {
        const fullName = `${item.first_name} ${item.last_name}`.toLowerCase();
        const query = searchQuery.toLowerCase();
        return fullName.includes(query) || item.email.toLowerCase().includes(query);
      })
    : state.students;

  totalStudents.textContent = String(state.students.length);
  renderTable(visibleStudents, searchQuery);
}

async function loadStudents() {
  const query = searchInput.value.trim();
  const requestId = ++state.requestId;
  const isSearch = query.length >= 3;

  showLoading(isSearch ? `Searching "${query}"...` : 'Loading records...');

  try {
    const endpoint = isSearch
      ? `/api/students/search?name=${encodeURIComponent(query)}`
      : '/api/students?limit=10&offset=0';

    const data = await apiRequest(endpoint);
    if (requestId !== state.requestId) return;

    const students = Array.isArray(data) ? data : data.students || [];
    const totalCount = Array.isArray(data) ? students.length : (data.total ?? students.length);

    if (!isSearch) {
      state.students = students;
    }

    totalStudents.textContent = String(totalCount);
    renderTable(students, query);
  } catch (error) {
    if (requestId !== state.requestId) return;
    setStatus(error.message, true);
    studentTableBody.innerHTML = '<tr><td class="empty-row" colspan="8">Unable to load student data.</td></tr>';
  } finally {
    if (requestId === state.requestId) {
      hideLoading();
    }
  }
}

async function handleFormSubmit(event) {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  const actionLabel = state.selectedStudentId ? 'Updating student...' : 'Saving student...';
  showLoading(actionLabel);

  try {
    let savedStudent;

    if (state.selectedStudentId) {
      savedStudent = await apiRequest(`/api/students/${state.selectedStudentId}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      setStatus('Student updated successfully.');
      applyStudentListUpdate(savedStudent, 'update');
    } else {
      savedStudent = await apiRequest('/api/students', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setStatus('Student added successfully.');
      applyStudentListUpdate(savedStudent, 'create');
    }

    resetForm();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    hideLoading();
  }
}

async function openStudentDetails(studentId) {
  const cachedStudent = state.students.find((item) => item.student_id === studentId);

  try {
    const student = cachedStudent || (await apiRequest(`/api/students/${studentId}`));
    const details = [
      `Student ID: ${student.student_id}`,
      `Name: ${student.first_name} ${student.last_name}`,
      `Email: ${student.email}`,
      `Phone: ${student.phone_number}`,
      `Course: ${student.course}`,
      `Batch: ${student.batch}`,
      `Address: ${student.address || 'No address provided'}`,
    ].join('\n');
    alert(details);
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function fillStudentForm(studentId) {
  try {
    const student = await apiRequest(`/api/students/${studentId}`);
    state.selectedStudentId = student.student_id;
    formTitle.textContent = 'Edit Student';
    deleteSelectedButton.hidden = false;

    Object.entries(student).forEach(([key, value]) => {
      const element = document.getElementById(key);
      if (element) {
        element.value = value || '';
      }
    });
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteStudent(studentId) {
  const confirmed = window.confirm('Are you sure you want to delete this student record?');
  if (!confirmed) return;

  showLoading('Deleting student...');

  try {
    const student = state.students.find((item) => item.student_id === studentId) || { student_id: studentId };
    await apiRequest(`/api/students/${studentId}`, { method: 'DELETE' });
    setStatus('Student deleted successfully.');
    applyStudentListUpdate(student, 'delete');
    resetForm();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    hideLoading();
  }
}

studentTableBody.addEventListener('click', async (event) => {
  const button = event.target.closest('button[data-action]');
  if (!button) return;

  const { action, id } = button.dataset;
  if (action === 'view') {
    await openStudentDetails(Number(id));
  }
  if (action === 'edit') {
    await fillStudentForm(Number(id));
  }
  if (action === 'delete') {
    await deleteStudent(Number(id));
  }
});

form.addEventListener('submit', handleFormSubmit);
resetButton.addEventListener('click', resetForm);
clearSearchButton.addEventListener('click', () => {
  searchInput.value = '';
  setStatus('');
  loadStudents();
});

deleteSelectedButton.addEventListener('click', async () => {
  if (!state.selectedStudentId) return;
  await deleteStudent(state.selectedStudentId);
});

searchInput.addEventListener('input', () => {
  window.clearTimeout(state.searchTimer);
  const query = searchInput.value.trim();

  if (query.length >= 3 || query.length === 0) {
    state.searchTimer = window.setTimeout(() => {
      loadStudents();
    }, 180);
  }
});

window.addEventListener('DOMContentLoaded', async () => {
  resetForm();
  await loadStudents();
});
