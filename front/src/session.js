async function validateSession() {
  const token = document.cookie
    .split("; ")
    .find((row) => row.startsWith("session_token="))
    ?.split("=")[1];

  if (!token) return;

  try {
    const response = await fetch("/api/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: token }),
    });

    if (response.ok) {
      const userData = await response.json();

      const authButton = document.getElementById("auth-button");
      authButton.outerHTML = `<span class="user-display">${userData.username}</span>`;
    }
  } catch (error) {
    console.error("Session validation failed", error);
  }
}

window.onload = validateSession;
