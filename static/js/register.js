function checkPasswordStrength(password) {
    let strength = 0;
    let feedback = [];

    // Longitud mínima
    if (password.length >= 8) {
        strength += 25;
        feedback.push("Longitud adecuada");
    }

    // Contiene números
    if (/\d/.test(password)) {
        strength += 25;
        feedback.push("Incluye números");
    }

    // Contiene letras minúsculas y mayúsculas
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
        strength += 25;
        feedback.push("Incluye mayúsculas y minúsculas");
    }

    // Contiene caracteres especiales
    if (/[^A-Za-z0-9]/.test(password)) {
        strength += 25;
        feedback.push("Incluye caracteres especiales");
    }

    // Actualizar barra de progreso
    document.getElementById('passwordStrength').style.width = strength + '%';
    
    // Actualizar color según fortaleza
    const fill = document.getElementById('passwordStrength');
    if (strength < 50) {
        fill.style.backgroundColor = '#ef4444';
    } else if (strength < 75) {
        fill.style.backgroundColor = '#f59e0b';
    } else {
        fill.style.backgroundColor = '#10b981';
    }

    // Mostrar feedback
    const feedbackElement = document.getElementById('passwordFeedback');
    if (password.length === 0) {
        feedbackElement.textContent = "La contraseña debe tener al menos 8 caracteres";
    } else if (strength < 50) {
        feedbackElement.textContent = "Contraseña débil - Añade más variedad";
    } else if (strength < 75) {
        feedbackElement.textContent = "Contraseña media - Vas por buen camino";
    } else {
        feedbackElement.textContent = "¡Excelente contraseña!";
    }
}