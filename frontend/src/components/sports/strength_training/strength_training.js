// ============================================================================================
//                          STRENGTH TRAINING — LATERAL HELPER VIEWS
// - Controls which lateral panel (Exercise Creator / Routine Creator) is currently open.
// ============================================================================================

const exerciseCreatorView = document.getElementById('exercise_creator_view');
const routineCreatorView = document.getElementById('routine_creator_view');

const exerciseCreationViewBtn = document.getElementById('exercise_creation_view_toggle');
const routineCreationViewBtn = document.getElementById('routine_creation_view_toggle');


// ---------------- Helpers ----------------
// Closes a lateral helper view instantly, skipping its width/margin transition,
// so switching between helpers doesn't show the old one visibly shrinking.
function closeInstantly(view) {
    view.classList.add('no_transition');
    view.classList.remove('active');
    void view.offsetWidth; // force reflow so the change applies before re-enabling transitions
    view.classList.remove('no_transition');
}


// ---------------- Toggle: Exercise Creator ----------------
exerciseCreationViewBtn.addEventListener('click', () => {
    console.log('Sub-module selected: Exercise Creator');
    if (routineCreatorView.classList.contains('active')) closeInstantly(routineCreatorView);
    exerciseCreatorView.classList.toggle('active');
    adaptToastPopupToHelperViews();
});


// ---------------- Toggle: Routine Creator ----------------
routineCreationViewBtn.addEventListener('click', () => {
    console.log('Sub-module selected: Routine Creator');
    if (exerciseCreatorView.classList.contains('active')) closeInstantly(exerciseCreatorView);
    routineCreatorView.classList.toggle('active');
    adaptToastPopupToHelperViews();
});


// ============================================================================================
//                          STRENGTH TRAINING — INTERNAL VIEWS SWITCHING
// ============================================================================================
const mainTitle = document.querySelector('.strength_training_main_tittle');

function changeTitleAnimated(newText, directionClass) {
    if (mainTitle.textContent === newText) return;

    mainTitle.classList.add(directionClass);

    setTimeout(() => {
        mainTitle.textContent = newText;
        mainTitle.classList.remove(directionClass);
    }, 300); 
}

const viewButtons = document.querySelectorAll('.strength_training_view_btn');
const subviews = document.querySelectorAll('.strength_training_content_view > div');
const saveWorkoutBtn = document.getElementById('save_workout_btn');

let currentViewIndex = 0;

viewButtons.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        if (index === currentViewIndex) return;

        // Tittle direction & changing
        const directionClass = index > currentViewIndex ? 'slide-left' : 'slide-right';
        const newTitle = btn.getAttribute('data-title') || btn.textContent;
        changeTitleAnimated(newTitle, directionClass);

        // Moove subviews based on actual index
        subviews.forEach(subview => { subview.style.transform = `translateX(-${index * 100}%)`; });

        // Update buttons visual states
        viewButtons.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        // 4. Lógica específica según la vista activa (ejemplo: mostrar botón guardar)
        // saveWorkoutBtn.classList.toggle('is_active', btn.id === 'strength_training_add_workout_view_btn');

        currentViewIndex = index;
    });
});


// ============================================================================================
//                             ON LOADED WORKOUT DATA  - backend init
// ============================================================================================
function onStrengthTrainingDataLoaded(payload) {
    // ------ EXERCISES DATA    
    //  {    
    //     'lat pulldowns': {
    //          'name': 'lat pulldowns', 
    //          'category': 'pull', 'muscles': {
    //                              'lats': 1.0, 
    //                              'upper_back': 1.0, 
    //                              'rear_deltoid': 1.0
    //                              }
    //                      }, 
    // }
    const exercises_data = Object.values(payload["exercises"] || {});
    exercises_data.forEach(exercise => {
        addExerciseToList(exercise.name, exercise.category, exercise.muscles)
        addSavedExerciseToCreator(exercise.name, exercise.category)
    })
    showValidToast("Loaded: Strength Training data")
}
