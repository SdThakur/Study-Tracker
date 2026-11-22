/**
 * Study Tracker — Client Application Logic
 */

const API_BASE = '';

// App State
const state = {
  token: localStorage.getItem('study_tracker_token') || null,
  user: null,
  courses: [],
  sessions: [],
  stats: null,
  activeTab: 'dashboard',
  filters: {
    courseId: '',
    startDate: '',
    endDate: '',
  },
  timer: {
    intervalId: null,
    seconds: 0,
    running: false,
    selectedCourseId: null,
  }
};

// ==================== API Service ====================
async function apiRequest(endpoint, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }
  if (options.body && !headers['Content-Type']) {
    if (options.body instanceof URLSearchParams) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded';
    } else if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    const hadToken = !!state.token;
    state.token = null;
    state.user = null;
    localStorage.removeItem('study_tracker_token');
    updateAuthUI();
    if (hadToken && endpoint !== '/auth/token') {
      showToast('Session expired. Please sign in.', 'error');
    }
    const errData = await response.json().catch(() => null);
    throw new Error(errData?.detail || 'Incorrect username or password');
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    let errorMsg = 'An error occurred';
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        errorMsg = data.detail;
      } else if (Array.isArray(data.detail)) {
        errorMsg = data.detail.map(e => e.msg || e.detail || JSON.stringify(e)).join(', ');
      } else {
        errorMsg = JSON.stringify(data.detail);
      }
    }
    throw new Error(errorMsg);
  }

  return data;
}

// ==================== Toast Notifications ====================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `pointer-events-auto px-4 py-2.5 rounded-lg text-xs font-medium shadow-md transition-all duration-200 transform translate-y-2 opacity-0 flex items-center space-x-2 border ${
    type === 'error'
      ? 'bg-rose-50 text-rose-900 border-rose-200'
      : type === 'success'
      ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
      : 'bg-white text-zinc-900 border-zinc-200'
  }`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  // Animate in
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// ==================== Auth & Profile ====================
async function checkAuth() {
  if (!state.token) {
    updateAuthUI();
    loadPublicDemo();
    return;
  }
  try {
    const user = await apiRequest('/auth/me');
    state.user = user;
    updateAuthUI();
    await refreshAllData();
  } catch (err) {
    updateAuthUI();
  }
}

function updateAuthUI() {
  const userMenu = document.getElementById('user-menu');
  const btnOpenAuth = document.getElementById('btn-open-auth');
  const userPill = document.getElementById('user-pill');
  const guestBanner = document.getElementById('guest-banner');

  if (state.user) {
    userMenu.classList.remove('hidden');
    userMenu.classList.add('flex');
    btnOpenAuth.classList.add('hidden');
    userPill.textContent = `@${state.user.username}`;
    guestBanner.classList.add('hidden');
  } else {
    userMenu.classList.add('hidden');
    userMenu.classList.remove('flex');
    btnOpenAuth.classList.remove('hidden');
    guestBanner.classList.remove('hidden');
  }
}

// ==================== Data Fetching ====================
async function refreshAllData() {
  if (!state.token) return;
  try {
    const [courses, stats] = await Promise.all([
      apiRequest('/courses/'),
      apiRequest('/stats/'),
    ]);
    state.courses = courses;
    state.stats = stats;

    renderCourses();
    renderStats();
    populateCourseDropdowns();
    await fetchSessions();
  } catch (err) {
    console.error('Failed to load data:', err);
  }
}

async function fetchSessions() {
  if (!state.token) return;
  try {
    let url = '/sessions/?limit=50';
    if (state.filters.courseId) url += `&course_id=${state.filters.courseId}`;
    if (state.filters.startDate) url += `&start_date=${state.filters.startDate}`;
    if (state.filters.endDate) url += `&end_date=${state.filters.endDate}`;

    const sessions = await apiRequest(url);
    state.sessions = sessions;
    renderSessions();
    renderRecentSessions();
  } catch (err) {
    console.error('Failed to fetch sessions:', err);
  }
}

function loadPublicDemo() {
  // Clear displays for unauthenticated state
  document.getElementById('stat-total-hours').textContent = '0.0';
  document.getElementById('stat-weekly-streak').textContent = '0';
  document.getElementById('stat-total-sessions').textContent = '0';
  document.getElementById('stat-course-count').textContent = '0';
  document.getElementById('header-streak-count').textContent = '0';

  document.getElementById('course-progress-list').innerHTML = `
    <div class="text-xs text-zinc-400 py-6 text-center">
      Sign in to view your course study progress and weekly streaks.
    </div>
  `;
  document.getElementById('courses-grid').innerHTML = `
    <div class="col-span-full py-12 text-center text-xs text-zinc-400">
      Please sign in to view and create courses.
    </div>
  `;
  document.getElementById('sessions-table-body').innerHTML = `
    <tr><td colspan="5" class="py-12 text-center text-zinc-400">Please sign in to view your logged study sessions.</td></tr>
  `;
  document.getElementById('recent-sessions-tbody').innerHTML = `
    <tr><td colspan="4" class="py-6 text-center text-zinc-400">No session records to show.</td></tr>
  `;
}

// ==================== Render Functions ====================
function renderStats() {
  if (!state.stats) return;
  const totalHours = (state.stats.total_minutes / 60).toFixed(1);
  document.getElementById('stat-total-hours').textContent = totalHours;
  document.getElementById('stat-total-minutes-sub').textContent = `${state.stats.total_minutes} min logged`;
  document.getElementById('stat-weekly-streak').textContent = state.stats.weekly_streak;
  document.getElementById('stat-total-sessions').textContent = state.stats.total_sessions;
  document.getElementById('stat-course-count').textContent = state.courses.length;
  document.getElementById('header-streak-count').textContent = state.stats.weekly_streak;

  // Course breakdown progress bars
  const container = document.getElementById('course-progress-list');
  if (!state.stats.courses || state.stats.courses.length === 0) {
    container.innerHTML = `<div class="text-xs text-zinc-400 py-6 text-center">No study sessions logged for any courses yet.</div>`;
    return;
  }

  const maxMinutes = Math.max(...state.stats.courses.map(c => c.total_minutes), 1);
  container.innerHTML = state.stats.courses.map(c => {
    const pct = Math.min(100, Math.round((c.total_minutes / maxMinutes) * 100));
    const hours = (c.total_minutes / 60).toFixed(1);
    return `
      <div class="space-y-1.5">
        <div class="flex justify-between items-center text-xs">
          <span class="font-medium text-zinc-900">${escapeHtml(c.course_title)}</span>
          <span class="text-zinc-500 font-mono">${hours}h (${c.total_minutes}m) &middot; ${c.session_count} ses</span>
        </div>
        <div class="w-full bg-zinc-100 h-2 rounded-full overflow-hidden">
          <div class="bg-zinc-900 h-full rounded-full transition-all duration-300" style="width: ${pct}%"></div>
        </div>
      </div>
    `;
  }).join('');
}

function renderCourses() {
  const grid = document.getElementById('courses-grid');
  if (state.courses.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full p-8 text-center border border-dashed border-zinc-200 rounded-xl space-y-2">
        <p class="text-xs text-zinc-500 font-medium">No courses added yet.</p>
        <p class="text-[11px] text-zinc-400">Create your first subject or curriculum to start logging study sessions.</p>
      </div>
    `;
    return;
  }

  // Map courses to their stats
  const statsMap = {};
  if (state.stats && state.stats.courses) {
    state.stats.courses.forEach(c => { statsMap[c.course_id] = c; });
  }

  grid.innerHTML = state.courses.map(course => {
    const s = statsMap[course.id] || { total_minutes: 0, session_count: 0 };
    const hours = (s.total_minutes / 60).toFixed(1);
    return `
      <div class="card-subtle p-5 rounded-xl flex flex-col justify-between space-y-4">
        <div>
          <div class="flex items-start justify-between">
            <h3 class="text-sm font-semibold text-zinc-900">${escapeHtml(course.title)}</h3>
            <button onclick="handleDeleteCourse(${course.id})" class="text-zinc-400 hover:text-rose-600 transition-quiet" title="Delete Course">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
          <p class="text-xs text-zinc-500 mt-1 line-clamp-2">${escapeHtml(course.description || 'No description.')}</p>
        </div>
        <div class="pt-3 border-t border-zinc-100 flex items-center justify-between text-xs text-zinc-500">
          <span class="font-mono text-zinc-900 font-medium">${hours} hrs</span>
          <span>${s.session_count} sessions</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderSessions() {
  const tbody = document.getElementById('sessions-table-body');
  if (state.sessions.length === 0) {
    tbody.innerHTML = `
      <tr><td colspan="5" class="py-12 text-center text-xs text-zinc-400">No study sessions found matching your filters.</td></tr>
    `;
    return;
  }

  const courseMap = {};
  state.courses.forEach(c => { courseMap[c.id] = c.title; });

  tbody.innerHTML = state.sessions.map(s => {
    const courseTitle = courseMap[s.course_id] || `Course #${s.course_id}`;
    return `
      <tr class="hover:bg-zinc-50/70 transition-quiet">
        <td class="py-3 px-4 font-mono text-zinc-500">${s.session_date}</td>
        <td class="py-3 px-4 font-medium text-zinc-900">${escapeHtml(courseTitle)}</td>
        <td class="py-3 px-4 font-mono font-medium text-zinc-900">${s.minutes} min</td>
        <td class="py-3 px-4 text-zinc-500 max-w-xs truncate">${escapeHtml(s.notes || '—')}</td>
        <td class="py-3 px-4 text-right">
          <button onclick="handleDeleteSession(${s.id})" class="text-zinc-400 hover:text-rose-600 transition-quiet" title="Delete Session">
            <svg class="w-3.5 h-3.5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderRecentSessions() {
  const tbody = document.getElementById('recent-sessions-tbody');
  const recent = state.sessions.slice(0, 5);
  if (recent.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="py-6 text-center text-zinc-400">No recent sessions recorded.</td></tr>`;
    return;
  }

  const courseMap = {};
  state.courses.forEach(c => { courseMap[c.id] = c.title; });

  tbody.innerHTML = recent.map(s => {
    const courseTitle = courseMap[s.course_id] || `Course #${s.course_id}`;
    return `
      <tr>
        <td class="py-2.5 font-mono text-zinc-500">${s.session_date}</td>
        <td class="py-2.5 font-medium text-zinc-900">${escapeHtml(courseTitle)}</td>
        <td class="py-2.5 font-mono font-medium text-zinc-900">${s.minutes}m</td>
        <td class="py-2.5 text-zinc-500 truncate max-w-xs">${escapeHtml(s.notes || '—')}</td>
      </tr>
    `;
  }).join('');
}

function populateCourseDropdowns() {
  const selects = [
    document.getElementById('dash-timer-course-select'),
    document.getElementById('main-timer-course-select'),
    document.getElementById('session-course-select'),
    document.getElementById('filter-course-select'),
  ];

  selects.forEach(sel => {
    if (!sel) return;
    const isFilter = sel.id === 'filter-course-select';
    const currentVal = sel.value;
    sel.innerHTML = isFilter
      ? `<option value="">All Courses</option>`
      : `<option value="">Select course...</option>`;

    state.courses.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.title;
      sel.appendChild(opt);
    });

    sel.value = currentVal;
  });
}

// ==================== Actions: Courses ====================
async function handleCreateCourse(e) {
  e.preventDefault();
  const title = document.getElementById('course-title-input').value.trim();
  const description = document.getElementById('course-desc-input').value.trim() || null;
  if (!title) return;

  try {
    const newCourse = await apiRequest('/courses/', {
      method: 'POST',
      body: JSON.stringify({ title, description }),
    });
    showToast(`Course "${newCourse.title}" created`, 'success');
    document.getElementById('form-create-course').reset();
    document.getElementById('add-course-panel').classList.add('hidden');
    await refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleDeleteCourse(courseId) {
  if (!confirm('Are you sure you want to delete this course and all its study sessions?')) return;
  try {
    await apiRequest(`/courses/${courseId}`, { method: 'DELETE' });
    showToast('Course deleted', 'success');
    await refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==================== Actions: Sessions ====================
async function handleLogSession(e) {
  e.preventDefault();
  const courseId = parseInt(document.getElementById('session-course-select').value);
  const minutes = parseInt(document.getElementById('session-minutes-input').value);
  const sessionDate = document.getElementById('session-date-input').value;
  const notes = document.getElementById('session-notes-input').value.trim() || null;

  if (!courseId || !minutes || !sessionDate) {
    showToast('Please fill in course, minutes, and date', 'error');
    return;
  }

  try {
    await apiRequest('/sessions/', {
      method: 'POST',
      body: JSON.stringify({
        course_id: courseId,
        minutes,
        session_date: sessionDate,
        notes,
      }),
    });
    showToast(`Logged ${minutes} min session`, 'success');
    document.getElementById('form-log-session').reset();
    document.getElementById('session-date-input').value = new Date().toISOString().split('T')[0];
    document.getElementById('log-session-panel').classList.add('hidden');
    await refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleDeleteSession(sessionId) {
  if (!confirm('Delete this study session?')) return;
  try {
    await apiRequest(`/sessions/${sessionId}`, { method: 'DELETE' });
    showToast('Session record deleted', 'success');
    await refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==================== Study Timer Logic ====================
function formatTime(totalSeconds) {
  const hrs = Math.floor(totalSeconds / 3600);
  const mins = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;
  return [hrs, mins, secs].map(v => String(v).padStart(2, '0')).join(':');
}

function updateTimerDisplays() {
  const formatted = formatTime(state.timer.seconds);
  const dashDisplay = document.getElementById('dash-timer-display');
  const mainClock = document.getElementById('main-timer-clock');
  const dashSaveBtn = document.getElementById('dash-timer-save-btn');
  const mainSaveBtn = document.getElementById('btn-timer-save');
  const statusIndicator = document.getElementById('quick-timer-status');
  const timerBadge = document.getElementById('main-timer-badge');

  if (dashDisplay) dashDisplay.textContent = formatted;
  if (mainClock) mainClock.textContent = formatted;

  const canSave = state.timer.seconds >= 60;
  if (dashSaveBtn) {
    dashSaveBtn.disabled = !canSave;
    dashSaveBtn.className = canSave
      ? 'py-2 text-xs font-medium rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 transition-quiet'
      : 'py-2 text-xs font-medium rounded-lg bg-zinc-100 text-zinc-400 border border-zinc-200 cursor-not-allowed transition-quiet';
  }
  if (mainSaveBtn) {
    mainSaveBtn.disabled = !canSave;
    mainSaveBtn.className = canSave
      ? 'px-5 py-3 text-sm font-medium rounded-xl bg-zinc-900 text-white hover:bg-zinc-800 transition-quiet shadow-sm'
      : 'px-5 py-3 text-sm font-medium rounded-xl bg-zinc-100 text-zinc-400 border border-zinc-200 cursor-not-allowed transition-quiet';
  }

  if (state.timer.running) {
    if (statusIndicator) statusIndicator.className = 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse';
    if (timerBadge) {
      timerBadge.textContent = 'FOCUSING';
      timerBadge.className = 'inline-block mt-3 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium text-emerald-800 bg-emerald-100';
    }
  } else {
    if (statusIndicator) statusIndicator.className = 'w-2 h-2 rounded-full bg-zinc-300';
    if (timerBadge) {
      timerBadge.textContent = state.timer.seconds > 0 ? 'PAUSED' : 'READY';
      timerBadge.className = 'inline-block mt-3 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium text-zinc-500 bg-zinc-100';
    }
  }
}

function toggleTimer() {
  if (state.timer.running) {
    // Pause
    clearInterval(state.timer.intervalId);
    state.timer.running = false;
    document.getElementById('dash-timer-toggle-btn').textContent = 'Resume';
    document.getElementById('btn-timer-toggle').textContent = 'Resume';
  } else {
    // Start
    state.timer.running = true;
    state.timer.intervalId = setInterval(() => {
      state.timer.seconds += 1;
      updateTimerDisplays();
    }, 1000);
    document.getElementById('dash-timer-toggle-btn').textContent = 'Pause';
    document.getElementById('btn-timer-toggle').textContent = 'Pause';
  }
  updateTimerDisplays();
}

function resetTimer() {
  clearInterval(state.timer.intervalId);
  state.timer.running = false;
  state.timer.seconds = 0;
  document.getElementById('dash-timer-toggle-btn').textContent = 'Start';
  document.getElementById('btn-timer-toggle').textContent = 'Start';
  updateTimerDisplays();
}

async function saveTimerSession() {
  const minutes = Math.max(1, Math.round(state.timer.seconds / 60));
  const courseId = parseInt(
    document.getElementById('main-timer-course-select').value ||
    document.getElementById('dash-timer-course-select').value
  );

  if (!courseId) {
    showToast('Please select a course for this session', 'error');
    return;
  }

  try {
    await apiRequest('/sessions/', {
      method: 'POST',
      body: JSON.stringify({
        course_id: courseId,
        minutes,
        session_date: new Date().toISOString().split('T')[0],
        notes: `Focus timer study session (${minutes} minutes)`,
      }),
    });
    showToast(`Saved ${minutes} min focus session`, 'success');
    resetTimer();
    await refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==================== Tab Switching ====================
function switchTab(tabName) {
  state.activeTab = tabName;
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  const activeEl = document.getElementById(`tab-${tabName}`);
  if (activeEl) activeEl.classList.remove('hidden');

  // Update nav buttons
  document.querySelectorAll('.nav-tab').forEach(btn => {
    if (btn.dataset.tab === tabName) {
      btn.className = 'nav-tab px-3 py-1.5 text-sm font-medium rounded-md transition-quiet bg-zinc-100 text-zinc-900';
    } else {
      btn.className = 'nav-tab px-3 py-1.5 text-sm font-medium rounded-md transition-quiet text-zinc-600 hover:text-zinc-900 hover:bg-zinc-50';
    }
  });
}

// ==================== Modal & Event Listeners ====================
function setupEventListeners() {
  // Navigation tabs
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Auth modal toggle
  const authModal = document.getElementById('auth-modal');
  const btnOpenAuth = document.getElementById('btn-open-auth');
  const btnCloseAuth = document.getElementById('btn-close-auth');
  const bannerLoginBtn = document.getElementById('banner-login-btn');

  const openAuth = () => authModal.classList.remove('hidden');
  const closeAuth = () => authModal.classList.add('hidden');

  if (btnOpenAuth) btnOpenAuth.addEventListener('click', openAuth);
  if (bannerLoginBtn) bannerLoginBtn.addEventListener('click', openAuth);
  if (btnCloseAuth) btnCloseAuth.addEventListener('click', closeAuth);

  // Tab Auth (Login vs Register)
  const tabLogin = document.getElementById('tab-auth-login');
  const tabRegister = document.getElementById('tab-auth-register');
  const formLogin = document.getElementById('form-login');
  const formRegister = document.getElementById('form-register');
  const authErrorBox = document.getElementById('auth-error-box');

  tabLogin.addEventListener('click', () => {
    tabLogin.className = 'pb-2 text-sm font-semibold border-b-2 border-zinc-900 text-zinc-900';
    tabRegister.className = 'pb-2 text-sm font-semibold border-b-2 border-transparent text-zinc-400 hover:text-zinc-600';
    formLogin.classList.remove('hidden');
    formRegister.classList.add('hidden');
    authErrorBox.classList.add('hidden');
  });

  tabRegister.addEventListener('click', () => {
    tabRegister.className = 'pb-2 text-sm font-semibold border-b-2 border-zinc-900 text-zinc-900';
    tabLogin.className = 'pb-2 text-sm font-semibold border-b-2 border-transparent text-zinc-400 hover:text-zinc-600';
    formRegister.classList.remove('hidden');
    formLogin.classList.add('hidden');
    authErrorBox.classList.add('hidden');
  });

  // Login form submit
  formLogin.addEventListener('submit', async (e) => {
    e.preventDefault();
    const u = document.getElementById('login-username').value.trim();
    const p = document.getElementById('login-password').value;
    authErrorBox.classList.add('hidden');

    try {
      const formData = new URLSearchParams();
      formData.append('username', u);
      formData.append('password', p);

      const res = await apiRequest('/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      state.token = res.access_token;
      localStorage.setItem('study_tracker_token', res.access_token);
      showToast('Signed in successfully', 'success');
      closeAuth();
      formLogin.reset();
      await checkAuth();
    } catch (err) {
      authErrorBox.textContent = err.message;
      authErrorBox.classList.remove('hidden');
    }
  });

  // Register form submit
  formRegister.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    authErrorBox.classList.add('hidden');

    try {
      await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
      });

      // Auto login
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await apiRequest('/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      state.token = res.access_token;
      localStorage.setItem('study_tracker_token', res.access_token);
      showToast('Account created and signed in', 'success');
      closeAuth();
      formRegister.reset();
      await checkAuth();
    } catch (err) {
      authErrorBox.textContent = err.message;
      authErrorBox.classList.remove('hidden');
    }
  });

  // Logout button
  document.getElementById('btn-logout').addEventListener('click', () => {
    state.token = null;
    state.user = null;
    localStorage.removeItem('study_tracker_token');
    updateAuthUI();
    loadPublicDemo();
    showToast('Signed out', 'info');
  });

  // Course form events
  document.getElementById('btn-show-add-course').addEventListener('click', () => {
    document.getElementById('add-course-panel').classList.toggle('hidden');
  });
  document.getElementById('btn-cancel-course').addEventListener('click', () => {
    document.getElementById('add-course-panel').classList.add('hidden');
  });
  document.getElementById('form-create-course').addEventListener('submit', handleCreateCourse);

  // Session form events
  document.getElementById('btn-toggle-log-session').addEventListener('click', () => {
    document.getElementById('log-session-panel').classList.toggle('hidden');
  });
  document.getElementById('btn-cancel-session').addEventListener('click', () => {
    document.getElementById('log-session-panel').classList.add('hidden');
  });
  document.getElementById('form-log-session').addEventListener('submit', handleLogSession);

  // Default session date input to today
  document.getElementById('session-date-input').value = new Date().toISOString().split('T')[0];

  // Dashboard quick triggers
  document.getElementById('dash-quick-log').addEventListener('click', () => {
    switchTab('sessions');
    document.getElementById('log-session-panel').classList.remove('hidden');
  });
  document.getElementById('dash-start-timer').addEventListener('click', () => {
    switchTab('timer');
  });
  document.getElementById('dash-view-courses-btn').addEventListener('click', () => switchTab('courses'));
  document.getElementById('dash-view-all-sessions-btn').addEventListener('click', () => switchTab('sessions'));

  // Session filters
  document.getElementById('filter-course-select').addEventListener('change', (e) => {
    state.filters.courseId = e.target.value;
    fetchSessions();
  });
  document.getElementById('filter-start-date').addEventListener('change', (e) => {
    state.filters.startDate = e.target.value;
    fetchSessions();
  });
  document.getElementById('filter-end-date').addEventListener('change', (e) => {
    state.filters.endDate = e.target.value;
    fetchSessions();
  });
  document.getElementById('btn-clear-filters').addEventListener('click', () => {
    document.getElementById('filter-course-select').value = '';
    document.getElementById('filter-start-date').value = '';
    document.getElementById('filter-end-date').value = '';
    state.filters = { courseId: '', startDate: '', endDate: '' };
    fetchSessions();
  });

  // Timer buttons
  document.getElementById('dash-timer-toggle-btn').addEventListener('click', toggleTimer);
  document.getElementById('dash-timer-save-btn').addEventListener('click', saveTimerSession);
  document.getElementById('btn-timer-toggle').addEventListener('click', toggleTimer);
  document.getElementById('btn-timer-reset').addEventListener('click', resetTimer);
  document.getElementById('btn-timer-save').addEventListener('click', saveTimerSession);

  // Timer presets
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const addedMins = parseInt(btn.dataset.addMin);
      state.timer.seconds += addedMins * 60;
      updateTimerDisplays();
    });
  });

  // Sync timer course selects
  document.getElementById('dash-timer-course-select').addEventListener('change', (e) => {
    document.getElementById('main-timer-course-select').value = e.target.value;
  });
  document.getElementById('main-timer-course-select').addEventListener('change', (e) => {
    document.getElementById('dash-timer-course-select').value = e.target.value;
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Window global functions for inline onclicks
window.handleDeleteCourse = handleDeleteCourse;
window.handleDeleteSession = handleDeleteSession;

// App Initialization
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  checkAuth();
});
