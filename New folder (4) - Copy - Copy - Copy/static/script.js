const apiBase = '';

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function setStatus(el, text, cls) {
    el.textContent = text || '';
    el.className = `status ${cls || ''}`;
}

function toast(message, type = 'ok') {
    const host = document.querySelector('#toasts');
    if (!host) return;
    const div = document.createElement('div');
    div.className = `px-4 py-3 rounded shadow text-sm ${type === 'ok' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`;
    div.textContent = message;
    host.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}

async function fetchJSON(url, options) {
    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        const err = new Error(data.error || 'Request failed');
        err.details = data.details;
        err.status = res.status;
        throw err;
    }
    return data;
}

async function loadEmployees() {
    const status = $('#list-status');
    setStatus(status, 'Loading...');
    try {
        const data = await fetchJSON(`${apiBase}/employees`);
        const tbody = $('#employees-table tbody');
        tbody.innerHTML = '';
        const q = (document.querySelector('#search')?.value || '').toLowerCase();
        const filtered = (data.data || []).filter(emp => {
            const hay = [emp.name, emp.email, emp.department, emp.department_id].join(' ').toLowerCase();
            return hay.includes(q);
        });

        // Stats
        const total = filtered.length;
        const avg = total ? (filtered.reduce((s, e) => s + (Number(e.salary) || 0), 0) / total) : 0;
        const fmt = (n) => n.toLocaleString(undefined, { maximumFractionDigits: 2 });
        const setText = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        setText('total-count', fmt(total));
        setText('avg-salary', total ? `$${fmt(avg)}` : '—');
        setText('last-refresh', new Date().toLocaleTimeString());

        filtered.forEach(emp => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
        <td>${emp.id}</td>
        <td>${emp.name}</td>
        <td>${emp.email}</td>
        <td>${emp.department ?? ''} ${emp.department_id ? `(id ${emp.department_id})` : ''}</td>
        <td>
          <input type="number" class="inline-salary" value="${emp.salary?.toFixed ? emp.salary.toFixed(2) : emp.salary}" step="0.01" style="width:110px" />
        </td>
        <td class="actions">
          <button data-save="${emp.id}">Save</button>
          <button data-del="${emp.id}">Delete</button>
        </td>
      `;
            tbody.appendChild(tr);
        });

        // Wire delete buttons
        $$('#employees-table [data-del]').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-del');
                if (!confirm(`Delete employee #${id}?`)) return;
                try {
                    await fetchJSON(`${apiBase}/employees/${id}`, { method: 'DELETE' });
                    await loadEmployees();
                    toast('Deleted');
                } catch (e) {
                    toast(e.message, 'err');
                }
            });
        });

        // Wire save buttons (inline salary update)
        $$('#employees-table [data-save]').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-save');
                const tr = btn.closest('tr');
                const salaryInput = tr.querySelector('.inline-salary');
                const newSalary = Number(salaryInput.value);
                if (!(newSalary > 0)) { toast('Enter valid salary', 'err'); return; }
                try {
                    await fetchJSON(`${apiBase}/employees/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ salary: newSalary })
                    });
                    toast('Saved');
                    await loadEmployees();
                } catch (e) {
                    toast(e.message, 'err');
                }
            });
        });

        setStatus(status, `Loaded ${data.count} employees`, 'ok');
    } catch (e) {
        setStatus(status, e.message, 'err');
    }
}

function wireCreateForm() {
    const form = $('#create-form');
    const status = $('#create-status');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        setStatus(status, 'Creating...');
        const payload = {
            name: $('#name').value.trim(),
            salary: Number($('#salary').value)
        };
        // Send whichever your DB supports
        const dep = $('#department').value.trim();
        if (dep) payload.department = dep; // if column exists
        const maybeId = Number(dep);
        if (!isNaN(maybeId) && maybeId > 0) payload.department_id = maybeId; // allow numeric dep as id
        const email = $('#email').value.trim();
        if (email) payload.email = email.toLowerCase();
        try {
            await fetchJSON(`${apiBase}/employees`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            setStatus(status, 'Employee created', 'ok');
            toast('Employee created');
            form.reset();
            await loadEmployees();
        } catch (e) {
            setStatus(status, e.message + (e.details ? `: ${e.details.join(', ')}` : ''), 'err');
            toast(e.message, 'err');
        }
    });
}

function wireUpdateForm() {
    const form = $('#update-form');
    const status = $('#update-status');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        setStatus(status, 'Updating...');
        const id = Number($('#u-id').value);
        const payload = {};
        const dep = $('#u-department').value.trim();
        const sal = $('#u-salary').value;
        if (dep) payload.department = dep;
        if (sal) payload.salary = Number(sal);
        if (!Object.keys(payload).length) {
            setStatus(status, 'Provide salary and/or department', 'err');
            return;
        }
        try {
            await fetchJSON(`${apiBase}/employees/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            setStatus(status, 'Employee updated', 'ok');
            toast('Employee updated');
            await loadEmployees();
        } catch (e) {
            setStatus(status, e.message + (e.details ? `: ${e.details.join(', ')}` : ''), 'err');
            toast(e.message, 'err');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    $('#refresh-btn').addEventListener('click', loadEmployees);
    const s = document.querySelector('#search');
    if (s) s.addEventListener('input', () => loadEmployees());
    wireCreateForm();
    wireUpdateForm();
    loadEmployees();

    // Modal logic
    const modal = document.getElementById('modal');
    const openBtn = document.getElementById('new-btn');
    const closeBtn = document.getElementById('modal-close');
    const cancelBtn = document.getElementById('modal-cancel');
    const form = document.getElementById('modal-form');
    function openModal() { modal.classList.remove('hidden'); modal.classList.add('flex'); form.reset(); document.getElementById('m-id').value = ''; }
    function closeModal() { modal.classList.add('hidden'); modal.classList.remove('flex'); }
    if (openBtn) openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    if (modal) modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
    if (form) form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            name: document.getElementById('m-name').value.trim(),
            salary: Number(document.getElementById('m-salary').value)
        };
        const dep = document.getElementById('m-department').value.trim();
        if (dep) payload.department = dep;
        const maybeId = Number(dep);
        if (!isNaN(maybeId) && maybeId > 0) payload.department_id = maybeId;
        const email = document.getElementById('m-email').value.trim();
        if (email) payload.email = email.toLowerCase();
        try {
            await fetchJSON(`${apiBase}/employees`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            toast('Employee created');
            closeModal();
            await loadEmployees();
        } catch (e) {
            toast(e.message, 'err');
        }
    });
});


