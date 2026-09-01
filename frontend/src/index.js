// ============================================================================================
//                                      WEBSOCKET CONNECTION
// - Message format:
// { "type": "type", "payload": { ... } }
// ============================================================================================

let socket;
let messageQueue = [];


function connectSocket() {
    console.log('Intentando conectar al backend Python...');
    socket = new WebSocket('ws://localhost:8765');

    socket.addEventListener('open', () => {
        console.log('¡Conectado al backend Python!');
        messageQueue.forEach(msg => socket.send(msg));
        messageQueue = [];
    });

    socket.addEventListener('error', (err) => {
        console.error('Error de WebSocket:', err);
    });

    socket.addEventListener('close', () => {
        console.log('Conexión cerrada. Reintentando en 2 segundos...');
        // Vuelve a llamar a la función tras 2 segundos de forma indefinida
        setTimeout(connectSocket, 2000);
    });

    socket.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        console.log('Mensaje del backend:', data);

        // Websocket routing
        // ----- EXERCISE
        if (data.type === 'exercise_saved')    onExerciseSaved(data.payload)
        if (data.type === 'invalid_exercise')  showErrorToast(data.payload.errors)
        // ----- WORKOUT
        if (data.type === 'workout_saved')     onWorkoutSaved()
        if(data.type === 'invalid_workout')    showErrorToast(data.payload.errors)
            
        // ----- WORKOUT
        if (data.type === 'strength_training_data_loaded')  onStrengthTrainingDataLoaded(data.payload)
        if (data.type === 'heatmap_data_loaded')            loadHeatMapCalendar(data.payload)
        
        // ----- OVERVIEW
        if (data.type === 'general_progress_data_loaded')   onGeneralProgressDataLoaded(data.payload)
        // if (data.type === 'exercises_loaded')  onExerciseLoaded(data.payload)
    });
}

connectSocket();

// -- OLD
// function sendToBackend(type, payload) {
//     if (socket.readyState === WebSocket.OPEN) {
//         socket.send(JSON.stringify({ type, payload }));
//     }
// }
function sendToBackend(type, payload) {
    const message = JSON.stringify({ type, payload });
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(message);
    } else {
        messageQueue.push(message);
    }
}

// ============================================================================================
//                                      SIDEBAR
// ============================================================================================
// Window buttons
const closeAppBtn = document.getElementById('close_app_btn')
const minimizeMainWindow = document.getElementById('minimize_window_btn') 
const ajustMainWindow = document.getElementById('ajust_window_btn')

closeAppBtn.addEventListener('click', () => {
    window.electronAPI.closeApp();
    console.log("Close request sent");
})

minimizeMainWindow.addEventListener('click', () => {
    window.electronAPI.minimizeApp();
    console.log("Minimize request sent");
})

ajustMainWindow.addEventListener('click', () => {
    window.electronAPI.ajustApp();
    console.log("Adjust window request sent");
})

// Sidebar module selection 
document.querySelectorAll('.sidebar_module').forEach(btn => {
    btn.addEventListener('click', function(e) {
        if (e.target.closest('.sport-module')) {
            // Ignore clicks that come from child .sport-module buttons,
            // otherwise the click bubbles up and toggles this parent off
            return;
        }

        const moduleId = this.id;
        const isAlreadyActive = this.classList.contains('active');
        
        if (moduleId !== 'sports_module_btn') desactivateViews();
        document.querySelectorAll('.sidebar_module').forEach(b => b.classList.remove('active'));
        
        if (!isAlreadyActive) this.classList.add('active');
        
        console.log('Module selected:', moduleId);
    });
});


// ------------------------ SPORT MODULES - OPENING --------------------------
const strengthTrainingView = document.getElementById('strength_training_view')
const sports = document.querySelectorAll('.sport-module');

sports.forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.stopPropagation();

        // 1. Si el botón ya está activo, no hacemos nada y salimos
        if (this.classList.contains('active')) {
            return;
        }

        // 2. Si no estaba activo, desactivamos el resto y cambiamos de vista
        sports.forEach(b => b.classList.remove('active'));
        desactivateViews();

        this.classList.add('active');
        const sportId = this.id;

        if (sportId === 'strength-training-module-btn') {
            strengthTrainingView.classList.add('active');
            sendToBackend("get_strength_training_data", {});
            sendToBackend("get_heatmap_data", { year: String(currentYear) });
            sendToBackend("get_general_progress_data", {})
        }


        console.log('Sport selected:', sportId);
    });
});

// get all views (const) and deactivate them
function desactivateViews() {
    strengthTrainingView.classList.remove('active')
}


// ============================================================================================
//                                      TOASTS POP UP MANAGER
// ============================================================================================
function adaptToastPopupToHelperViews() {
    const isAnyViewOpen = exerciseCreatorView?.classList.contains('active') || 
                        routineCreatorView?.classList.contains('active');
    toastPopup.classList.toggle('helper_view_opened', isAnyViewOpen);
}

// ==================== ERROR
const toastPopup = document.getElementById('toast_popup')
let toastTimer = null

function showErrorToast(errors) {
    // Clear any running timer before starting a new one
    clearTimeout(toastTimer)

    // Render errors as individual lines
    toastPopup.innerHTML = errors.map(err => `<p>·&nbsp; ${err}</p>`).join('')

    // Force reflow if already visible so the animation re-triggers
    toastPopup.classList.remove('error', 'valid')
    void toastPopup.offsetHeight

    toastPopup.classList.add('error')

    toastTimer = setTimeout(() => {
        toastPopup.classList.remove('error')
    }, 3000)
}


// ==================== OKAY / VALID / SUSCCESS
function showValidToast(message) {
     // Clear any running timer before starting a new one
    clearTimeout(toastTimer)

    // Render errors as individual lines
    toastPopup.textContent = "· " + message

    // Force reflow if already visible so the animation re-triggers
    toastPopup.classList.remove('valid', 'error')
    void toastPopup.offsetHeight

    toastPopup.classList.add('valid')

    toastTimer = setTimeout(() => {
        toastPopup.classList.remove('valid')
    }, 3000)
}

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

function onGeneralProgressDataLoaded(payload) {
    Object.entries(payload).forEach(([categoryName, data]) => {
        const canvasId = categoryCanvasMap[categoryName];
        const canvas = document.getElementById(canvasId);

        if (!canvas) return;

        const months = Object.keys(data.monthly_progress);
        const monthlyValues = Object.values(data.monthly_progress);
        const accumulatedValues = Object.values(data.accumulated_monthly_progress);

        // Destruir chart anterior
        if (categoryCharts[categoryName]) {
            categoryCharts[categoryName].destroy();
        }

        // Crear chart
        const ctx = canvas.getContext('2d');
        categoryCharts[categoryName] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    {
                        type: 'line',
                        label: 'Progreso Acumulado (%)',
                        data: accumulatedValues,
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 4,
                        pointBackgroundColor: '#4f46e5',
                        yAxisID: 'y'
                    },
                    {
                        type: 'bar',
                        label: 'Mejora Mensual (%)',
                        data: monthlyValues,
                        backgroundColor: monthlyValues.map(v => v >= 0 ? 'rgba(34, 197, 94, 0.6)' : 'rgba(239, 68, 68, 0.6)'),
                        borderColor: monthlyValues.map(v => v >= 0 ? '#16a34a' : '#dc2626'),
                        borderWidth: 1,
                        borderRadius: 4,
                        yAxisID: 'y'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { color: '#e2e8f0' }
                    },
                    tooltip: {
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
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        ticks: {
                            color: '#94a3b8',
                            callback: value => value + '%'
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                }
            }
        });
    });
}