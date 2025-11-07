// Use a relative path so same-origin cookies are sent automatically. Change to an absolute
// URL if your frontend is hosted separately — then ensure fetch uses credentials:'include'.
const API_URL = "/employees";

// Fetch all employees
async function fetchEmployees() {
  const res = await fetch(API_URL);
  const data = await res.json();

  const tableBody = document.getElementById("employeeTableBody");
  tableBody.innerHTML = "";


  
  data.data.forEach(emp => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="py-2 px-4 border">${emp.id}</td>
      <td class="py-2 px-4 border">${emp.name}</td>
      <td class="py-2 px-4 border">${emp.email}</td>
      <td class="py-2 px-4 border">${emp.department}</td>
      <td class="py-2 px-4 border">$${emp.salary}</td>
      <td class="py-2 px-4 border text-center">
        <button onclick="deleteEmployee(${emp.id})" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">Delete</button>
      </td>
    `;
    tableBody.appendChild(row);
  });
}

// Add employee
document.getElementById("employeeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const department = document.getElementById("department").value.trim();
  const salary = document.getElementById("salary").value.trim();

  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, department, salary }),
  });

  const data = await res.json();
  if (data.success) {
    alert("✅ Employee added successfully!");
    e.target.reset();
    fetchEmployees();
  } else {
    alert("❌ Error: " + data.error);
  }
});

// Delete employee
async function deleteEmployee(id) {
  if (!confirm("Are you sure you want to delete this employee?")) return;
  const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
  const data = await res.json();
  if (data.success) {
    alert("🗑️ Employee deleted successfully");
    fetchEmployees();
  } else {
    alert("❌ Failed to delete employee");
  }
}

// Initial load
fetchEmployees();
