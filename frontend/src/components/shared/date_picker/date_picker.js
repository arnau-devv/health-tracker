// ============================================================================================
//                                      DATE PICKER
// - Thin wrapper around Flatpickr, so the rest of the app never talks to Flatpickr directly.
// ============================================================================================
const DATE_PICKER_DEFAULTS = {
    dateFormat: 'Y-m-d',
    altInput: true,
    altFormat: 'd M Y',
    disableMobile: true,
    animate: true,
    defaultDate: 'today',
    monthSelectorType: 'static',
    nReady: (_, __, fp) => {
        // Make the year input read-only so the user can't type in it either
        const yearInput = fp.calendarContainer.querySelector('.cur-year')
        if (yearInput) yearInput.setAttribute('readonly', true)
    }
};

function initDatePicker(selector, options = {}) {
    const element = document.querySelector(selector);
    if (!element) {
        console.warn(`Date picker target not found: ${selector}`);
        return null;
    }
    return flatpickr(element, { ...DATE_PICKER_DEFAULTS, static: true, ...options });
}
