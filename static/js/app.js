document.addEventListener("DOMContentLoaded", function () {
    const flashEl = document.getElementById("flash-data");
    if (flashEl && typeof Swal !== "undefined") {
        JSON.parse(flashEl.textContent).forEach(function ([category, message]) {
            Swal.fire({
                toast: true,
                position: "top-end",
                icon: category === "success" ? "success" : "error",
                title: message,
                showConfirmButton: false,
                timer: 3000,
                timerProgressBar: true,
            });
        });
    }

    document.querySelectorAll("form.confirm-delete").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            Swal.fire({
                title: "Jeste li sigurni?",
                text: form.dataset.message || "Ova se akcija ne može poništiti.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d96d95",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Da.",
                cancelButtonText: "Odustani.",
            }).then(function (result) {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    });
});
