// theme.js

document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.getElementById("toggle-dark-mode");
    const currentTheme = localStorage.getItem("theme") || "light";

    // Áp dụng chế độ hiện tại
    if (currentTheme === "dark") {
        document.body.classList.add("dark-mode");
        toggleButton.textContent = "Chế Độ Sáng";
    } else {
        toggleButton.textContent = "Chế Độ Tối";
    }

    // Xử lý sự kiện khi nhấn nút chuyển đổi
    toggleButton.addEventListener("click", function() {
        document.body.classList.toggle("dark-mode");
        let theme = "light";
        if (document.body.classList.contains("dark-mode")) {
            theme = "dark";
            toggleButton.textContent = "Chế Độ Sáng";
        } else {
            toggleButton.textContent = "Chế Độ Tối";
        }
        localStorage.setItem("theme", theme);
    });
});
