
// =========================================================================================================================
//                                              HEATMAP CALENDAR CONSTRUCTION
// =========================================================================================================================
const heatmapContainer = document.getElementById('heatmap')
const heatmapMonthsContainer = document.getElementById('heatmap_months')

const MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const DAY_MS = 1000 * 60 * 60 * 24


// toISOString() converts to UTC before formatting, which shifts the date
// by a day near midnight in timezones ahead of UTC (e.g. Jan 1st becomes Dec 31st).
// This formats the date using local values instead, avoiding that shift.
function formatLocalDate(date) {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
}

function initHeatmap(year) {
    heatmapContainer.innerHTML = ''
    heatmapMonthsContainer.innerHTML = ''

    const startOfYear = new Date(year, 0, 1)
    const startDay = startOfYear.getDay() // Sunday = 0, already in the right order
    const daysInYear = (new Date(year + 1, 0, 1) - startOfYear) / DAY_MS

    // empty cells so Jan 1st lands on its correct row (day of the week)
    for (let i = 0; i < startDay; i++) {
        const filler = document.createElement('div')
        filler.className = 'heatmap-cell empty'
        heatmapContainer.appendChild(filler)
    }

    for (let i = 0; i < daysInYear; i++) {
        const date = new Date(year, 0, i + 1)
        const dateStr = formatLocalDate(date)

        const cell = document.createElement('div')
        cell.className = 'heatmap-cell'
        cell.dataset.date = dateStr
        heatmapContainer.appendChild(cell)
    }

    renderHeatmapMonths(year, startDay);
}

function renderHeatmapMonths(year, startDay) {
    for (let month = 0; month < 12; month++) {
        const firstOfMonth = new Date(year, month, 1)
        const dayOfYear = Math.round((firstOfMonth - new Date(year, 0, 1)) / DAY_MS)
        const columnIndex = Math.floor((startDay + dayOfYear) / 7)

        const label = document.createElement('span')
        label.className = 'heatmap_month_label'
        label.textContent = MONTH_NAMES[month]
        label.style.gridColumnStart = columnIndex + 1
        heatmapMonthsContainer.appendChild(label)
    }
}

const INTENSITY_COLORS = {
    'very_low':  '#371b1b',
    'low':       '#592222',
    'moderate':  '#862727',
    'high':      '#bd2828',
    'very_high': '#e33b3b',
}

const SATISFACTION_COLORS = {
    'terrible': '#1b2337',
    'bad':      '#222d59',
    'neutral':  '#273a86',
    'good':     '#2850bd',
    'great':    '#3b6fe3',
}

function loadHeatMapCalendar(workouts) {
    workouts.forEach(workout => {
        const cell = heatmapContainer.querySelector(`[data-date="${workout.date}"]`)
        if (!cell) return

        cell.classList.add('has-workout')
        cell.dataset.intensity = workout.intensity
        cell.dataset.satisfaction = workout.satisfaction
    })

    document.getElementById('total_workouts_heatmap_sumary').textContent = workouts.length
    renderHeatmapColors()
}

function renderHeatmapColors() {
    const colors = heatmapMode === 'intensity' ? INTENSITY_COLORS : SATISFACTION_COLORS

    heatmapContainer.querySelectorAll('.heatmap-cell.has-workout').forEach(cell => {
        const value = cell.dataset[heatmapMode]
        cell.style.background = colors[value] ?? colors['moderate'] ?? colors['neutral']
    })
}

const intensityRadio = document.querySelector('input[value="intensity"]')
const satisfactionRadio = document.querySelector('input[value="satisfaction"]')
let heatmapMode = intensityRadio.checked ? 'intensity' : 'satisfaction'
const heatmapColors = document.querySelectorAll('.heatmap_legend_color')

intensityRadio.addEventListener('change', () => {
    heatmapMode = 'intensity'
    heatmapColors.forEach(day => {
        day.classList.remove('satisfaction_colors')
        day.classList.add('intensity_colors')
    })
    renderHeatmapColors()
})

satisfactionRadio.addEventListener('change', () => {
    heatmapMode = 'satisfaction'
    heatmapColors.forEach(day => {
        day.classList.remove('intensity_colors')
        day.classList.add('satisfaction_colors')
    })
    renderHeatmapColors()
})

// --------------- HEATMAP YEARS LOGIC
const heatmapYearSpan = document.getElementById('heatmap_year')
const heatmapPrevYear = document.getElementById('heatmap_prev_year')
const heatmapNextYear = document.getElementById('heatmap_next_year')
let currentYear = new Date().getFullYear();
// sendToBackend("get_heatmap_data", { year: String(currentYear) });

initHeatmap(currentYear)
heatmapYearSpan.textContent = Number(currentYear);

heatmapPrevYear.addEventListener('click', () => {
    if (currentYear > 2025) {
        currentYear -= 1;
        initHeatmap(currentYear)
        sendToBackend("get_heatmap_data", { year: String(currentYear) });
        heatmapYearSpan.textContent = currentYear;
    }
})

heatmapNextYear.addEventListener('click', () => {
    if (currentYear < 2026) {
        currentYear += 1;
        initHeatmap(currentYear)
        sendToBackend("get_heatmap_data", { year: String(currentYear) });
        heatmapYearSpan.textContent = currentYear;
    }
})


// ============================================================================================
//                             HEATMAP TOOLTIP (fuera del contenedor con scroll)
// ============================================================================================
const heatmapTooltip = document.getElementById('heatmap_tooltip')

heatmapContainer.addEventListener('mouseover', (e) => {
    const cell = e.target.closest('.heatmap-cell')
    if (!cell || !cell.classList.contains('has-workout')) return

    heatmapTooltip.textContent = cell.dataset.date
    heatmapTooltip.classList.add('visible')
})

heatmapContainer.addEventListener('mousemove', (e) => {
    if (!heatmapTooltip.classList.contains('visible')) return
    heatmapTooltip.style.left = `${e.clientX}px`
    heatmapTooltip.style.top = `${e.clientY - 10}px`
})

heatmapContainer.addEventListener('mouseout', (e) => {
    const cell = e.target.closest('.heatmap-cell')
    if (cell) heatmapTooltip.classList.remove('visible')
})



// =========================================================================================================================
//                                              GENERAL PROGROGRESS CHART
// =========================================================================================================================
const generalProgressChartsButtons = document.querySelectorAll('.general_progress_chart_selector_btn')
const generalProgressCanvas = document.querySelectorAll('.general_progress_canvas')
let currentGeneralProgressChartIndex = 0;

generalProgressChartsButtons.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        if (index === currentGeneralProgressChartIndex) return;

        generalProgressCanvas.forEach(canvas => { canvas.style.transform = `translateX(-${index * 100}%)`; });
        generalProgressChartsButtons.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected')

        currentGeneralProgressChartIndex = index;
    })
})


new Chart(document.getElementById('general_progress_chart'), {
  type: 'bar',
  data: {
    labels: ['1','2','3','4','5','6','7','8','9','10','11','12',
            '13','14','15','16','17','18','19','20','21','22','23','24'],            
    datasets: [{
        label: 'Progreso',
        data: [12, 19, 3, 5, 2, 3, 10, 8, 15, 6, 9, 4, 11, 18, 7, 4, 6, 8, 13, 16, 10, 5, 12, 7]
    }]
  },
  options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    display: false,
                    position: 'bottom',
                    labels: {
                        color: '#7a7a7a',
                        font: { size: 10 },
                        boxWidth: 8,
                        boxHeight: 8,
                        usePointStyle: true,
                    }
                },
                tooltip: {
                    backgroundColor: '#181818',
                    titleColor: '#bbbbbb',
                    bodyColor: '#bbbbbb',
                    borderColor: '#292929',
                    borderWidth: 1,
                    padding: 8,
                    boxPadding: 4,
                }
            },
            scales: {
                x: {
                    grid: { display: false, drawOnChartArea: false, drawBorder: false },
                    ticks: { color: '#5a5a5a', font: { size: 9 }, display: false }
                },
                y: {
                    stacked: true,
                    grid: { display: false, color: 'rgba(255,255,255,0.04)', drawBorder: false },
                    ticks: { color: '#5a5a5a', font: { size: 9 }, display: false }
                }
            }
        }
});