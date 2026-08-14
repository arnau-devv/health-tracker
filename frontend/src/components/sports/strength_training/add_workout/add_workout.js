// ============================================================================
//                                   ADD WORKOUT (Subview) 
// ============================================================================

// ======= SAVED EXERCISES SELECTOR
document.querySelectorAll('.exercises_list_tittle').forEach(header => {
    header.addEventListener('click', () => {
        const list = header.closest('.exercises_list')
        if (list) list.classList.toggle('open')
    })
})


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
