document.getElementById("register-form").addEventListener("submit", async (e) => {

    e.preventDefault();

    const full_name = document.getElementById("full_name").value;
    const company = document.getElementById("company").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {

        await APIClient.post("/auth/register",{

            full_name,
            company,
            email,
            password

        });

        alert("Recruiter account created successfully!");

        window.location.href="login.html";

    }

    catch(err){

        alert(err.message);

    }

});
