// ============================================================================================
//                          SAVE EXERCISE (declared first, used later in this file)
// ============================================================================================
const saveExerciseBtn = document.getElementById('save_exercise_btn');
const nameInput = document.getElementById('exercise_name_input');

function updateSaveButtonState() {
    const hasName = nameInput.value.trim() !== '';
    const hasMuscles = Array.from(document.querySelectorAll('.muscle_selector_button'))
        .some(btn => Number(btn.dataset.involvement) > 0);

    saveExerciseBtn.disabled = !(hasName && hasMuscles);
}


// ============================================================================
//                          EXERCISE CREATOR (Window Helper View)
// ============================================================================
// ================= MUSCLE SELECTOR
document.querySelectorAll('.muscle_selector_button').forEach(btn => {
    btn.addEventListener('click', () => { btn.classList.toggle('open') })
})

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
//                          SAVE EXERCISE — event listeners
// ============================================================================================
nameInput.addEventListener('input', updateSaveButtonState);
updateSaveButtonState(); // initial state

saveExerciseBtn.addEventListener('click', () => {
    const name = nameInput.value.trim();

    const muscles = {};
    document.querySelectorAll('.muscle_selector_button').forEach(btn => {
        const involvement = Number(btn.dataset.involvement) || 0;
        if (involvement > 0) {
            const muscleKey = btn.id.replace('_muscle_btn', '');
            muscles[muscleKey] = Number((involvement / 100).toFixed(2));
        }
    });

    const exerciseData = { name, muscles };
    console.log('Exercise to save:', exerciseData);
    sendToBackend('save_exercise', exerciseData);
});