let workouts = [];
let volumeChart;

// Fetch and render the table data
async function fetchWorkoutData() {
  try {
    const response = await fetch('/api/get_curr_page');
    if (!response.ok) throw new Error('Failed to fetch table data');
    workouts = await response.json();
    renderTable();
  } catch (error) {
    console.error('Error fetching workout data:', error);
  }
}

// Render the table with toggleable rows
function renderTable() {
  const tbody = document.querySelector('#workout-table tbody');
  tbody.innerHTML = ''; // Clear existing rows

  workouts.forEach(({ date, workout }, index) => {
    // Main date row with a toggle icon
    const dateRow = `
      <tr>
        <td>
          <span class="expand-icon" data-index="${index}" role="button">▶</span> ${date}
        </td>
        <td></td>
      </tr>
    `;
    tbody.insertAdjacentHTML('beforeend', dateRow);

    // Add detail rows for each workout, hidden by default
    workout.forEach(({ movement, sets }) => {
      const detailRow = `
        <tr class="details-row hidden" data-index="${index}">
          <td colspan="2">
            <div class="p-3">
              <strong class="text-purple">${movement}</strong>
              <table class="table table-sm mt-2">
                <thead>
                  <tr>
                    <th>Set</th>
                    <th>Reps</th>
                    <th>Weight (lbs)</th>
                    <th>Failure</th>
                  </tr>
                </thead>
                <tbody>
                  ${sets.map(set => `
                    <tr>
                      <td>${set.set}</td>
                      <td>${set.reps}</td>
                      <td>${set.weight}</td>
                      <td>${set.failure ? '<span class="text-danger">Yes</span>' : '<span class="text-success">No</span>'}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </td>
        </tr>
      `;
      tbody.insertAdjacentHTML('beforeend', detailRow);
    });
  });

  // Attach event listener for toggle functionality
  document.querySelector('#workout-table tbody').addEventListener('click', function (event) {
    if (event.target.classList.contains('expand-icon')) {
      const index = event.target.dataset.index;
      const detailsRows = document.querySelectorAll(`.details-row[data-index="${index}"]`);
      const isHidden = detailsRows[0].classList.contains('hidden');

      // Update icon direction
      event.target.textContent = isHidden ? '▼' : '▶';

      // Show or hide relevant rows
      detailsRows.forEach(row => row.classList.toggle('hidden'));
    }
  });
}

// Fetch and render the dropdown options
async function fetchMovements() {
  try {
    const response = await fetch('/api/get_all_movements');
    if (!response.ok) throw new Error('Failed to fetch movements');
    const movements = await response.json();

    // Populate the select dropdown
    const movementSelect = document.querySelector('#movement-select');
    movements.forEach(movement => {
      const option = document.createElement('option');
      option.value = movement;
      option.textContent = movement;
      movementSelect.appendChild(option);
    });

    // Add event listener for dropdown change
    movementSelect.addEventListener('change', () => {
      const selectedMovement = movementSelect.value;
      fetchVolumeData(selectedMovement);
    });
  } catch (error) {
    console.error('Error fetching movements:', error);
  }
}

// Fetch and render the chart data
async function fetchVolumeData(movement) {
  try {
    const response = await fetch(`/api/get_volume?movement=${encodeURIComponent(movement)}`);
    if (!response.ok) throw new Error('Failed to fetch volume data');
    const volumeData = await response.json();

    // Prepare data for Chart.js
    const labels = Object.keys(volumeData);
    const data = Object.values(volumeData);

    // Update the chart
    updateChart(labels, data);
  } catch (error) {
    console.error('Error fetching volume data:', error);
  }
}

// Initialize Chart.js
function initializeChart() {
  const ctx = document.querySelector('#volume-chart').getContext('2d');
  volumeChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [], // Dates
      datasets: [
        {
          label: 'Volume',
          data: [], // Volume values
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderWidth: 2,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: {
            color: 'white',
          },
        },
      },
      scales: {
        x: {
          ticks: { color: 'white' },
        },
        y: {
          ticks: { color: 'white' },
        },
      },
    },
  });
}

// Update the Chart.js chart
function updateChart(labels, data) {
  volumeChart.data.labels = labels;
  volumeChart.data.datasets[0].data = data;
  volumeChart.update();
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  fetchWorkoutData(); // Ensure table is populated
  fetchMovements(); // Initialize dropdown options
  initializeChart(); // Set up the chart
});
