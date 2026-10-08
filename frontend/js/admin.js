const API_BASE_URL = "http://127.0.0.1:8000";


// =========================
// LOAD ADMIN STATISTICS
// =========================

async function loadAdminStats() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/tickets/admin/stats`
            );

        if (!response.ok) {
            throw new Error(
                "Could not load admin statistics"
            );
        }

        const stats =
            await response.json();

        const cards =
            document.querySelectorAll(
                ".feature-card"
            );

        if (cards.length >= 3) {

            // Total Tickets
            cards[0]
                .querySelector("h2")
                .textContent =
                stats.total_tickets;

            // Pending Tickets
            cards[1]
                .querySelector("h2")
                .textContent =
                stats.pending_tickets;

            // Total Documents
            cards[2]
                .querySelector("h2")
                .textContent =
                stats.total_documents;
        }

    } catch (error) {

        console.error(
            "Could not load admin statistics:",
            error
        );
    }
}


// =========================
// LOAD ADMIN TICKETS
// =========================

async function loadAdminTickets() {

    const ticketList =
        document.getElementById(
            "adminTicketList"
        );

    ticketList.innerHTML =
        `<p class="empty-state">
            Loading tickets...
        </p>`;

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/tickets/admin/all`
            );

        if (!response.ok) {
            throw new Error(
                "Could not load tickets"
            );
        }

        const tickets =
            await response.json();

        if (!tickets.length) {

            ticketList.innerHTML =
                `<p class="empty-state">
                    No tickets found.
                </p>`;

            return;
        }

        ticketList.innerHTML = "";

        tickets.forEach(ticket => {

            const ticketDiv =
                document.createElement("div");

            ticketDiv.className =
                "ticket-item";

            ticketDiv.innerHTML = `

                <h3>
                    #${ticket.id}
                    ${escapeHtml(ticket.subject)}
                </h3>

                <p>
                    ${escapeHtml(ticket.description)}
                </p>

                <div class="ticket-meta">

                    <span class="ticket-badge">
                        ${escapeHtml(
                            ticket.category ||
                            "General Support"
                        )}
                    </span>

                    <span class="ticket-badge status-badge">
                        ${escapeHtml(ticket.status)}
                    </span>

                </div>

                <div style="margin-top: 15px;">

                    <label>
                        Update Status
                    </label>

                    <select
                        onchange="updateTicketStatus(
                            ${ticket.id},
                            this.value
                        )"
                        style="
                            padding: 10px;
                            margin-left: 10px;
                            border: 1px solid #d1d5db;
                            border-radius: 8px;
                        "
                    >

                        <option value="">
                            Select status
                        </option>

                        <option value="Pending">
                            Pending
                        </option>

                        <option value="In Progress">
                            In Progress
                        </option>

                        <option value="Resolved">
                            Resolved
                        </option>

                        <option value="Closed">
                            Closed
                        </option>

                    </select>

                </div>
            `;

            ticketList.appendChild(
                ticketDiv
            );

        });

    } catch (error) {

        ticketList.innerHTML =
            `<p class="empty-state">
                Could not connect to the backend.
                Make sure FastAPI is running.
            </p>`;

        console.error(error);
    }
}


// =========================
// UPDATE TICKET STATUS
// =========================

async function updateTicketStatus(
    ticketId,
    status
) {

    if (!status) {
        return;
    }

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/tickets/admin/${ticketId}/status?status=${encodeURIComponent(status)}`,
                {
                    method: "PUT"
                }
            );

        if (!response.ok) {
            throw new Error(
                "Could not update ticket status"
            );
        }

        alert(
            `Ticket #${ticketId} updated to ${status}`
        );

        loadAdminTickets();

        loadAdminStats();

    } catch (error) {

        alert(
            "Could not update ticket status."
        );

        console.error(error);
    }
}


// =========================
// UPLOAD DOCUMENT
// =========================

async function uploadDocument() {

    const title =
        document
            .getElementById("documentTitle")
            .value
            .trim();

    const fileInput =
        document.getElementById(
            "documentFile"
        );

    const message =
        document.getElementById(
            "documentMessage"
        );


    if (!title) {

        message.textContent =
            "Please enter a document title.";

        message.style.color =
            "#dc2626";

        return;
    }


    if (!fileInput.files.length) {

        message.textContent =
            "Please select a PDF file.";

        message.style.color =
            "#dc2626";

        return;
    }


    const file =
        fileInput.files[0];


    if (
        file.type !== "application/pdf" &&
        !file.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        message.textContent =
            "Only PDF files are supported.";

        message.style.color =
            "#dc2626";

        return;
    }


    message.textContent =
        "Uploading and processing document...";

    message.style.color =
        "#2563eb";


    const formData =
        new FormData();

    formData.append(
        "title",
        title
    );

    formData.append(
        "file",
        file
    );


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/documents/upload`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {
            throw new Error(
                "Document upload failed"
            );
        }


        const data =
            await response.json();


        message.textContent =
            `Document uploaded successfully. ${data.chunks_created} knowledge chunks created.`;

        message.style.color =
            "#16a34a";


        document.getElementById(
            "documentTitle"
        ).value = "";


        fileInput.value = "";


        // Update document count
        loadAdminStats();


    } catch (error) {

        message.textContent =
            "Could not upload the document. Please make sure the backend server is running.";

        message.style.color =
            "#dc2626";

        console.error(error);
    }
}


// =========================
// SECURITY HELPER
// =========================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;
}


// =========================
// PAGE INITIALIZATION
// =========================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadAdminTickets();

        loadAdminStats();

    }
);