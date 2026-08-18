// ==============================================================================================================
//                                      EXERCISE CREATOR (Window Helper View)
// ================================================================================================================

// ======================= SAVE EXERCISE (declared first, used later in this file)
const saveExerciseBtn = document.getElementById('save_exercise_btn');
const nameInput = document.getElementById('exercise_name_input');

function updateSaveButtonState() {
    const hasName = nameInput.value.trim() !== '';
    const hasMuscles = Array.from(document.querySelectorAll('.muscle_selector_button'))
        .some(btn => Number(btn.dataset.involvement) > 0);

    saveExerciseBtn.disabled = !(hasName && hasMuscles);
}

// ================= MUSCLE SELECTOR
const titles = document.querySelectorAll('.muscles_selector_tittle');

titles.forEach(title => {
    title.addEventListener('click', () => {
        // Busca el contenedor padre .muscles_selector más cercano y le conmuta 'open'
        const parent = title.closest('.muscles_selector');
        parent.classList.toggle('open');
    });
});

document.querySelectorAll('.muscle_selector_button').forEach(btn => {
    btn.addEventListener('click', () => { btn.classList.toggle('open') })
})

// --- MUSCLE SELECTOR CONTAINER — SIZE WATCHER
const muscleSelectorContainer = document.querySelector('.muscle_selector_container')
const resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
        const height = entry.contentRect.height

        if (height > 340) muscleSelectorContainer.classList.add('is-tall')
        else muscleSelectorContainer.classList.remove('is-tall')
    }
})

resizeObserver.observe(muscleSelectorContainer)

// ================= MUSCLE INVOLVEMENT SLIDER =================
function updateGroupCount(anyBtnInGroup) {
    const group = anyBtnInGroup.closest('.muscles_selector')
    if (!group) return

    const buttons = group.querySelectorAll('.muscle_selector_button')
    let count = 0
    buttons.forEach(btn => {
        if (Number(btn.dataset.involvement) > 0) count++
    })

    const counterLabel = group.querySelector('.muscles_selected')
    if (counterLabel) counterLabel.textContent = count
}

document.querySelectorAll('.muscle_inv_track').forEach(track => {
    const fill = track.querySelector('.muscle_inv_fill')
    const handle = track.querySelector('.muscle_inv_handle')
    const parentBtn = track.closest('.muscle_selector_button')
    const valueLabel = parentBtn ? parentBtn.querySelector('.muscle_involucration_value') : null
    let dragging = false
    let wasDragging = false

    function calculatePercent(clientX) {
        const rect = track.getBoundingClientRect()
        let percent = ((clientX - rect.left) / rect.width) * 100
        percent = Math.max(0, Math.min(100, percent))
        return percent
    }

    function setValue(percent) {
        const rounded = Math.round(percent)
        fill.style.width = percent + '%'
        handle.style.left = percent + '%'
        if (parentBtn) parentBtn.dataset.involvement = rounded
        if (valueLabel) {
            valueLabel.textContent = rounded + '%'
            valueLabel.classList.toggle('is-zero', rounded === 0)
        }
        if (parentBtn) updateGroupCount(parentBtn)

        updateSaveButtonState()
    }

    setValue(0) // ahora esto es seguro: nameInput y saveExerciseBtn ya existen

    track.addEventListener('mousedown', (e) => {
        e.stopPropagation()
        e.preventDefault()
        dragging = true
        wasDragging = false
        setValue(calculatePercent(e.clientX))
    })

    document.addEventListener('mousemove', (e) => {
        if (!dragging) return
        wasDragging = true
        setValue(calculatePercent(e.clientX))
    })

    document.addEventListener('mouseup', () => {
        dragging = false
    })

    track.addEventListener('click', (e) => e.stopPropagation())

    if (parentBtn) {
        parentBtn.addEventListener('click', (e) => {
            if (wasDragging) {
                e.stopImmediatePropagation()
                e.preventDefault()
                wasDragging = false
            }
        }, true)
    }
})


// ============================================================================================
//                          SAVE EXERCISE BUTTON ACTION — event listeners
// ============================================================================================
nameInput.addEventListener('input', updateSaveButtonState);
updateSaveButtonState(); // initial state

saveExerciseBtn.addEventListener('click', () => {
    const name = nameInput.value.trim();
    const bodyweighted = document.querySelector('.bodyweighted_checkbox_input')?.checked ?? false;
    const muscles = {};
    document.querySelectorAll('.muscle_selector_button').forEach(btn => {
        const involvement = Number(btn.dataset.involvement) || 0;
        if (involvement > 0) {
            const muscleKey = btn.id.replace('_muscle_btn', '').toLowerCase();
            muscles[muscleKey] = Number((involvement / 100).toFixed(2));
        }
    });

    const exerciseData = { name, muscles, bodyweighted };
    console.log('Exercise to save:', exerciseData);
    sendToBackend('save_exercise', exerciseData);
});


// ============================================================================================
//                          SAVE EXERCISE ERROR
// ───────────── Called when the backend returns validation errors
// ============================================================================================
// function onInvalidExercise(payload) {
//     showErrorToast(payload.errors);
// }



// ============================================================================================
//                          SAVED EXERCISES LIST (Exercise Creator)
// ============================================================================================
const exerciseCreatorSavedExercises = document.querySelector('.exercise_creator_saved_exercises')

function addSavedExerciseToCreator(name, category) {
    const item = document.createElement('div')
    item.className = 'saved_exercise_item'

    item.innerHTML = `
        <div class="saved_exercise_info">
            <span class="saved_exercise_category">${category.toUpperCase()}</span>
            <span class="saved_exercise_name">${name}</span>
        </div>
        <div class="saved_exercise_actions">
            <button class="saved_exercise_action_btn saved_exercise_edit_btn" title="Editar">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M16.5 3.5L20.5 7.5L8 20H4V16L16.5 3.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            <button class="saved_exercise_action_btn saved_exercise_delete_btn" title="Eliminar">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 6H20M9 6V4H15V6M6 6L7 20H17L18 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </div>
    `

    exerciseCreatorSavedExercises.appendChild(item)
}


// ============================================================================================
//           ON SAVED EXERCISE  - RESET EXERCISE CREATOR (after successful save)
// ============================================================================================
function resetExerciseCreatorData() {
    // Nombre
    nameInput.value = ''

    // Cada botón de músculo vuelve a 0%
    document.querySelectorAll('.muscle_selector_button').forEach(btn => {
        btn.dataset.involvement = 0
        btn.classList.remove('open')

        const fill = btn.querySelector('.muscle_inv_fill')
        const handle = btn.querySelector('.muscle_inv_handle')
        const valueLabel = btn.querySelector('.muscle_involucration_value')

        if (fill) fill.style.width = '0%'
        if (handle) handle.style.left = '0%'
        if (valueLabel) {
            valueLabel.textContent = '0%'
            valueLabel.classList.add('is-zero')
        }
    })

    // Recalcula el contador "X seleccionados" de cada grupo (push/pull/legs/core)
    document.querySelectorAll('.muscles_selector').forEach(group => {
        group.classList.remove('open')
        const counterLabel = group.querySelector('.muscles_selected')
        if (counterLabel) counterLabel.textContent = 0
    })

    // El botón de guardar vuelve a desactivarse (no hay nombre ni músculos)
    updateSaveButtonState()
}