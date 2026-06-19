(function () {
    function formatLocalDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        return year + "-" + month + "-" + day;
    }

    function openReservationForm(dateStr) {
        const dateInput = document.getElementById("date");
        const collapseEl = document.getElementById("newReservation");
        if (dateInput) {
            dateInput.value = dateStr;
        }
        if (collapseEl && typeof bootstrap !== "undefined") {
            bootstrap.Collapse.getOrCreateInstance(collapseEl, { toggle: false }).show();
        }
        if (dateInput) {
            dateInput.focus();
            dateInput.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    }

    function showReservationDetails(props) {
        const price = Number(props.price).toFixed(2);
        Swal.fire({
            title: props.bride_name + " i " + props.groom_name,
            html:
                '<dl class="text-start mb-0 hall-calendar-details">' +
                "<dt>Datum</dt><dd>" + props.date + "</dd>" +
                "<dt>Status</dt><dd>" + props.status_label + "</dd>" +
                "<dt>Broj gostiju</dt><dd>" + props.guest_count + "</dd>" +
                "<dt>Cijena najma</dt><dd>" + price + " €</dd>" +
                "<dt>Kontakt mladenke</dt><dd>" + props.bride_contact + "</dd>" +
                "<dt>Kontakt mladoženja</dt><dd>" + props.groom_contact + "</dd>" +
                "</dl>",
            icon: "info",
            showCancelButton: true,
            confirmButtonText: "Uredi rezervaciju",
            cancelButtonText: "Zatvori",
            confirmButtonColor: "#d96d95",
        }).then(function (result) {
            if (result.isConfirmed) {
                window.location.href = props.edit_url;
            }
        });
    }

    function offerNewReservation(dateStr) {
        Swal.fire({
            title: "Novi termin",
            text: "Želite li zakazati rezervaciju za " + dateStr + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: "Nova rezervacija",
            cancelButtonText: "Odustani",
            confirmButtonColor: "#d96d95",
        }).then(function (result) {
            if (result.isConfirmed) {
                openReservationForm(dateStr);
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        const calendarEl = document.getElementById("hall-calendar");
        if (!calendarEl || typeof FullCalendar === "undefined") {
            return;
        }

        const today = calendarEl.dataset.today;
        const reservationsUrl = calendarEl.dataset.reservationsUrl;
        const blockedDates = new Set();

        function isPastDate(dateStr) {
            return dateStr < today;
        }

        function isDateDisabled(dateStr) {
            return isPastDate(dateStr) || blockedDates.has(dateStr);
        }

        fetch(reservationsUrl)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Neuspjelo učitavanje rezervacija.");
                }
                return response.json();
            })
            .then(function (data) {
                data.blocked_dates.forEach(function (dateStr) {
                    blockedDates.add(dateStr);
                });

                const calendar = new FullCalendar.Calendar(calendarEl, {
                    locale: "hr",
                    firstDay: 1,
                    initialView: "dayGridMonth",
                    headerToolbar: {
                        left: "prev,next today",
                        center: "title",
                        right: "dayGridMonth,dayGridWeek",
                    },
                    noEventsText: "Nema rezervacija za prikaz",
                    height: "auto",
                    fixedWeekCount: false,
                    events: data.events,
                    eventDisplay: "block",
                    dayMaxEvents: 3,
                    eventClick: function (info) {
                        info.jsEvent.preventDefault();
                        showReservationDetails(info.event.extendedProps);
                    },
                    dateClick: function (info) {
                        const dateStr = formatLocalDate(info.date);
                        if (isDateDisabled(dateStr)) {
                            return;
                        }
                        offerNewReservation(dateStr);
                    },
                    dayCellClassNames: function (arg) {
                        const dateStr = formatLocalDate(arg.date);
                        if (isDateDisabled(dateStr)) {
                            return ["fc-day-disabled"];
                        }
                        return ["fc-day-available"];
                    },
                });

                calendar.render();

                const totalEl = document.getElementById("hall-calendar-total");
                if (totalEl) {
                    totalEl.textContent = "Ukupno rezervacija: " + data.total;
                }
            })
            .catch(function () {
                Swal.fire({
                    icon: "error",
                    title: "Greška",
                    text: "Kalendar nije uspio učitati rezervacije.",
                });
            });
    });
})();
