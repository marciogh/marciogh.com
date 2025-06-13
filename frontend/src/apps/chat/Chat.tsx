import { JSX, useState } from "react";
import "./chat.css";

const BACKEND = "https://fqc0a78xlj.execute-api.ap-southeast-2.amazonaws.com/test"

export default function Chat(): JSX.Element {

    const [spinner, setSpinner] = useState(false);
    const [responses, setResponses] = useState<string[]>([]);
    const [questions, setQuestions] = useState<string[]>([]);
    const [lastError, setLastError] = useState<string>("");
    const [q, setQ] = useState<string>("");


    function onFormSubmit(e) {
        e.preventDefault();
        ask()
    }

    function ask() {
        if (q.length > 0) {
            setSpinner(true);
            setLastError("")
            setQ("")
            fetch(BACKEND + "?q=" + encodeURIComponent(q))
                .then((response) => {
                    if (response.status === 429) {
                        setSpinner(false);
                        setLastError("To many questions, come back later");
                    } else {
                        response.json().then((data) => {
                            setSpinner(false);
                            setQuestions([q, ...questions])
                            setResponses([data, ...responses]);
                        })
                    }
                })
                .catch((error) => {
                    setSpinner(false);
                    setLastError(error);
                    console.log(lastError);
                });
        }
    }

    return (
        <div className="Chat">
            <div className="spinnerContainer">
            <div className={spinner? "fadeIn" : "fadeOut"}>Thinking...</div>
            </div>
            <form onSubmit={onFormSubmit}>
                <input autoFocus type="text" name="q" value={q} onChange={e => setQ(e.target.value)}/>
                <button type="submit" name="ask" onClick={ask}>Ask away -- just hit Enter</button>
                <span id="error" className={lastError.length > 0 ? "fadeIn" : "fadeOut"}>{lastError}</span>
            </form>
            <div className="responsesContainer">
                <div className="responses">{responses.map(r => (<div><span>{r}</span></div>))}</div>
            </div>
        </div>
    )
}