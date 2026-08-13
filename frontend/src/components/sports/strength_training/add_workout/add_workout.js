// ============================================================================
//                                   ADD WORKOUT (Subview) 
// ============================================================================
document.querySelectorAll('.exercises_list_tittle').forEach(header => {
    header.addEventListener('click', () => {
        const list = header.closest('.exercises_list')
        if (list) list.classList.toggle('open')
    })
})