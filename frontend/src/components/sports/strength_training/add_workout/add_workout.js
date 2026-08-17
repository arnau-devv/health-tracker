// ============================================================================
//                                   ADD WORKOUT (Subview) 
// ============================================================================

// ======= SAVED EXERCISES SELECTOR
document.querySelectorAll('.exercises_list_tittle').forEach(header => {
    header.addEventListener('click', () => {
        const list = header.closest('.exercises_list')
        if (!list) return

        const wasOpen = list.classList.contains('open')

        document.querySelectorAll('.exercises_list').forEach(item => {
            item.classList.remove('open')
        })

        if (!wasOpen) {
            list.classList.add('open')
        }
    })
})

document.querySelectorAll('.exercises_list_items').forEach(container => {
    container.addEventListener('click', (e) => {
        const button = e.target.closest('.exercise_list_item')
        if (button) button.classList.toggle('open')
    })
})

const MUSCLE_LABELS = {
    chest: 'Chest',
    anterior_shoulder: 'Anterior deltoid',
    lateral_shoulder: 'Lateral deltoid',
    triceps: 'Triceps',
    forearm_extensors: 'Forearm extensors',
    lats: 'Lats',
    upper_back: 'Upper back',
    rear_deltoid: 'Rear deltoid',
    biceps: 'Biceps',
    forearm_flexors: 'Forearm flexors',
    quadriceps: 'Quadriceps',
    hamstrings: 'Hamstrings',
    glutes: 'Glutes',
    calves: 'Calves',
    adductors: 'Adductors',
    rectus_abdominis: 'Rectus abdominis',
    obliques: 'Obliques',
    lower_back: 'Lower back',
}


// ============================================================================================
//                                      WORKOUT DATE
// ============================================================================================
const workoutDatePicker = initDatePicker('#workout_date_input', {
    inline: true,      // calendar always visible, not a popup
    maxDate: 'today',  // can't log a workout in the future
});


// ============================================================================================
//                                      WORKOUT SATISFACTION
// ============================================================================================
const workoutSatisfactionButtons = document.querySelectorAll('.workout_satisfaction_btn')
workoutSatisfactionButtons.forEach(Btn => {
    Btn.addEventListener('click', () => {
        workoutSatisfactionButtons.forEach(b => b.classList.remove('selected'));
        Btn.classList.add('selected')
    })
} )

const workoutIntensityButtons = document.querySelectorAll('.workout_intensity_btn')
workoutIntensityButtons.forEach(Btn => {
    Btn.addEventListener('click', () => {
        workoutIntensityButtons.forEach(b => b.classList.remove('selected'));
        Btn.classList.add('selected')
    })
} )




// ============================================================================================
//                                      ON SAVED EXERCICE - post backend
// ============================================================================================
const CATEGORY_CONTAINER_SELECTOR = {
    push: '.push_exercises_list_items',
    pull: '.pull_exercises_list_items',
    legs: '.legs_exercises_list_items',
    core: '.core_exercises_list_items',
}

function onExerciseSaved(payload) {
    const { name, category, muscles } = payload
    showValidToast("Exercise saved correctly.")
    addExerciseToList(name, category, muscles)
    addSavedExerciseToCreator(name, category) // <- nuevo

}

function addExerciseToList(name, category, muscles) {
    const container = document.querySelector(CATEGORY_CONTAINER_SELECTOR[category])
    if (!container) {
        console.warn(`Categoría desconocida: ${category}`)
        return
    }

    const button = document.createElement('button')
    button.className = 'exercise_list_item'
    button.id = `${slugify(name)}_exercise_item`
    button.draggable = true // <- nuevo
    button.dataset.exerciseName = name // <- nuevo, para leerlo al soltar

    button.innerHTML = `
        <span class="exercise_item_name">${name}</span>
        <div class="exercise_item_muscles">
            ${buildMusclesList(muscles)}
        </div>
    `

    container.appendChild(button)
    updateCategoryCount(container)
}

function buildMusclesList(muscles) {
    return Object.entries(muscles)
        .filter(([, intensity]) => intensity > 0)
        .sort(([, a], [, b]) => b - a) // de mayor a menor implicación
        .map(([muscle, intensity]) => `
            <div class="exercise_item_muscle">
                <span class="exercise_item_muscle_name">${MUSCLE_LABELS[muscle] || muscle}</span>
                <span class="exercise_item_muscle_value">${Math.round(intensity * 100)}%</span>
            </div>
        `).join('')
}

function slugify(text) {
    return text.trim().toLowerCase().replace(/\s+/g, '_')
}

function updateCategoryCount(container) {
    const list = container.closest('.exercises_list')
    if (!list) return

    const countSpan = list.querySelector('.exercises_list_tittle .muscles_selected')
    if (countSpan) countSpan.textContent = container.children.length
}



// ============================================================================================
//                                      DRAG & DROP - EXERCISE SELECTION
// ============================================================================================
const savedExercisesList = document.querySelector('.saved_exercises_list')
const selectedExercisesManager = document.querySelector('.selected_exercices_manager')

// --- Origen: cualquier .exercise_list_item ---
savedExercisesList.addEventListener('dragstart', (e) => {
    const item = e.target.closest('.exercise_list_item')
    if (!item) return

    e.dataTransfer.setData('text/plain', item.dataset.exerciseName)
    e.dataTransfer.effectAllowed = 'copy'

    item.classList.add('is-dragging')
})

savedExercisesList.addEventListener('dragend', (e) => {
    const item = e.target.closest('.exercise_list_item')
    if (item) item.classList.remove('is-dragging')
})


// --- Destino: selected_exercices_manager ---
selectedExercisesManager.addEventListener('dragover', (e) => {
    e.preventDefault() // obligatorio para que 'drop' se dispare
    e.dataTransfer.dropEffect = 'copy'
})

selectedExercisesManager.addEventListener('drop', (e) => {
    e.preventDefault()

    const name = e.dataTransfer.getData('text/plain')
    if (!name) return

    const item = createSelectedExerciseItem(name)
    selectedExercisesManager.appendChild(item)
})

function createSelectedExerciseItem(name) {
    const item = document.createElement('div')
    item.className = 'selected_exercise_item'

    item.innerHTML = `
        <h3 class="selected_exercise_item_tittle">
            ${name}
            <div class="sets_counter">
                <span class="sets_counter_label">Sets</span>
                <button class="sets_counter_btn sets_counter_decrease" type="button">−</button>
                <span class="sets_counter_value">0</span>
                <button class="sets_counter_btn sets_counter_increase" type="button">+</button>
            </div>
        </h3>
        <div class="selected_exercise_item_details">
            <!-- SET DETAILS - generated dinamically via js -->
        </div>
    `

    return item
}
// ===================================================================================================
//                                          SELECTED EXERCICES
// ====================================================================================================
// ======= Exercice opener
selectedExercisesManager.addEventListener('click', (e) => {
    if (e.target.closest('.sets_counter')) return

    const header = e.target.closest('.selected_exercise_item_tittle')
    if (!header) return

    const selectedExercise = header.closest('.selected_exercise_item')
    if (!selectedExercise) return

    const details = selectedExercise.querySelector('.selected_exercise_item_details')
    if (details && details.children.length > 0) selectedExercise.classList.toggle('open')
})

// ======= Sets counter (+ / -) → genera/elimina filas de series
selectedExercisesManager.addEventListener('click', (e) => {
    const btn = e.target.closest('.sets_counter_btn')
    if (!btn) return

    const item = btn.closest('.selected_exercise_item')
    const valueSpan = item.querySelector('.sets_counter_value')
    const detailsContainer = item.querySelector('.selected_exercise_item_details')
    let value = parseInt(valueSpan.textContent, 10) || 0

    if (value === 1) item.classList.remove('open')

    if (btn.classList.contains('sets_counter_increase') && value < 20) {
        value++
        detailsContainer.appendChild(createSetRow(value))
    }

    if (btn.classList.contains('sets_counter_decrease') && value > 0) {
        value--
        detailsContainer.lastElementChild?.remove() // elimina la última fila
    }

    valueSpan.textContent = value
})

// ======= Inputs y controles dentro de cada set_row → guardan en row.setData
selectedExercisesManager.addEventListener('click', (e) => {
    const btn = e.target.closest('.set_field_btn')
    if (btn) {
        const row = btn.closest('.set_row')
        const input = btn.parentElement.querySelector('.set_field_input')
        let value = parseFloat(input.value) || 0

        if (btn.classList.contains('set_field_increase')) value++
        if (btn.classList.contains('set_field_decrease')) value = Math.max(0, value - 1)

        input.value = value
        updateRowData(row)
    }
})

selectedExercisesManager.addEventListener('input', (e) => {
    const row = e.target.closest('.set_row')
    if (row) updateRowData(row)
})

selectedExercisesManager.addEventListener('change', (e) => {
    const row = e.target.closest('.set_row')
    if (row) updateRowData(row)
})

function updateRowData(row) {
    row.setData = {
        weight: parseFloat(row.querySelector('.weight_input').value) || 0,
        reps: parseInt(row.querySelector('.reps_input').value, 10) || 0,
        rpe: row.querySelector('.rpe_checkbox_input').checked,
        type: row.querySelector('.set_type_select').value,
    }
}


function createSetRow(index) {
    const row = document.createElement('div')
    row.className = 'set_row'

    row.innerHTML = `
        <span class="set_row_index">${index}</span>

        <div class="set_field weight_field">
            <span class="set_field_label">KG</span>
            <button class="set_field_btn set_field_decrease" type="button">−</button>
            <input class="set_field_input weight_input" type="text" inputmode="decimal" value="0">
            <button class="set_field_btn set_field_increase" type="button">+</button>
        </div>

        <div class="set_field reps_field">
            <span class="set_field_label">REPS</span>
            <button class="set_field_btn set_field_decrease" type="button">−</button>
            <input class="set_field_input reps_input" type="text" inputmode="numeric" value="0">
            <button class="set_field_btn set_field_increase" type="button">+</button>
        </div>

        <label class="set_rpe_checkbox">
            <input type="checkbox" class="rpe_checkbox_input">
            <span class="rpe_checkbox_box"></span>
            <span class="rpe_checkbox_label">RPE</span>
        </label>

        <select class="set_type_select">
            <option value="warmup">W</option>
            <option value="working" selected>WS</option>
            <option value="dropset">DS</option>
            <option value="failure">F</option>
        </select>
    `

    // Guardamos los datos de esta serie directamente en el elemento
    row.setData = { weight: 0, reps: 0, rpe: false, type: 'working' }

    return row
}