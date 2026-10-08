const API_BASE_URL = "http://127.0.0.1:8000";

const accessToken =
    localStorage.getItem("access_token");


/* =========================================================
   AUTHENTICATION
========================================================= */

function requireLogin() {
    if (!accessToken) {
        window.location.href = "logic.html";
        return false;
    }

    return true;
}


function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${accessToken}`
    };
}


function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("student");

    window.location.href = "logic.html";
}


/* =========================================================
   NAVIGATION
========================================================= */

function scrollToSection(sectionId) {
    const section =
        document.getElementById(sectionId);

    if (section) {
        section.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}


function setupNavigation() {
    const navLinks =
        document.querySelectorAll("[data-section]");

    navLinks.forEach(function(link) {

        link.addEventListener("click", function(event) {

            event.preventDefault();

            const sectionId =
                link.getAttribute("data-section");

            scrollToSection(sectionId);
        });
    });
}


/* =========================================================
   PAGE INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        if (!requireLogin()) {
            return;
        }

        loadProfile();
        loadTickets();
        setupNavigation();

        setupChatInput();
    }
);


/* =========================================================
   CHAT INPUT
========================================================= */

function setupChatInput() {

    const chatInput =
        document.getElementById("chatInput");

    if (!chatInput) {
        return;
    }

    chatInput.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();
            }
        }
    );
}


/* =========================================================
   SEND CHAT MESSAGE
========================================================= */

async function sendMessage() {

    const input =
        document.getElementById("chatInput");

    const messages =
        document.getElementById("chatMessages");

    if (!input || !messages) {
        return;
    }

    const question =
        input.value.trim();

    if (!question) {
        return;
    }


    /* Add student's message */

    addChatMessage(
        messages,
        question,
        "student"
    );

    input.value = "";


    /* Add temporary loading message */

    const loadingElement =
        addChatMessage(
            messages,
            "Thinking...",
            "ai"
        );


    try {

        const response =
            await fetch(
                API_BASE_URL + "/chat/",
                {
                    method: "POST",

                    headers: authHeaders(),

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        /* Authentication expired */

        if (response.status === 401) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to get an answer."
            );
        }


        /* Replace Thinking... */

        loadingElement.textContent =
            data.answer;


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );

        loadingElement.textContent =
            "Sorry, I couldn't process your question right now.";
    }
}


/* =========================================================
   CHAT MESSAGE UI
========================================================= */

function addChatMessage(
    container,
    text,
    type
) {

    const message =
        document.createElement("div");

    message.className =
        "chat-message " + type;


    const avatar =
        document.createElement("div");

    avatar.className =
        "chat-avatar";


    if (type === "student") {

        avatar.textContent =
            "You";

    } else {

        avatar.textContent =
            "AI";
    }


    const bubble =
        document.createElement("div");

    bubble.className =
        "chat-bubble";

    bubble.textContent =
        text;


    message.appendChild(
        avatar
    );

    message.appendChild(
        bubble
    );

    container.appendChild(
        message
    );


    container.scrollTop =
        container.scrollHeight;


    return bubble;
}


/* =========================================================
   CREATE SUPPORT TICKET
========================================================= */

async function createTicket() {

    const subjectInput =
        document.getElementById(
            "ticketSubject"
        );

    const descriptionInput =
        document.getElementById(
            "ticketDescription"
        );

    const message =
        document.getElementById(
            "ticketMessage"
        );


    if (
        !subjectInput ||
        !descriptionInput
    ) {
        return;
    }


    const subject =
        subjectInput.value.trim();

    const description =
        descriptionInput.value.trim();


    if (
        !subject ||
        !description
    ) {

        showTicketMessage(
            message,
            "Please enter both a subject and description.",
            "error"
        );

        return;
    }


    try {

        const response =
            await fetch(
                API_BASE_URL + "/tickets/",
                {
                    method: "POST",

                    headers: authHeaders(),

                    body: JSON.stringify({
                        subject: subject,
                        description: description
                    })
                }
            );


        if (response.status === 401) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to create ticket."
            );
        }


        showTicketMessage(
            message,
            "Support request created successfully.",
            "success"
        );


        subjectInput.value = "";

        descriptionInput.value = "";


        loadTickets();


    } catch (error) {

        console.error(
            "Ticket error:",
            error
        );


        showTicketMessage(
            message,
            error.message ||
            "Unable to create support request.",
            "error"
        );
    }
}


/* =========================================================
   TICKET MESSAGE
========================================================= */

function showTicketMessage(
    element,
    text,
    type
) {

    if (!element) {
        return;
    }


    element.textContent =
        text;

    element.className =
        "ticket-message " + type;
}


/* =========================================================
   LOAD STUDENT TICKETS
========================================================= */

async function loadTickets() {

    const ticketList =
        document.getElementById(
            "ticketList"
        );


    if (!ticketList) {
        return;
    }


    try {

        const response =
            await fetch(
                API_BASE_URL + "/tickets/",
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${accessToken}`
                    }
                }
            );


        if (response.status === 401) {

            logout();

            return;
        }


        const tickets =
            await response.json();


        if (!response.ok) {

            throw new Error(
                tickets.detail ||
                "Unable to load tickets."
            );
        }


        renderTickets(
            ticketList,
            tickets
        );


    } catch (error) {

        console.error(
            "Load tickets error:",
            error
        );


        ticketList.innerHTML = `
            <div class="empty-state">
                Unable to load your support requests.
            </div>
        `;
    }
}


/* =========================================================
   RENDER TICKETS
========================================================= */

function renderTickets(
    container,
    tickets
) {

    if (
        !tickets ||
        tickets.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                You don't have any support requests yet.
            </div>
        `;

        return;
    }


    container.innerHTML =
        tickets.map(function(ticket) {

            return `
                <div class="ticket-item">

                    <div class="ticket-main">

                        <h3>
                            ${escapeHtml(
                                ticket.subject
                            )}
                        </h3>

                        <p>
                            ${escapeHtml(
                                ticket.description
                            )}
                        </p>

                    </div>


                    <div class="ticket-meta">

                        <span class="ticket-category">
                            ${escapeHtml(
                                ticket.category ||
                                "General Support"
                            )}
                        </span>

                        <span class="ticket-status">
                            ${escapeHtml(
                                ticket.status
                            )}
                        </span>

                    </div>

                </div>
            `;

        }).join("");
}


/* =========================================================
   LOAD STUDENT PROFILE
========================================================= */

async function loadProfile() {

    try {

        const response =
            await fetch(
                API_BASE_URL +
                "/student/profile",
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${accessToken}`
                    }
                }
            );


        if (response.status === 401) {

            logout();

            return;
        }


        const student =
            await response.json();


        if (!response.ok) {

            throw new Error(
                student.detail ||
                "Unable to load profile."
            );
        }


        updateProfileUI(
            student
        );


        localStorage.setItem(
            "student",
            JSON.stringify(student)
        );


    } catch (error) {

        console.error(
            "Profile error:",
            error
        );


        const storedStudent =
            localStorage.getItem(
                "student"
            );


        if (storedStudent) {

            try {

                updateProfileUI(
                    JSON.parse(
                        storedStudent
                    )
                );

            } catch (parseError) {

                console.error(
                    parseError
                );
            }
        }
    }
}


/* =========================================================
   UPDATE PROFILE UI
========================================================= */

function updateProfileUI(student) {

    const profileName =
        document.getElementById(
            "profileName"
        );

    const profileEmail =
        document.getElementById(
            "profileEmail"
        );

    const profileDepartment =
        document.getElementById(
            "profileDepartment"
        );


    if (profileName) {

        profileName.textContent =
            student.name ||
            "Student";
    }


    if (profileEmail) {

        profileEmail.textContent =
            student.email ||
            "—";
    }


    if (profileDepartment) {

        profileDepartment.textContent =
            student.department ||
            "Not specified";
    }


    const accountName =
        document.getElementById(
            "accountName"
        );


    if (accountName) {

        accountName.textContent =
            student.name ||
            "Student";
    }
}


/* =========================================================
   SECURITY / HTML ESCAPING
========================================================= */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );
}


/* =========================================================
   COMPATIBILITY FUNCTIONS
   These support the function names currently used
   by index.html.
========================================================= */

function sendChatMessage() {

    sendMessage();
}


function handleChatKey(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendMessage();
    }
}


/* =========================================================
   GLOBAL FUNCTIONS
========================================================= */

window.sendMessage =
    sendMessage;

window.sendChatMessage =
    sendChatMessage;

window.handleChatKey =
    handleChatKey;

window.createTicket =
    createTicket;

window.loadTickets =
    loadTickets;

window.loadProfile =
    loadProfile;

window.logout =
    logout;

window.scrollToSection =
    scrollToSection;