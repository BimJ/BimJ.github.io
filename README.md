# BimJ.github.io
For test and learning
<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <title>Kjell & Co Schema</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    h1 { text-align: center; }
    table {
      border-collapse: collapse;
      width: 100%;
      margin-top: 20px;
      table-layout: fixed;
    }
    th, td {
      border: 1px solid #ccc;
      text-align: center;
      padding: 5px;
      vertical-align: middle;
    }
    th {
      background-color: #1e88e5;
      color: white;
      height: 120px;
    }
    td:first-child {
      width: 80px;
      font-weight: bold;
    }
    .chatt { background-color: #fdd835; color: black; }
    .telefon { background-color: #43a047; color: white; }
    .admin, .meta { background-color: #1e88e5; color: white; }
    .lunch { background-color: #ffe0b2; color: black; }
    .semester { background-color: #ff9800; color: black; }
    .möte { background-color: #f44336; color: white }
    .sick { background-color: #ef9a9a; color: black; }
    select, input[type="text"] {
      width: 100%;
      padding: 5px;
      font-size: 14px;
      box-sizing: border-box;
      margin-bottom: 4px;
    }
    .name-label {
      font-weight: bold;
      display: block;
      margin-top: 4px;
    }
  </style>
</head>
<body>
  <h1>Kjell & Co Schema</h1>
  <table id="schedule">
    <thead>
      <tr>
        <script>
          const names = ["Bim", "Rasmus", "Oliver", "Dennis", "Hampus", "Emil", "Kungens Kurva", "Jennifer", "Huy", "Melanie"];
          document.write('<th>Tid</th>');
          names.forEach((_, index) => {
            document.write(`
              <th>
                <input type="text" placeholder="Kommentar..." />
                <select onchange="updateNameLabel(this)">
                  <option value="">Välj namn</option>
                  ${names.map(n => `<option value="${n}">${n}</option>`).join('')}
                </select>
                <span class="name-label">Ingen vald</span>
                <select onchange="fillColumn(this, ${index + 1})">
                  <option value=""> </option>
                  <option value="Semester">🌻 Semester</option>
                  <option value="Sjuk">🤒 Sjuk</option>
                </select>
              </th>
            `);
          });
        </script>
      </tr>
    </thead>
    <tbody>
      <!-- Rader genereras med JavaScript -->
    </tbody>
  </table>

  <script>
    const tasks = [
      { label: "", icon: "" },
      { label: "Chatt", icon: "💬" },
      { label: "Telefon", icon: "📞" },
      { label: "Admin", icon: "🗂️" },
      { label: "Lunch", icon: "🍽️" },
      { label: "Meta & Trust", icon: "🛡️" },
      { label: "Möte", icon: "🗓️" },
      { label: "Semester", icon: "🌻" },
      { label: "Sjuk", icon: "🤒" }
    ];
    const colors = {
      "Chatt": "chatt",
      "Telefon": "telefon",
      "Admin": "admin",
      "Lunch": "lunch",
      "Meta & Trust": "meta",
      "Semester": "semester",
      "Möte": "möte",
      "Sjuk": "sjuk"
    };

    const tableBody = document.querySelector("#schedule tbody");

    for (let hour = 8; hour < 18; hour++) {
      const row = document.createElement("tr");
      const timeCell = document.createElement("td");
      timeCell.textContent = `${hour.toString().padStart(2, '0')}-${(hour + 1).toString().padStart(2, '0')}`;
      row.appendChild(timeCell);

      for (let i = 0; i < 10; i++) {
        const cell = document.createElement("td");
        const select = document.createElement("select");

        tasks.forEach(task => {
          const option = document.createElement("option");
          option.value = task.label;
          option.textContent = task.icon + " " + task.label;
          select.appendChild(option);
        });

        select.addEventListener("change", () => {
          select.className = colors[select.value] || "";
        });

        cell.appendChild(select);
        row.appendChild(cell);
      }

      tableBody.appendChild(row);
    }

    function fillColumn(dropdown, colIndex) {
      const value = dropdown.value;
      const selects = tableBody.querySelectorAll(`tr td:nth-child(${colIndex + 1}) select`);
      selects.forEach(select => {
        select.value = value;
        select.className = colors[value] || "";
      });
    }

    function updateNameLabel(select) {
      const label = select.parentElement.querySelector(".name-label");
      label.textContent = select.value || "Ingen vald";
    }
  </script>
</body>
</html>
