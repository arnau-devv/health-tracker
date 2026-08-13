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
});


// ---------------- Toggle: Routine Creator ----------------
routineCreationViewBtn.addEventListener('click', () => {
    console.log('Sub-module selected: Routine Creator');
    if (exerciseCreatorView.classList.contains('active')) closeInstantly(exerciseCreatorView);
    routineCreatorView.classList.toggle('active');
});


// ============================================================================================
//                          STRENGTH TRAINING — INTERNAL VIEWS
// ============================================================================================

const strengthTrainingMainViewBtn = document.getElementById('strength_training_main_view_btn');
const strengthTrainingAddWorkoutBtn = document.getElementById('strength_training_add_workout_view_btn');

const strengthTrainingMainView = document.getElementById('strength_training_main_subview');
const strengthTrainingAddWorkoutView = document.getElementById('strength_training_add_workout_subview');

const mainTitle = document.querySelector('.strength_training_main_tittle');
function changeTitleAnimated(newText, directionClass) {
    if (mainTitle.textContent === newText) return;

    mainTitle.classList.add(directionClass);

    setTimeout(() => {
        mainTitle.textContent = newText;
        mainTitle.classList.remove(directionClass);
    }, 300); 
}

// --- EVENTOS ---

strengthTrainingMainViewBtn.addEventListener('click', () => {
    strengthTrainingAddWorkoutBtn.classList.remove('selected');
    strengthTrainingMainViewBtn.classList.add('selected');

    strengthTrainingMainView.style.transform = 'translateX(0%)';
    strengthTrainingAddWorkoutView.style.transform = 'translateX(0%)';

    changeTitleAnimated('Strength Training', 'slide-right');
});

strengthTrainingAddWorkoutBtn.addEventListener('click', () => {
    strengthTrainingAddWorkoutBtn.classList.add('selected');
    strengthTrainingMainViewBtn.classList.remove('selected');

    strengthTrainingMainView.style.transform = 'translateX(-100%)';
    strengthTrainingAddWorkoutView.style.transform = 'translateX(-100%)';

    changeTitleAnimated('New Workout', 'slide-left');
});