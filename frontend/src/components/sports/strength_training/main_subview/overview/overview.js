
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

        // # Example of returned dicc:
        // # {
        // #     "date": date(2026, 9, 23), "satisfaction": "good", "intensity": "high",
        // #     "exercises": [
        // #         {
        // #             "name": "bench press", "bodyweighted": False,
        // #             "sets": [
        // #                 {"set_number": 1, "weight": 45.0, "reps": 12, "reached_failure": False},
        // #                 {"set_number": 2, "weight": 40.0, "reps": 8, "reached_failure": True},
        // #             ]
        // #         },
        // #         {
        // #             "name": "pushups", "bodyweighted": True,
        // #             "sets": [{"set_number": 1, "weight": 18.0, "reps": 15, "reached_failure": False}]
        // #         }
        // #     ]
        // # }
function loadWorkoutDataView(workout_data) {
    const workoutData = loadWorkoutDataByDate(cell.dataset.date)
    const workoutDate = document.getElementById('workout_data_date');
    const workoutSatifaction = document.getElementById('workout_data_view_satisfaction');
    workoutDate.textContent = cell.dataset.date;
    workoutSatifaction.textContent = cell.dataset.satisfaction;
    console.log(cell.dataset)
}

function loadWorkoutDataByDate(date) {
}

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


// ============================================================================================
//                               GENERAL PROGRESS CHARTS (CHART.JS)
// ============================================================================================

const categoryCharts = {};
const categoryCanvasMap = {
    'push': 'push_general_progress_chart',
    'pull': 'pull_general_progress_chart',
    'legs': 'legs_general_progress_chart',
    'core': 'core_general_progress_chart'
};

const CATEGORY_COLORS = {
    push: { main: '#e05555', bar_pos: 'rgba(224, 85, 85, 0.5)', bar_neg: 'rgba(85, 140, 224, 0.5)', line: '#e05555' },
    pull: { main: '#5588e0', bar_pos: 'rgba(85, 136, 224, 0.5)', bar_neg: 'rgba(224, 140, 85, 0.5)', line: '#5588e0' },
    legs: { main: '#e0a855', bar_pos: 'rgba(224, 168, 85, 0.5)', bar_neg: 'rgba(85, 160, 224, 0.5)', line: '#e0a855' },
    core: { main: '#a855e0', bar_pos: 'rgba(168, 85, 224, 0.5)', bar_neg: 'rgba(140, 224, 85, 0.5)', line: '#a855e0' },
}

function onGeneralProgressDataLoaded(payload) {
    Object.entries(payload).forEach(([categoryName, data]) => {
        const canvasId = categoryCanvasMap[categoryName]
        const canvas = document.getElementById(canvasId)
        if (!canvas) return

        const months = Object.keys(data.monthly_progress)
        const monthlyValues = Object.values(data.monthly_progress)
        const accumulatedValues = Object.values(data.accumulated_monthly_progress)

        if (categoryCharts[categoryName]) categoryCharts[categoryName].destroy()

        const colors = CATEGORY_COLORS[categoryName]
        const ctx = canvas.getContext('2d')

        categoryCharts[categoryName] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    {
                        type: 'line',
                        label: 'Accumulated (%)',
                        data: accumulatedValues,
                        borderColor: colors.main,
                        backgroundColor: colors.main + '18',
                        borderWidth: 1.5,
                        tension: 0.45,
                        pointRadius: 0,
                        pointHoverRadius: 3,
                        pointBackgroundColor: colors.main,
                        fill: true,
                        yAxisID: 'y',
                        order: 1,
                    },
                    {
                        type: 'bar',
                        label: 'Monthly (%)',
                        data: monthlyValues,
                        backgroundColor: monthlyValues.map(v =>
                            v >= 0 ? colors.bar_pos : colors.bar_neg
                        ),
                        borderColor: 'transparent',
                        borderWidth: 0,
                        borderRadius: 2,
                        borderSkipped: false,
                        barThickness: 'flex',
                        maxBarThickness: 16,
                        yAxisID: 'y',
                        order: 2,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                layout: { padding: { top: 4, right: 4, bottom: 0, left: 0 } },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            color: '#5a5a5a',
                            font: { size: 9, family: 'Poppins' },
                            boxWidth: 6,
                            boxHeight: 6,
                            usePointStyle: true,
                            pointStyleWidth: 6,
                            padding: 10,
                        }
                    },
                    tooltip: {
                        backgroundColor: '#141414',
                        titleColor: '#7a7a7a',
                        bodyColor: '#bbbbbb',
                        borderColor: '#292929',
                        borderWidth: 1,
                        padding: 8,
                        cornerRadius: 3,
                        boxPadding: 4,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(2) + '%';
                                }
                                return label;
                            }
                        }
                        // callbacks: {
                        //     label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}%`
                        // }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        border: { display: false },
                        ticks: {
                            color: '#444444',
                            font: { size: 9, family: 'Poppins' },
                            maxRotation: 0,
                            padding: 4,
                        }
                    },
                    y: {
                        position: 'left',
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        border: { display: false, dash: [3, 3] },
                        ticks: {
                            color: '#444444',
                            font: { size: 9, family: 'Poppins' },
                            padding: 6,
                            callback: v => v + '%'
                        }
                    }
                }
            }
        })
    })
}