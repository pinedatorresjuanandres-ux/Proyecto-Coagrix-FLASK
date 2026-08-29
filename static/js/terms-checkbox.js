function toggleSubmitButton(checkbox, buttonId) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    button.disabled = !checkbox.checked;
}