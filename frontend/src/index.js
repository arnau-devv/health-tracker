// ============================================================================================
//                                      WEBSOCKET CONNECTION
// - Message format:
// { "type": "type", "payload": { ... } }
// ============================================================================================

const socket = new WebSocket('ws://localhost:8765');

socket.addEventListener('open', () => console.log('Conectado al backend Python'));

socket.addEventListener('error', (err) => console.error('Error de WebSocket:', err));

socket.addEventListener('close', () => {
    console.log('Connection to backend closed. Retrying in 2s...');
    setTimeout(connectSocket, 2000);
});

socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    console.log('Mensaje del backend:', data);

    // Websocket routing
    if (data.type === 'exercise_saved') {
        console.log('Ejercicio guardado correctamente:', data.payload);
    }
});


function sendToBackend(type, payload) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type, payload }));
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

// Sport sub-module selection (strength training, running, etc.)
const strengthTrainingView = document.getElementById('strength_training_view')

const sports = document.querySelectorAll('.sport-module')
sports.forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.stopPropagation(); // Stop the click from bubbling up to #sports_module_btn
        sports.forEach(b => b.classList.remove('active'));
        desactivateViews();
        
        this.classList.add('active');

        const sportId = this.id;

        if (sportId === 'strength-training-module-btn') strengthTrainingView.classList.add('active')
        
        console.log('Sport selected:', sportId);
    });
});

// get all views (const) and deactivate them
function desactivateViews() {
    strengthTrainingView.classList.remove('active')
}

