// Registration.js

import {useState} from "react";

export default function Form() {
    
    //Pulling from input boxes
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    // Check for errors 
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState(false);

    // Name Change
    const handleName = (e) => {
        setName(e.target.value);
        setSubmitted(false);
    }

    // Email Change
    const handleEmail = (e) => {
        setEmail(e.target.value);
        setSubmitted(false);
    }

    // Password Change
    const handlePassword (e) => {
        setPassword(e.target.value);
        setSubmitted(false);
    }

    // Form submission
    const handleSubmit = (e) => {
        e.preventDefault();
        if (name === "" || email === "" || password === "") {
            setError(true);
        } else {
            setSubmitted(true);
            setError(false);
        }
    };

    // success message
    const sucessMessage = () => {
        return (
            <div
                className = "success"
                style= {{
                    display: submitted ? = "" : "none",
                }}
            >
                <h1>User {name} successfully registered!!</h1>
            </div>
        );
    };

    // error message
    const errorMessage = () => {
        return (
            <div
                className="error"
                style={{
                    display: error ? "" : "none",
                }}
            >
                <h1>Please enter all the fields</h1>
                </div>
        );
    };

}

